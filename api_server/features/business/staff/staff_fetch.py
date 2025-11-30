


from core.exception_handler import APIException
from core.messages import *
from core.models import *
import storage.storage_broker as storage_broker
from sqlalchemy import func


def touch_rule_by_id(id : int):
    data = storage_broker.get(
        ManagementRule,
        {ManagementRule.id_management_rule:id},
        None,
        [
        ]
    )
    
    if data == []:
        return None

    return data[0]


def fetch_staff(org_id, supplier_id, user_id,rule_id, offset, limit):
    # Build conditions dynamically
    conditions = {}

    if int(rule_id) !=0:
        conditions[ManagementRule.id_management_rule] = int(rule_id)
    else:
        if int(user_id) != 0:
            conditions[ManagementRule.rule_ref_user] = int(user_id)

        if int(supplier_id) != 0:
            conditions[ManagementRule.rule_ref_provider] = int(supplier_id)

        if int(org_id) != 0:
            conditions[ManagementRule.rule_ref_org] = int(org_id)

    # Fetch data
    rule_list = storage_broker.get(
        ManagementRule,
        conditions,
        None,
        [
            ManagementRule.management_rule_code,
            ManagementRule.management_rule_status,
            ManagementRule.management_rule_expiry,
            ManagementRule.provider_organisation,
            {
                
                
                ManagementRule.product_provider:[ProductProvider.product_provider_details]},
                {
                    ManagementRule.app_user: [{
                        AppUser.app_user_person: [
                            Person.person_details
                        ]
                    }]
                },
        ],
        offset,
        limit,
    )



    return rule_list












