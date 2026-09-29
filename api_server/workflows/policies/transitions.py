# policies/transitions.py
"""
Generic transition engine.

Idea: a transition is a first-class value. You register edges between
states, attach a predicate (the "decision function") and a side-effect
list. The engine answers `decide(current, target, context)` without knowing
anything about your domain.

Three pieces:

  Transition        — one edge, with its own predicate and context shape
  TransitionRegistry— the set of edges for one entity type
  TransitionEngine  — generic decider; works with any registry

A policy class is then a thin façade: it holds a registry, exposes
`decide()` / `assert_transition()` / etc., and provides the default
predicates specific to its domain.
"""

from dataclasses import dataclass, field
from typing import (
    Any,
    Callable,
    Dict,
    FrozenSet,
    Iterable,
    List,
    Mapping,
    Optional,
    Tuple,
)


# ============================================================================
# PREDICATE & CONTEXT
# ============================================================================

# A predicate receives a context dict and returns True/False.
#
#   predicate: (context) -> bool
#
# Context is free-form. Convention: it always contains at least
#   { "current": str, "target": str }
# Callers may add whatever the predicate needs: user role, amounts,
# flags, sibling entity states, etc.
Predicate = Callable[[Mapping[str, Any]], bool]


def always(_: Mapping[str, Any]) -> bool:
    """Default predicate — edge is always allowed when reached."""
    return True

def all_of(*predicates):
    return lambda ctx: all(p(ctx) for p in predicates)

def any_of(*predicates):
    return lambda ctx: any(p(ctx) for p in predicates)

def not_(predicate):
    return lambda ctx: not predicate(ctx)

# ============================================================================
# TRANSITION
# ============================================================================

@dataclass(frozen=True)
class Transition:
    """
    One edge in a state graph.

    source        — state the entity is currently in
    target        — state the entity is moving to
    predicate     — decides whether the move is allowed given context
    side_effects  — human-readable annotations the caller may act on
    name          — optional label for diagnostics / logging
    """
    source: str
    target: str
    predicate: Predicate = always
    side_effects: Tuple[str, ...] = ()
    name: Optional[str] = None

    def matches(self, current: str, target: str) -> bool:
        return self.source == current and self.target == target

    def evaluate(self, context: Mapping[str, Any]) -> bool:
        try:
            return bool(self.predicate(context))
        except Exception:
            # A predicate that raises is treated as "denied" — never let
            # a bug in a predicate take down the caller's request.
            return False


# ============================================================================
# DECISION
# ============================================================================

@dataclass(frozen=True)
class Decision:
    """Result of asking the engine about a (current, target) move."""
    allowed: bool
    current: str
    target: str
    reason: Optional[str] = None
    side_effects: List[str] = field(default_factory=list)
    is_terminal: bool = False
    matched_transition: Optional[Transition] = None
    context: Mapping[str, Any] = field(default_factory=dict)


# ============================================================================
# REGISTRY
# ============================================================================

class TransitionRegistry:
    """
    Holds the edges for one entity type.

    The registry is built once per policy and reused — it's immutable in
    practice after construction.
    """

    def __init__(
        self,
        *,
        valid_states: Iterable[str],
        initial_state: str,
        terminal_states: Iterable[str] = (),
        normalize: Optional[Callable[[Optional[str]], str]] = None,
    ):
        self.valid_states: FrozenSet[str] = frozenset(valid_states)
        self.initial_state = initial_state
        self.terminal_states: FrozenSet[str] = frozenset(terminal_states)
        self._normalize = normalize or (lambda s: s or initial_state)

        # (source, target) -> Transition
        self._edges: Dict[Tuple[str, str], Transition] = {}
        # source -> [Transition, ...]  (for `allowed_targets`)
        self._by_source: Dict[str, List[Transition]] = {}

    # ── Normalization ────────────────────────────────────────────────

    def normalize(self, state: Optional[str]) -> str:
        return self._normalize(state)

    # ── Registration ─────────────────────────────────────────────────

    def add(self, transition: Transition) -> "TransitionRegistry":
        source = self.normalize(transition.source)
        target = self.normalize(transition.target)

        if source not in self.valid_states:
            raise ValueError(
                f"Transition source '{source}' not in valid states "
                f"{sorted(self.valid_states)}"
            )
        if target not in self.valid_states:
            raise ValueError(
                f"Transition target '{target}' not in valid states "
                f"{sorted(self.valid_states)}"
            )

        key = (source, target)
        if key in self._edges:
            raise ValueError(
                f"Duplicate transition {source} → {target}"
            )

        normalized = Transition(
            source=source,
            target=target,
            predicate=transition.predicate,
            side_effects=transition.side_effects,
            name=transition.name,
        )
        self._edges[key] = normalized
        self._by_source.setdefault(source, []).append(normalized)
        return self

    def add_many(
        self, transitions: Iterable[Transition]
    ) -> "TransitionRegistry":
        for t in transitions:
            self.add(t)
        return self

    # ── Queries ──────────────────────────────────────────────────────

    def is_valid(self, state: str) -> bool:
        return self.normalize(state) in self.valid_states

    def is_terminal(self, state: str) -> bool:
        return self.normalize(state) in self.terminal_states

    def get(
        self, current: str, target: str
    ) -> Optional[Transition]:
        return self._edges.get(
            (self.normalize(current), self.normalize(target))
        )

    def outgoing(self, current: str) -> List[Transition]:
        return list(self._by_source.get(self.normalize(current), []))

    def targets_from(self, current: str) -> FrozenSet[str]:
        return frozenset(
            t.target for t in self.outgoing(current)
        )

    def all_transitions(self) -> List[Transition]:
        return list(self._edges.values())


# ============================================================================
# ENGINE
# ============================================================================

class TransitionEngine:
    """
    Generic decider. Nothing here knows about orders, payments, or
    invoices — only about (state, state, registry).

    The engine is stateless. Construct once, reuse forever.
    """

    def decide(
        self,
        registry: TransitionRegistry,
        current: str,
        target: str,
        context: Optional[Mapping[str, Any]] = None,
    ) -> Decision:
        ctx: Dict[str, Any] = dict(context or {})
        cur = registry.normalize(current)
        tgt = registry.normalize(target)

        # Enrich the context so predicates always see the two states.
        ctx.setdefault('current', cur)
        ctx.setdefault('target', tgt)

        # 1. Same-state is a no-op.
        if cur == tgt:
            return Decision(
                allowed=True,
                current=cur,
                target=tgt,
                reason="no-op: already in target state",
                is_terminal=registry.is_terminal(cur),
                context=ctx,
            )

        # 2. Target must be a known state.
        if not registry.is_valid(tgt):
            return Decision(
                allowed=False,
                current=cur,
                target=tgt,
                reason=(
                    f"'{tgt}' is not a valid state. "
                    f"Valid: {sorted(registry.valid_states)}"
                ),
                context=ctx,
            )

        # 3. Terminal states cannot be left.
        if registry.is_terminal(cur):
            return Decision(
                allowed=False,
                current=cur,
                target=tgt,
                reason=f"'{cur}' is terminal — no transitions allowed",
                is_terminal=True,
                context=ctx,
            )

        # 4. Edge must exist.
        transition = registry.get(cur, tgt)
        if transition is None:
            return Decision(
                allowed=False,
                current=cur,
                target=tgt,
                reason=(
                    f"'{cur}' → '{tgt}' not permitted. "
                    f"Allowed: {sorted(registry.targets_from(cur)) or 'none'}"
                ),
                context=ctx,
            )

        # 5. Predicate decides.
        if not transition.evaluate(ctx):
            return Decision(
                allowed=False,
                current=cur,
                target=tgt,
                reason=(
                    f"Transition '{cur}' → '{tgt}' rejected by predicate"
                    + (f" ({transition.name})" if transition.name else "")
                ),
                matched_transition=transition,
                context=ctx,
            )

        return Decision(
            allowed=True,
            current=cur,
            target=tgt,
            side_effects=list(transition.side_effects),
            matched_transition=transition,
            context=ctx,
        )


# ============================================================================
# POLICY BASE
# ============================================================================

class PolicyBase:
    """
    Thin façade over a registry + engine. Subclasses build their registry
    in `_build_registry()` and declare their own predicate helpers.
    """

    def __init__(
        self,
        engine: Optional[TransitionEngine] = None,
    ):
        self._engine = engine or TransitionEngine()
        self._registry = self._build_registry()

    # Subclasses override.
    def _build_registry(self) -> TransitionRegistry:
        raise NotImplementedError

    # ── Delegated queries ────────────────────────────────────────────

    @property
    def registry(self) -> TransitionRegistry:
        return self._registry

    @property
    def valid_states(self) -> FrozenSet[str]:
        return self._registry.valid_states

    @property
    def initial_state(self) -> str:
        return self._registry.initial_state

    @property
    def terminal_states(self) -> FrozenSet[str]:
        return self._registry.terminal_states

    def normalize(self, state: Optional[str]) -> str:
        return self._registry.normalize(state)

    def is_valid(self, state: str) -> bool:
        return self._registry.is_valid(state)

    def is_terminal(self, state: str) -> bool:
        return self._registry.is_terminal(state)

    def allowed_targets(self, current: str) -> FrozenSet[str]:
        return self._registry.targets_from(current)

    def can_transition(
        self,
        current: str,
        target: str,
        context: Optional[Mapping[str, Any]] = None,
    ) -> bool:
        return self.decide(current, target, context).allowed

    def decide(
        self,
        current: str,
        target: str,
        context: Optional[Mapping[str, Any]] = None,
    ) -> Decision:
        return self._engine.decide(
            self._registry, current, target, context
        )

    # ── Assertions ───────────────────────────────────────────────────

    def assert_transition(
        self,
        current: str,
        target: str,
        context: Optional[Mapping[str, Any]] = None,
    ) -> Decision:
        decision = self.decide(current, target, context)
        if decision.allowed:
            return decision
        raise self.transition_error(decision)

    def assert_valid(self, state: str) -> None:
        if self.is_valid(state):
            return
        raise self.invalid_state_error(state)

    # ── Error hooks (subclasses override to raise domain exceptions) ─

    def transition_error(self, decision: Decision) -> Exception:
        return ValueError(
            f"Illegal transition '{decision.current}' → "
            f"'{decision.target}': {decision.reason}"
        )

    def invalid_state_error(self, state: str) -> Exception:
        return ValueError(
            f"Invalid state '{state}'. "
            f"Valid: {sorted(self.valid_states)}"
        )