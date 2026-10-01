# services/product_service.py
"""
Product service — local operations only.

Responsibilities (strictly local):
  - validations against the repository (existence, category, uniqueness)
  - model construction (Product, ProductImage, Iproduct, NamingContribution)
  - persistence via repositories
  - entity-level rollback (delete local rows)

Allowed collaborators:
  - repositories (ProductRepository, IProductRepository,
    NamingContributionRepository)
  - pure-local helpers that have no I/O beyond repos

Forbidden collaborators:
  - AIService (network / model inference)
  - any service that performs a remote call
  - subscriber notification (that belongs to the workflow or the router)
  - background task scheduling

Every method the workflow needs to reach is public (no leading underscore).
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional, Any

from core.exceptions.specific.supplier_exceptions import (
    ImageInsertFailedException,
    ImageUpdateFailedException,
)
from core.models.api_models import (
    Product_API,
    ProductImage_API,
    Iproduct_API,
    NamingContribution_API,
)
from core.exceptions.specific.product_exceptions import (
    ProductNotFoundException,
    ProductAlreadyExistsException,
    ProductInsertFailedException,
    ProductUpdateFailedException,
    ProductDeleteFailedException,
    ProductCategoryNotFoundException,
    ProductImageNotFoundException,
)
from core.models.models import Product, ProductImage, Iproduct
from repositories.product_repository import ProductRepository
from repositories.iproduct_repository import IProductRepository
from repositories.naming_contribution_repository import (
    NamingContributionRepository,
)

logger = logging.getLogger(__name__)

# Canonical visibility values accepted by the service.
VISIBILITY_VISIBLE = 'VISIBLE'
VISIBILITY_HIDDEN = 'HIDDEN'

# Contribution type used for every iproduct naming row. Matches the
# enum on `naming_contribution.naming_contribution_type`.
IPRODUCT_CONTRIBUTION_TYPE = 'product'


class ProductService:
    """Local-only product operations."""

    def __init__(self):
        self.product_repo = ProductRepository()
        self.iproduct_repo = IProductRepository()
        self.naming_repo = NamingContributionRepository()

    # ==================== Retrieval ====================

    def get_product_by_id(
        self,
        product_id: int,
        full: bool = False,
        include_hidden: bool = True,
    ) -> Product:
        """
        Fetch a product by id.

        `include_hidden` defaults to True so the editor can always open a
        product by id. Pass False to treat a hidden product as missing.
        """
        product = self.product_repo.get_product_by_id(
            product_id,
            eager_load=full,
            include_hidden=include_hidden,
        )
        if not product:
            logger.warning(f"Product not found with ID: {product_id}")
            raise ProductNotFoundException(product_id=product_id)
        return product

    def get_all_products(
        self,
        user_id: int = 0,
        provider_id: int = 0,
        category_id: int = 0,
        offset: int = 0,
        limit: int = 10,
        serialize: bool = False,
        include_hidden: bool = False,
    ) -> List[Product]:
        """
        Fetch all products with filters.

        `include_hidden` defaults to False so the public catalog never
        surfaces hidden products.
        """
        return self.product_repo.get_all_products(
            user_id,
            provider_id,
            category_id,
            offset,
            limit,
            serialize,
            include_hidden=include_hidden,
        )

    def get_products_by_category(
        self,
        category_id: int,
        offset: int = 0,
        limit: int = 10,
        include_hidden: bool = False,
    ) -> List[Product]:
        category = self.product_repo.get_product_category_by_id(category_id)
        if not category:
            raise ProductCategoryNotFoundException(category_id=category_id)
        return self.product_repo.get_products_by_category(
            category_id,
            offset,
            limit,
            include_hidden=include_hidden,
        )

    def get_product_categories(self) -> List:
        return self.product_repo.get_product_categories()

    def get_iproduct_by_barcode(self, barcode: str) -> Optional[List[Iproduct]]:
        return self.iproduct_repo.get_by_barcode(barcode)

    def get_iproduct_by_id(self, iproduct_id: int) -> Optional[Iproduct]:
        return self.iproduct_repo.get_by_id(iproduct_id)

    # ==================== Category validation ====================

    def validate_category(self, category_id: int) -> Any:
        """
        Local: fetch the category or raise. Used by the workflow before it
        hands a Product_API to create/update.
        """
        category = self.product_repo.get_product_category_by_id(category_id)
        if not category:
            logger.warning(f"Product category not found with ID: {category_id}")
            raise ProductCategoryNotFoundException(category_id=category_id)
        return category

    # ==================== Creation ====================

    def create_product(
        self,
        product_api: Product_API,
        image: Optional[ProductImage_API] = None,
        iproduct: Optional[Iproduct_API] = None,
    ) -> Product:
        """
        Local: build and persist a Product. All validation happens here
        against the local repositories. The workflow is responsible for
        producing `iproduct` (via AI) before calling.

        When `iproduct` carries a `naming` block, the naming contribution
        is resolved (or created) *before* the iproduct insert, so the
        iproduct row always has a valid `iproduct_naming_ref`.
        """
        logger.info(f"Creating new product: {product_api.product_name}")

        if product_api.id_product:
            existing = self.product_repo.get_product_by_id(
                product_api.id_product,
                include_hidden=True,
            )
            if existing:
                raise ProductAlreadyExistsException(
                    product_id=product_api.id_product,
                    product_name=product_api.product_name,
                )

        product_category = self.validate_category(product_api.product_category_id)

        product = self.build_product_model(product_api)
        product.product_category_id = product_category.id_product_category

        if image and image.product_image_url:
            product.product_image = [
                ProductImage(product_image_url=image.product_image_url)
            ]

        if iproduct:
            self.attach_iproduct(product, iproduct)

        try:
            result = self.product_repo.create_product(product)
            logger.info(f"Product created successfully with ID: {result.id_product}")
            return result
        except Exception as e:
            logger.error(f"Failed to create product: {e}")
            raise ProductInsertFailedException(
                error=str(e),
                product_name=product_api.product_name,
            )

    # ==================== Update ====================

    def update_product(
        self,
        product_id: int,
        product_api: Product_API,
        image: Optional[ProductImage_API] = None,
    ) -> Product:
        """
        Local: apply fields and persist. The workflow handles background
        tasks, notifications, and any remote calls.

        Loads with `include_hidden=True` so an editor can edit a hidden
        product without it appearing to not exist.
        """
        logger.info(f"Updating product with ID: {product_id}")

        product_category = self.validate_category(product_api.product_category_id)
        product = self.get_product_by_id(product_id, include_hidden=True)

        changes = self._collect_changes(product, product_api)

        product.product_name = product_api.product_name
        product.product_brand = product_api.product_brand
        product.product_barcode = product_api.product_barcode
        product.product_price = product_api.product_price
        product.product_base_price = getattr(
            product_api, "product_base_price", product.product_base_price
        )
        product.product_quantity = product_api.product_quantity
        product.product_reserved_quantity = getattr(
            product_api, "product_reserved_quantity",
            product.product_reserved_quantity
        )
        product.product_quantifier = product_api.product_quantifier
        product.product_description = product_api.product_description
        product.product_visibility = getattr(
            product_api, "product_visibility", product.product_visibility
        )
        product.product_origin_id = getattr(
            product_api, "product_origin_id", product.product_origin_id
        )
        product.product_category_id = product_category.id_product_category
        product.last_updated = datetime.now()

        if image and image.product_image_url:
            self.handle_product_image(image, product)

        try:
            updated = self.product_repo.update_product(product)
            logger.info(
                f"Product {product_id} updated successfully. "
                f"Changes: {changes if changes else 'none'}"
            )
            return updated
        except Exception as e:
            logger.error(f"Failed to update product {product_id}: {e}")
            raise ProductUpdateFailedException(
                product_id=product_id,
                error=str(e),
            )

    def update_product_visibility(
        self,
        product_id: int,
        visibility: str,
    ) -> Product:
        """
        Local: set only the visibility field and persist.

        Used by the dedicated PATCH endpoint so flipping visibility doesn't
        require the caller to send a full Product_API or risk overwriting
        other fields.

        `visibility` must be either 'VISIBLE' or 'HIDDEN' (case-insensitive
        on input; stored upper-case).
        """
        normalized = (visibility or '').strip().upper()
        if normalized not in (VISIBILITY_VISIBLE, VISIBILITY_HIDDEN):
            raise ValueError(
                f"Invalid visibility '{visibility}'. "
                f"Expected '{VISIBILITY_VISIBLE}' or '{VISIBILITY_HIDDEN}'."
            )

        product = self.get_product_by_id(product_id, include_hidden=True)

        if product.product_visibility == normalized:
            logger.info(
                f"Product {product_id} visibility already '{normalized}'; "
                f"no change."
            )
            return product

        previous = product.product_visibility
        product.product_visibility = normalized
        product.last_updated = datetime.now()

        try:
            updated = self.product_repo.update_product(product)
            logger.info(
                f"Product {product_id} visibility: {previous} → {normalized}"
            )
            return updated
        except Exception as e:
            logger.error(
                f"Failed to update visibility for product {product_id}: {e}"
            )
            raise ProductUpdateFailedException(
                product_id=product_id,
                error=str(e),
            )

    # ==================== Deletion ====================

    def delete_product(self, product_id: int, force_delete: bool = False) -> bool:
        logger.info(f"Deleting product with ID: {product_id} (force={force_delete})")
        product = self.get_product_by_id(product_id, include_hidden=True)

        # if not force_delete:
        #     has_dependencies = self.check_product_dependencies(product_id)
        #     if has_dependencies:
        #         raise ProductDeleteFailedException(
        #             product_id=product_id,
        #             has_dependencies=True,
        #             error="Product has existing dependencies (orders, carts)",
        #         )

        product.product_visibility = "DELETED"

        try:
            result = self.product_repo.update_product(product)
            if not result:
                raise ProductDeleteFailedException(
                    product_id=product_id,
                    error="Repository returned False",
                )
            logger.info(f"Product {product_id} deleted successfully")
            return result
        except ProductDeleteFailedException:
            raise
        except Exception as e:
            logger.error(f"Failed to delete product {product_id}: {e}")
            raise ProductDeleteFailedException(
                product_id=product_id,
                error=str(e),
            )

    def check_product_dependencies(self, product_id: int) -> bool:
        """Local: true when the product is referenced by any order or cart."""
        order_items = self.product_repo.get_order_items_by_product(product_id)
        if order_items:
            logger.debug(f"Product {product_id} has {len(order_items)} order items")
            return True

        cart_items = self.product_repo.get_cart_items_by_product(product_id)
        if cart_items:
            logger.debug(f"Product {product_id} has {len(cart_items)} cart items")
            return True

        return False

    # ==================== Model builders (local, pure) ====================

    def build_product_model(self, product_api: Product_API) -> Product:
        return Product(
            product_name=product_api.product_name,
            product_brand=product_api.product_brand,
            product_barcode=product_api.product_barcode,
            product_price=product_api.product_price,
            product_base_price=product_api.product_base_price,
            product_quantifier=product_api.product_quantifier,
            product_quantity=product_api.product_quantity,
            product_reserved_quantity=product_api.product_reserved_quantity,
            product_visibility=getattr(
                product_api, "product_visibility", VISIBILITY_VISIBLE
            ),
            product_description=product_api.product_description,
            product_owner=product_api.product_owner,
            product_provider_id=product_api.product_provider_id,
            product_origin_id=getattr(product_api, "product_origin_id", None),
            created=datetime.now(),
            last_updated=datetime.now(),
        )

    # ==================== Iproduct + NamingContribution ====================

    def attach_iproduct(self, product: Product, iproduct_api: Iproduct_API) -> None:
        """
        Local: link an Iproduct to a Product.

        Order of operations matters:
          1. Resolve the naming contribution from the API payload
             (either the nested `naming` block or the flat
             `iproduct_name`). This may create a NamingContribution row.
          2. Create or update the Iproduct, pointing its
             `iproduct_naming_ref` at the contribution.
          3. Link the Iproduct onto the Product via `product.product_origin`.

        Steps 1 and 2 are wrapped in a best-effort rollback: if the
        iproduct insert fails, the freshly-created naming row is
        deleted so a retry doesn't leave an orphan behind. If the naming
        row already existed, it is left alone.
        """
        if iproduct_api.id_iproduct:
            existing = self.iproduct_repo.get_by_id(iproduct_api.id_iproduct)
            if existing:
                self.update_iproduct(existing, iproduct_api)
                product.product_origin = existing
                logger.debug(f"Linked existing IProduct {existing.id_iproduct}")
                return

        # New iproduct path: resolve naming first.
        contribution = self.resolve_naming_contribution(iproduct_api)
        created_naming = contribution is not None and getattr(
            contribution, "_was_just_created", False
        )

        try:
            new_iproduct = self.create_iproduct_from_api(
                iproduct_api,
                naming_contribution_id=(
                    contribution.id_naming_contribution
                    if contribution else None
                ),
            )
            product.product_origin = new_iproduct
            logger.debug("Linked new IProduct to product")
        except Exception:
            # Roll back the contribution we just created so retries
            # don't accumulate orphans. Existing contributions are
            # left untouched.
            if created_naming and contribution is not None:
                try:
                    self.naming_repo.delete(contribution.id_naming_contribution)
                    logger.warning(
                        "Rolled back NamingContribution %s after iproduct "
                        "insert failed",
                        contribution.id_naming_contribution,
                    )
                except Exception as rollback_err:
                    logger.error(
                        "Failed to roll back NamingContribution %s: %s",
                        contribution.id_naming_contribution,
                        rollback_err,
                    )
            raise

    def resolve_naming_contribution(
        self,
        iproduct_api: Iproduct_API,
    ) -> Optional[Any]:
        """
        Local: produce the NamingContribution row backing this iproduct.

        Resolution order:
          1. Nested `naming` block on the API payload — full control.
          2. Flat `iproduct_name` — synthesise en/ar/fr from it.
          3. Neither — return None. The iproduct will be persisted with
             `iproduct_naming_ref = None`, which is allowed by the FK
             (nullable) and can be backfilled later.

        Tags the returned row with `_was_just_created = True` when this
        call inserted it, so the caller can roll back on downstream
        failure. The attribute is transient and not persisted.
        """
        nested: Optional[NamingContribution_API] = getattr(
            iproduct_api, "naming", None
        )

        if nested is not None:
            name_en = (nested.en or "").strip()
            if not name_en:
                logger.warning(
                    "Iproduct_API.naming.en is blank; skipping naming "
                    "contribution."
                )
                return None

            existing = self.naming_repo.get_by_english(
                name_en, contribution_type=IPRODUCT_CONTRIBUTION_TYPE
            )
            if existing:
                return existing

            contribution = self.naming_repo.get_or_create(
                name_en=name_en,
                name_ar=nested.ar,
                name_fr=nested.fr,
                contribution_type=IPRODUCT_CONTRIBUTION_TYPE,
                icon_url=(
                    nested.naming_contribution_icon_url
                    or iproduct_api.iproduct_image_url
                ),
                status=nested.naming_contribution_status or "APP_TRANSLATED",
            )
            setattr(contribution, "_was_just_created", True)
            return contribution

        flat_name = (iproduct_api.iproduct_name or "").strip()
        if not flat_name:
            logger.debug(
                "Iproduct has neither `naming` nor `iproduct_name`; "
                "persisting without a naming contribution."
            )
            return None

        existing = self.naming_repo.get_by_english(
            flat_name, contribution_type=IPRODUCT_CONTRIBUTION_TYPE
        )
        if existing:
            return existing

        contribution = self.naming_repo.get_or_create(
            name_en=flat_name,
            name_ar=flat_name,
            name_fr=flat_name,
            contribution_type=IPRODUCT_CONTRIBUTION_TYPE,
            icon_url=iproduct_api.iproduct_image_url,
        )
        setattr(contribution, "_was_just_created", True)
        return contribution

    def create_iproduct_from_api(
        self,
        iproduct_api: Iproduct_API,
        naming_contribution_id: Optional[int] = None,
    ) -> Iproduct:
        """
        Build and persist an Iproduct.

        `iproduct_name` is set from `naming.en` when a naming block is
        present, so the flat column and the naming row never drift.
        The `naming_contribution_id` argument overrides anything the
        caller might have set on the API payload — the FK is owned by
        the service, not by the client.
        """
        now = datetime.now()

        nested: Optional[NamingContribution_API] = getattr(
            iproduct_api, "naming", None
        )
        flat_name = (iproduct_api.iproduct_name or "").strip()
        resolved_name = (
            (nested.en or "").strip() if nested is not None else ""
        ) or flat_name or "Unknown"

        iproduct = Iproduct(
            iproduct_name=resolved_name,
            iproduct_barcode=iproduct_api.iproduct_barcode,
            iproduct_brand=iproduct_api.iproduct_brand or "Unknown",
            iproduct_estimated_price=iproduct_api.iproduct_estimated_price or 0.0,
            iproduct_price_currency=iproduct_api.iproduct_price_currency or "DZD",
            iproduct_gluten_status=iproduct_api.iproduct_gluten_status or "unknown",
            iproduct_info_source=iproduct_api.iproduct_info_source or "ai_analysis",
            iproduct_info_confidence=iproduct_api.iproduct_info_confidence or 0.0,
            iproduct_last_price_update=iproduct_api.iproduct_last_price_update or now,
            iproduct_created_at=iproduct_api.iproduct_created_at or now,
            iproduct_last_update=iproduct_api.iproduct_last_update or now.isoformat(),
            iproduct_model_name=iproduct_api.iproduct_model_name,
            iproduct_image_url=iproduct_api.iproduct_image_url,
            iproduct_naming_ref=naming_contribution_id,
        )

        self.iproduct_repo.create(iproduct)
        return iproduct

    def update_iproduct(self, existing: Iproduct, new_data: Iproduct_API) -> Iproduct:
        """
        Apply fields to an existing Iproduct.

        When the payload carries a `naming` block, the naming
        contribution is resolved (or created) and the iproduct's
        `iproduct_naming_ref` is updated to point at it. The flat
        `iproduct_name` is kept in sync with `naming.en`.
        """
        now = datetime.now()

        nested: Optional[NamingContribution_API] = getattr(new_data, "naming", None)
        if nested is not None and (nested.en or "").strip():
            contribution = self.resolve_naming_contribution(new_data)
            if contribution is not None:
                existing.iproduct_naming_ref = contribution.id_naming_contribution
                # Naming wins over the flat name.
                existing.iproduct_name = (nested.en or "").strip()
        elif new_data.iproduct_name:
            existing.iproduct_name = new_data.iproduct_name

        if new_data.iproduct_brand:
            existing.iproduct_brand = new_data.iproduct_brand
        if new_data.iproduct_estimated_price is not None:
            existing.iproduct_estimated_price = new_data.iproduct_estimated_price
            existing.iproduct_last_price_update = now
        if new_data.iproduct_gluten_status:
            existing.iproduct_gluten_status = new_data.iproduct_gluten_status
        if new_data.iproduct_info_source:
            existing.iproduct_info_source = new_data.iproduct_info_source
        if new_data.iproduct_info_confidence is not None:
            existing.iproduct_info_confidence = new_data.iproduct_info_confidence
        if new_data.iproduct_image_url:
            existing.iproduct_image_url = new_data.iproduct_image_url

        existing.iproduct_last_update = now.isoformat()
        self.iproduct_repo.update(existing)
        logger.debug(f"Updated IProduct {existing.id_iproduct}")
        return existing

    # ==================== Images ====================

    def handle_product_image(self, image: ProductImage_API, product: Product) -> None:
        """Local: create or update the product's image row."""
        if image.id_product_image == 0:
            new_image = ProductImage(product_image_url=image.product_image_url)
            new_image.product_ref = product
            try:
                self.product_repo.create_product_image(new_image)
                logger.info(f"Created product image for product {product.id_product}")
            except Exception as e:
                logger.error(f"Failed to create product image: {e}")
                raise ImageInsertFailedException(
                    error=str(e),
                    details={"product_id": product.id_product},
                )
        else:
            existing_images = self.product_repo.get_product_image_by_id(
                image.id_product_image
            )
            if existing_images:
                existing_image = existing_images[0]
                existing_image.product_image_url = image.product_image_url
                try:
                    self.product_repo.update_product_image(existing_image)
                    logger.info(f"Updated product image {image.id_product_image}")
                except Exception as e:
                    logger.error(f"Failed to update product image: {e}")
                    raise ImageUpdateFailedException(
                        image_id=image.id_product_image,
                        error=str(e),
                    )

    # ==================== Helpers ====================

    def _collect_changes(self, product: Product, product_api: Product_API) -> List[str]:
        changes: List[str] = []
        if product.product_name != product_api.product_name:
            changes.append(f"name: {product.product_name} -> {product_api.product_name}")
        if product.product_price != product_api.product_price:
            changes.append(f"price: {product.product_price} -> {product_api.product_price}")
        if product.product_quantity != product_api.product_quantity:
            changes.append(f"quantity: {product.product_quantity} -> {product_api.product_quantity}")
        if product.product_visibility != getattr(
            product_api, "product_visibility", product.product_visibility
        ):
            changes.append(
                f"visibility: {product.product_visibility} -> "
                f"{getattr(product_api, 'product_visibility', None)}"
            )
        return changes

    def product_to_dict(self, product: Product) -> Dict[str, Any]:
        """Local: serialise a Product for notifications."""
        out: Dict[str, Any] = {}
        for key, value in product.__dict__.items():
            if key.startswith("_"):
                continue
            if hasattr(value, "isoformat"):
                out[key] = value.isoformat()
            else:
                out[key] = value
        return out