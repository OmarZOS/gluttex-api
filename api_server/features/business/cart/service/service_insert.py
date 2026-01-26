





# here, we make schema translations

from typing import List, Tuple
from features.business.order.order_insert import build_ordered_item
from communication.publisher import send_to_product_subscribers
from core.exception_handler import APIException
from core.api_models import OrderedItem_API, OrderedService_API, Person_API, PlacedOrder_API, ProvidedService_API, ServiceResourceRequirement_API, ServiceStaffRequirement_API
from core.messages import *
from core.models import *
from features.insertion import insert_or_complete_or_raise, update_record_in_api
from features.business.product.product_fetch import fetch_product_by_id
from features.app.user.user_fetch import fetch_user_by_id, touch_user
from datetime import datetime;




def build_staff_requirement(staff_requirement_api : ServiceStaffRequirement_API):
    
    requirement =  ServiceStaffRequirement(
        service_staff_requirement_service_id = staff_requirement_api.service_staff_requirement_service_id,
        service_staff_requirement_role = staff_requirement_api.service_staff_requirement_role,
        service_staff_requirement_min_count = staff_requirement_api.service_staff_requirement_min_count,
        service_staff_requirement_max_count = staff_requirement_api.service_staff_requirement_max_count,
        service_staff_requirement_hourly_rate = staff_requirement_api.service_staff_requirement_hourly_rate,
        service_staff_requirement_allocated_hours = staff_requirement_api.service_staff_requirement_allocated_hours,
        service_staff_requirement_notes = staff_requirement_api.service_staff_requirement_notes,
    )
    if (staff_requirement_api.service_staff_requirement_id !=0 ):
        requirement.service_staff_requirement_id = staff_requirement_api.service_staff_requirement_id,
    return requirement


def build_resource_requirement(resource_requirement_api : ServiceResourceRequirement_API):
    requirement =  ServiceResourceRequirement(
        service_resource_requirement_service_id = resource_requirement_api.resource_requirement_service_id,
        service_resource_requirement_name = resource_requirement_api.resource_requirement_name,
        service_resource_requirement_type = resource_requirement_api.resource_requirement_type,
        service_resource_requirement_quantity = resource_requirement_api.resource_requirement_quantity,
        service_resource_requirement_cost_per_unit = resource_requirement_api.resource_requirement_cost_per_unit,
        service_resource_requirement_is_consumable = resource_requirement_api.resource_requirement_is_consumable,
        service_resource_requirement_notes = resource_requirement_api.resource_requirement_notes,
        service_resource_requirement_product_ref = resource_requirement_api.resource_requirement_product_ref,)

    if (resource_requirement_api.resource_requirement_id !=0 ):
        requirement.service_resource_requirement_id = resource_requirement_api.resource_requirement_id,
    
    return requirement

def build_service(provided_service_api : ProvidedService_API)-> ProvidedService:
    service =  ProvidedService(
        provided_service_name = provided_service_api.provided_service_name ,
        provided_service_description = provided_service_api.provided_service_description ,
        provided_service_category_id = provided_service_api.provided_service_category_id ,
        provided_service_product_provider_id = provided_service_api.provided_service_product_provider_id ,
        provided_service_base_price = provided_service_api.provided_service_base_price ,
        provided_service_final_price = provided_service_api.provided_service_final_price ,
        provided_service_actual_duration = provided_service_api.provided_service_actual_duration ,
        provided_service_is_active = provided_service_api.provided_service_is_active ,
        provided_service_pricing_config = provided_service_api.provided_service_pricing_config ,    
    )

    if (provided_service_api.provided_service_id !=0 ):
        service.provided_service_id = provided_service_api.provided_service_id,

    return service


def insert_service(service:ProvidedService_API ,    requirements :  List[ServiceResourceRequirement_API] ,staff_requirements: List[ServiceStaffRequirement_API] ):

    if service.provided_service_category_id == 0:
        raise APIException(
            status=HTTP_404_NOT_FOUND,
            code=SERVICE_CATEGORY_NOT_FOUND,
            details=SERVICE_CATEGORY_NOT_FOUND
        )



    service = build_service(service)
    resource_requirement = []
    staff_requirement = []

    for req in requirements:
        resource_requirement.append(build_resource_requirement(req))

    for req in staff_requirements:
        staff_requirement.append(build_staff_requirement(req))

    service.resource_requirements = resource_requirement
    service.staff_requirements = staff_requirement

    final_service = insert_or_complete_or_raise(service)

    return final_service



def build_ordered_service(ordered_service_api : OrderedService_API, new: bool = False):
    service =  OrderedService(
        ordered_service_quantity = ordered_service_api.ordered_service_quantity ,
        ordered_service_unit_price = ordered_service_api.ordered_service_unit_price ,
        ordered_service_total_price = ordered_service_api.ordered_service_total_price ,
        ordered_service_notes = ordered_service_api.ordered_service_notes ,
    )
    if ordered_service_api.ordered_service_scheduled_at and ordered_service_api.ordered_service_scheduled_at != '':
        service.ordered_service_scheduled_at = ordered_service_api.ordered_service_scheduled_at ,
    if (new):
        service.ordered_service_id = ordered_service_api.ordered_service_service_id,

    return service



def reduce_product_stock(product: Product, quantity: int):
    if product.product_quantity < quantity:
        raise APIException(
            status=HTTP_416_REQUESTED_RANGE_NOT_SATISFIABLE,
            code=PRODUCT_QUANTITY_NOT_ENOUGH,
            details=PRODUCT_QUANTITY_NOT_ENOUGH
        )

    product.product_quantity -= quantity
    update_record_in_api(product)
    
    try:
        send_to_product_subscribers(
            {'product_quantity': product.product_quantity},
            product.id_product
        )
    except:
        pass





# def insert_order(api_ordered_items: List[OrderedItem_API],
#                  ordered_service_api: OrderedService_API) -> Tuple[List[int], PlacedOrder]:

#     try:
#         # ---------------------------------------------------------
#         # 1. VALIDATE USER
#         # ---------------------------------------------------------
#         ordering_user = touch_user(ordered_service_api.ordering_user_id)
#         if ordering_user is None:
#             raise APIException(status=HTTP_404_NOT_FOUND, code=APPUSER_NOT_EXISTS)

#         ordered_items: List[OrderedItem] = []
#         ordered_products: List[Product] = []

#         # Temporary storage to restore the stock if ANY error happens
#         original_quantities = {}

#         # ---------------------------------------------------------
#         # 2. VALIDATE ORDERED PRODUCTS
#         # ---------------------------------------------------------
#         for api_item in api_ordered_items:
#             ordered_item = build_ordered_item(api_item)

#             product = session.get(Product, ordered_item.ordered_product_id)
#             if product is None:
#                 raise APIException(status=HTTP_404_NOT_FOUND, code=PRODUCT_NOT_EXISTS)

#             if product.product_quantity < ordered_item.ordered_quantity:
#                 raise APIException(
#                     status=HTTP_416_REQUESTED_RANGE_NOT_SATISFIABLE,
#                     code=PRODUCT_QUANTITY_NOT_ENOUGH,
#                     details=PRODUCT_QUANTITY_NOT_ENOUGH
#                 )

#             # Save original stock to restore if error occurs
#             original_quantities[product.id_product] = product.product_quantity

#             ordered_items.append(ordered_item)
#             ordered_products.append(product)

#         # ---------------------------------------------------------
#         # 3. VALIDATE & FETCH SERVICE RESOURCE REQUIREMENTS
#         # ---------------------------------------------------------
#         required_resources = session.query(ServiceResourceRequirement).filter_by(
#             service_resource_requirement_service_id=placed_order_api.service_id
#         ).all()

#         # Load products referenced by resources
#         resource_products = []
#         for r in required_resources:
#             if r.service_resource_requirement_is_consumable:
#                 product = session.get(Product, r.service_resource_requirement_product_ref)
#                 if product is None:
#                     raise APIException(status=HTTP_404_NOT_FOUND, code=PRODUCT_NOT_EXISTS)

#                 # Save original stock to restore if needed
#                 original_quantities.setdefault(product.id_product, product.product_quantity)

#                 # Validate quantity
#                 if product.product_quantity < r.service_resource_requirement_quantity:
#                     raise APIException(
#                         status=HTTP_416_REQUESTED_RANGE_NOT_SATISFIABLE,
#                         code=PRODUCT_QUANTITY_NOT_ENOUGH,
#                         details="Not enough stock for required resource"
#                     )

#                 resource_products.append((product, r.service_resource_requirement_quantity))

#         # ---------------------------------------------------------
#         # 4. APPLY STOCK CHANGES (Ordered Items + Required Resources)
#         # ---------------------------------------------------------
#         updated_quantities = []
#         order_total_price = 0.0

#         # Decrement product stock for ordered items
#         for ordered_item, product in zip(ordered_items, ordered_products):
#             product.product_quantity -= ordered_item.ordered_quantity
#             updated_quantities.append(product.product_quantity)

#             order_total_price += (
#                 ordered_item.ordered_quantity
#                 * float(product.product_price)
#                 * (1 + ordered_item.applied_vat)
#             )

#         # Decrement product stock for required resources
#         for product, qty in resource_products:
#             product.product_quantity -= qty

#         # ---------------------------------------------------------
#         # 5. CREATE ORDER + ITEMS (DB ONLY, NOT API YET)
#         # ---------------------------------------------------------
#         placed_order = PlacedOrder(
#             ordering_user_id=ordering_user.id_app_user,
#             order_discount=placed_order_api.order_discount,
#             placed_order_last_mod=datetime.now(),
#             total_price=order_total_price
#         )
#         placed_order.ordered_item = ordered_items

#         session.add(placed_order)
#         session.flush()  # Ensure order + items get IDs

#         # ---------------------------------------------------------
#         # 6. COMMIT TRANSACTION SAFELY
#         # ---------------------------------------------------------
#         session.commit()

#     except Exception as e:
#         session.rollback()

#         # Restore product quantities to original (safe state)
#         for product_id, quantity in original_quantities.items():
#             prod = session.get(Product, product_id)
#             if prod:
#                 prod.product_quantity = quantity

#         session.commit()  # Persist restore

#         raise APIException(status=HTTP_417_EXPECTATION_FAILED,
#                            code=ORDER_INSERT_CONFLICT,
#                            details=str(e))

#     finally:
#         session.close()

#     # ---------------------------------------------------------
#     # 7. SEND UPDATES TO SUBSCRIBERS (AFTER TRANSACTION!)
#     # ---------------------------------------------------------
#     for product in ordered_products:
#         send_to_product_subscribers(
#             {"product_quantity": product.product_quantity},
#             product.id_product
#         )

#     for product, _ in resource_products:
#         send_to_product_subscribers(
#             {"product_quantity": product.product_quantity},
#             product.id_product
#         )

#     return updated_quantities, placed_order











