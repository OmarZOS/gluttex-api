









from core.models import AdditionalFee, Deposit, Invoice, Payment
import storage.storage_broker as storage_broker
from core.api_models import AdditionalFee_API, Deposit_API, Payment_API


def touch_payment(payment_id: int):
    payment_list = storage_broker.get(Payment
                              ,{Payment.payment_id :int(payment_id)}
                              ,[]
                              ,[]
                              ,None
                              )
                            
    if payment_list == []:
        return None 
    return payment_list[0]

def touch_deposit(deposit_id:int):
    deposit_list = storage_broker.get(Deposit
                              ,{Deposit.deposit_id :int(deposit_id)}
                              ,[]
                              ,[]
                              ,None
                              )
                            
    if deposit_list == []:
        return None 
    return deposit_list[0]

def touch_fee(fee_id:int):
    fee_list = storage_broker.get(AdditionalFee
                              ,{AdditionalFee.additional_fee_id :int(fee_id)}
                              ,[]
                              ,[]
                              ,None
                              )
                            
    if fee_list == []:
        return None 
    return fee_list[0]

def touch_invoice(invoice_id:int):
    invoice_list = storage_broker.get(Invoice
                              ,{Invoice.invoice_id :int(invoice_id)}
                              ,[]
                              ,[]
                              ,None
                              )
                            
    if invoice_list == []:
        return None 
    return invoice_list[0]