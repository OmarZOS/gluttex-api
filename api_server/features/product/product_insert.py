
# here, we make schema translations

import uuid
from core.exception_handler import APIException
from features.media_net import upload_image
from core.api_models import Iproduct_API, Product_API, ProductImage_API
from core.messages import *
from core.models import *
from features.insertion import insert_or_complete_or_raise, update_record_in_api
from features.product.product_fetch import fetch_iproduct_by_id, fetch_product_by_id
from features.supplier.supplier_fetch import fetch_supplier_by_id
import storage.storage_broker as storage_broker
from datetime import datetime;


def fetch_product_category_object_by_id(category_id: str):
    record = storage_broker.get(ProductCategory,{ProductCategory.id_product_category:category_id},None,[])
    if record == []:
        return None
    supplier = ProductCategory(id_product_category = record[0].id_product_category)
    return supplier 

def build_product(product: Product_API):
    return Product(product_name=product.product_name,
                    product_brand=product.product_brand,
                    product_barcode=product.product_barcode,
                    product_price = product.product_price,
                    product_quantifier = product.product_quantifier,
                    product_quantity = product.product_quantity,
                    product_description = product.product_description,
                    product_owner = product.product_owner,
                    created = datetime.now(),
                    last_updated = datetime.now(),
                    )

async def insert_product(product_api: Product_API, image: ProductImage_API, iproduct: Iproduct_API = None):
    # 1. Quick existence check
    if fetch_product_by_id(product_api.id_product):
        raise APIException(
            status=HTTP_409_CONFLICT,
            code=PRODUCT_ALREADY_EXISTS,
            details=""
        )

    # 2. Fast validation with early returns
    product_category = fetch_product_category_object_by_id(product_api.id_product_category)
    if not product_category:
        raise APIException(
            status=HTTP_404_NOT_FOUND,
            code=PRODUCT_CATEGORY_NOT_EXISTS,
            message=PRODUCT_CATEGORY_NOT_EXISTS,
            details=""
        )

    product_suppliers = fetch_supplier_by_id(product_api.product_provider_id)
    if not product_suppliers:
        raise APIException(
            status=HTTP_404_NOT_FOUND,
            code=PRODUCT_SUPPLIER_NOT_EXISTS,
            message=PRODUCT_SUPPLIER_NOT_EXISTS,
            details=""
        )

    # 3. Build product with AI data if available
    product = build_product(product_api)
    product.product_provider_id = product_suppliers[0].id_product_provider
    product.product_category_id = product_category.id_product_category
    
    # 4. Handle image efficiently
    if image and image.product_image_url:
        product_image = ProductImage(product_image_url=image.product_image_url)
        product.product_image = [product_image]

    # 5. Handle AI product data (iproduct)
    if iproduct:
        await _handle_iproduct_data(product, iproduct)

    # 6. Insert with error handling
    try:
        product = insert_or_complete_or_raise(product)
        return product
    except Exception as e:
        raise APIException(
            status=HTTP_417_EXPECTATION_FAILED,
            code=PRODUCT_INSERT_FAILED,
            details=f"{str(e)}"
        )

async def _handle_iproduct_data(product: Product, iproduct: Iproduct_API):
    """Handle AI-generated product data efficiently"""
    if iproduct.id_iproduct:
        # Update existing iproduct
        existing_iproduct = fetch_iproduct_by_id(iproduct.id_iproduct)
        if existing_iproduct:
            _update_iproduct(existing_iproduct, iproduct)
            product.product_origin = existing_iproduct
        else:
            # Create new iproduct with the provided ID
            new_iproduct = _create_iproduct_from_api(iproduct)
            product.product_origin = new_iproduct
    else:
        # Create new iproduct without ID
        new_iproduct = _create_iproduct_from_api(iproduct)
        product.product_origin = new_iproduct

def _create_iproduct_from_api(iproduct_api: Iproduct_API) -> Iproduct:
    """Create Iproduct from API data with defaults"""
    now = datetime.now()
    
    return Iproduct(
        iproduct_name=iproduct_api.iproduct_name or "Unknown",
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
        iproduct_image_url=iproduct_api.iproduct_image_url
    )

def _update_iproduct(existing: Iproduct, new_data: Iproduct_API):
    """Update existing iproduct with new AI data"""
    now = datetime.now()
    
    if new_data.iproduct_name:
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
    
    existing.iproduct_last_update = now.isoformat()

    update_record_in_api(existing)    

