









from core.persistent_models import FinancialDocument
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


def fetch_financial_item(supplier_id: int = 0,person_id: int = 0,client_id: int = 0,seller_id: int = 0,cart_id: int = 0,order_id: int = 0,deposit_id: int = 0,invoice_id: int = 0,offset: int= 0, limit : int=10):
    
    conditions = {}
    if  supplier_id != 0 :
        conditions[FinancialDocument.supplier_id] = supplier_id
    if  client_id != 0 :
        conditions[FinancialDocument.customer_type] = "user"
        conditions[FinancialDocument.customer_id] = client_id
    if  person_id != 0 :
        conditions[FinancialDocument.customer_type] = "person"
        conditions[FinancialDocument.customer_id] = person_id
    if  seller_id != 0 :
        conditions[FinancialDocument.seller_id] = seller_id
    if  cart_id != 0 :
        conditions[FinancialDocument.source_type] = 'cart_based'
        conditions[FinancialDocument.source_id] = cart_id
    if  order_id != 0 :
        conditions[FinancialDocument.source_id] = order_id
    if  deposit_id != 0 :
        conditions[FinancialDocument.document_type] = "deposit"
        conditions[FinancialDocument.document_id] = deposit_id
    if  invoice_id != 0 :
        conditions[FinancialDocument.source_type] = "invoice_based"
        conditions[FinancialDocument.source_id] = invoice_id
    
    
    fianance_list = storage_broker.get(FinancialDocument
                              ,conditions
                              ,None,None
                              ,offset, limit
                              )
                            
    # if invoice_list == []:
    #     return None 
    return fianance_list

