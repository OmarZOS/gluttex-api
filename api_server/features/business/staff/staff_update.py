from features.business.supplier.supplier_fetch import fetch_only_supplier_by_id
from communication.publisher import notify_invitation_to_role_received, notify_rule_to_role_received
from features.app.notification.builders.notification_builder import NotificationFactory
from features.app.notification.notification_add import build_notification, insert_notification
from features.business.staff.staff_add import build_rule
from features.insertion import insert_or_complete_or_raise, update_record_in_api
from core.api_models import ManagementRule_API, Notification_API
from features.business.staff.staff_fetch import touch_rule_by_id
from core.exception_handler import APIException
from core.messages import *
from core.models import *
import storage.storage_broker as storage_broker
from sqlalchemy import func

def update_staff(rule: ManagementRule_API):
    # Build conditions dynamically
    old_rule = touch_rule_by_id(rule.id_management_rule)
    if int(rule.id_management_rule) != 0:
        if not old_rule :
                    raise APIException(
            status=HTTP_409_CONFLICT,
            code=RULE_NOT_EXISTS,
            details=f"Rule number '{rule.id_management_rule}' not exists."
        )

    new_rule = build_rule(rule)

    old_rule.management_rule_code = new_rule.management_rule_code
    old_rule.management_rule_status = new_rule.management_rule_status
    old_rule.management_rule_expiry = new_rule.management_rule_expiry

    try:
        final_rule = update_record_in_api(old_rule)

        supplier = fetch_only_supplier_by_id(final_rule.rule_ref_provider)[0]
        supplier_id = supplier.id_product_provider
        owner_id = supplier.product_provider_owner

        notification = NotificationFactory.rule.new_rule_added(rule_id=final_rule.id_management_rule
                                                               ,role=final_rule.management_rule_code
                                                               ,rule_type=final_rule.management_rule_status
                                                               ,user_id=final_rule.rule_ref_user
                                                               ,provider_id=supplier_id
                                                               ,organization_id=final_rule.rule_ref_org
                                                               ,invited_by=final_rule.rule_ref_user)

        insert_notification(build_notification(Notification_API(
            #  id_notification = 0,
             notification_code="new_rule_added",
             notification_params= NotificationFactory.dump_dict(notification),
             notification_user_ref= rule.rule_ref_user,
            #  notification_created_at=datetime.now()
        )))

        notify_invitation_to_role_received(notification,owner_id)
        notify_invitation_to_role_received(notification,final_rule.rule_ref_user)

        return final_rule
    except Exception as e:
        raise APIException(
            status=HTTP_417_EXPECTATION_FAILED,
            code=RULE_INSERT_FAILED,
            details=f"{str(e)}"
        )





def answer_staff(rule_id: int,answer :int):
    # Build conditions dynamically
    old_rule = touch_rule_by_id(rule_id)
    if int(rule_id) != 0:
        if not old_rule :
                    raise APIException(
            status=HTTP_409_CONFLICT,
            code=RULE_NOT_EXISTS,
            details=f"Rule number '{rule_id}' doesn't exists."
        )
    if answer == 0:
        old_rule.management_rule_status = 'ACTIVE'
    else: 
        old_rule.management_rule_status = 'REJECTED'
    
    try:
        final_rule = update_record_in_api(old_rule)


        if answer == 0:
            supplier = fetch_only_supplier_by_id(final_rule.rule_ref_provider)[0]
            supplier_id = supplier.id_product_provider
            owner_id = supplier.product_provider_owner

            notification = NotificationFactory.personnel.invitation_accepted(rule_id=final_rule.id_management_rule
                                                            ,user_id=final_rule.rule_ref_user
                                                            ,organization_id=final_rule.rule_ref_org
                                                            ,provider_id=final_rule.rule_ref_provider
                                                            ,role=final_rule.management_rule_code)

            insert_notification(build_notification(Notification_API(
                #  id_notification = 0,
                notification_code="invitation_accepted",
                notification_params= NotificationFactory.dump_dict(notification),
                notification_user_ref= final_rule.rule_ref_user,
                #  notification_created_at=datetime.now()
            )))

            notify_rule_to_role_received(notification,owner_id)

        return final_rule
    except Exception as e:
        raise APIException(
            status=HTTP_417_EXPECTATION_FAILED,
            code=RULE_INSERT_FAILED,
            details=f"{str(e)}"
        )










