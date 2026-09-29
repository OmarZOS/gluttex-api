# policies/transitions.py
"""
Generic transition engine.

A transition is a value: (source, target, predicate, side_effects).
The engine asks the predicate whether the move is allowed, given the
caller-supplied input. The engine does not interpret that input — it
hands it straight to the predicate.

Predicates take whatever the policy decides they should take. For
entity-specific policies that means an ORM instance. For entity-less
policies it means whatever the caller passes.
"""

from dataclasses import dataclass, field
from typing import (
    Any,
    Callable,
    Dict,
    FrozenSet,
    Iterable,
    List,
    Optional,
    Tuple,
)


# A predicate is any callable. The engine calls it with the input the
# policy declared at registry-build time.
Predicate = Callable[..., bool]


def always(*args, **kwargs) -> bool:
    """Default predicate — edge is always allowed when reached."""
    return True


# ============================================================================
# TRANSITION
# ============================================================================

@dataclass(frozen=True)
class Transition:
    source: str
    target: str
    predicate: Predicate = always
    side_effects: Tuple[str, ...] = ()
    name: Optional[str] = None

    def evaluate(self, *args, **kwargs) -> bool:
        try:
            return bool(self.predicate(*args, **kwargs))
        except Exception:
            # A predicate that raises is treated as "denied".
            return False


# ============================================================================
# DECISION
# ============================================================================

@dataclass(frozen=True)
class Decision:
    allowed: bool
    current: str
    target: str
    reason: Optional[str] = None
    side_effects: List[str] = field(default_factory=list)
    is_terminal: bool = False
    matched_transition: Optional[Transition] = None


# ============================================================================
# REGISTRY
# ============================================================================

class TransitionRegistry:
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

        self._edges: Dict[Tuple[str, str], Transition] = {}
        self._by_source: Dict[str, List[Transition]] = {}

    def normalize(self, state: Optional[str]) -> str:
        return self._normalize(state)

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
            raise ValueError(f"Duplicate transition {source} → {target}")

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

    def is_valid(self, state: str) -> bool:
        return self.normalize(state) in self.valid_states

    def is_terminal(self, state: str) -> bool:
        return self.normalize(state) in self.terminal_states

    def get(self, current: str, target: str) -> Optional[Transition]:
        return self._edges.get(
            (self.normalize(current), self.normalize(target))
        )

    def outgoing(self, current: str) -> List[Transition]:
        return list(self._by_source.get(self.normalize(current), []))

    def targets_from(self, current: str) -> FrozenSet[str]:
        return frozenset(t.target for t in self.outgoing(current))


# ============================================================================
# ENGINE
# ============================================================================

class TransitionEngine:
    """
    Generic decider. The engine calls `predicate(input, **extras)`.
    What `input` is depends entirely on the policy.
    """

    def decide(
        self,
        registry: TransitionRegistry,
        current: str,
        target: str,
        input: Any = None,       # <- whatever the policy decided
        **extras: Any,           # <- additional keyword arguments for the predicate
    ) -> Decision:
        cur = registry.normalize(current)
        tgt = registry.normalize(target)

        if cur == tgt:
            return Decision(
                allowed=True, current=cur, target=tgt,
                reason="no-op: already in target state",
                is_terminal=registry.is_terminal(cur),
            )

        if not registry.is_valid(tgt):
            return Decision(
                allowed=False, current=cur, target=tgt,
                reason=(
                    f"'{tgt}' is not a valid state. "
                    f"Valid: {sorted(registry.valid_states)}"
                ),
            )

        if registry.is_terminal(cur):
            return Decision(
                allowed=False, current=cur, target=tgt,
                reason=f"'{cur}' is terminal — no transitions allowed",
                is_terminal=True,
            )

        transition = registry.get(cur, tgt)
        if transition is None:
            return Decision(
                allowed=False, current=cur, target=tgt,
                reason=(
                    f"'{cur}' → '{tgt}' not permitted. "
                    f"Allowed: {sorted(registry.targets_from(cur)) or 'none'}"
                ),
            )

        if not transition.evaluate(input, **extras):
            return Decision(
                allowed=False, current=cur, target=tgt,
                reason=(
                    f"Transition '{cur}' → '{tgt}' rejected by predicate"
                    + (f" ({transition.name})" if transition.name else "")
                ),
                matched_transition=transition,
            )

        return Decision(
            allowed=True, current=cur, target=tgt,
            side_effects=list(transition.side_effects),
            matched_transition=transition,
        )


# ============================================================================
# POLICY BASE
# ============================================================================

class PolicyBase:
    """
    Thin façade over a registry + engine. Subclasses supply the input
    shape (an ORM instance, a plain value, anything) to `decide`.
    """

    def __init__(self, engine: Optional[TransitionEngine] = None):
        self._engine = engine or TransitionEngine()
        self._registry = self._build_registry()

    def _build_registry(self) -> TransitionRegistry:
        raise NotImplementedError

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
        input: Any = None,
        **extras: Any,
    ) -> bool:
        return self.decide(current, target, input, **extras).allowed

    def decide(
        self,
        current: str,
        target: str,
        input: Any = None,
        **extras: Any,
    ) -> Decision:
        return self._engine.decide(
            self._registry, current, target, input, **extras
        )

    def assert_transition(
        self,
        current: str,
        target: str,
        input: Any = None,
        **extras: Any,
    ) -> Decision:
        decision = self.decide(current, target, input, **extras)
        if decision.allowed:
            return decision
        raise self.transition_error(decision)

    def assert_valid(self, state: str) -> None:
        if self.is_valid(state):
            return
        raise self.invalid_state_error(state)

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