










from core.models import AdditionalFee, Payment
from features.business.cart.cart_fetch import touch_cart
from features.insertion import insert_or_complete_or_raise
from features.business.cart.cart_insert import create_deposit_for_cart, create_payment, create_payment_for_invoice
from features.business.finance.payment_fetch import touch_invoice
from core.api_models import AdditionalFee_API, Deposit_API, Payment_API


def create_fee(fee: AdditionalFee_API, payment : Payment = None):
    new_fee = AdditionalFee(
        additional_fee_payment_id=fee.additional_fee_payment_id,
        additional_fee_name=fee.additional_fee_name,
        additional_fee_amount=fee.additional_fee_amount,
        additional_fee_description=fee.additional_fee_description,
        additional_fee_on_provider_id = fee.additional_fee_on_provider_id,
        additional_fee_user_id = fee.additional_fee_user_id,
    )
    if (fee.additional_fee_id):
        new_fee.additional_fee_id = fee.additional_fee_id

    if payment:
        new_fee.additional_fee_payment = payment

    return new_fee


def insert_financial_item(payment: Payment_API = None,deposit : Deposit_API= None, fee : AdditionalFee_API =None):
    if payment:
        if payment.payment_invoice_id:
            invoice = touch_invoice(payment.payment_invoice_id)
            if invoice:
                return create_payment_for_invoice(invoice,payment.payment_amount)
    if fee:
        # new_payment = create_payment(payment)
        new_fee = create_fee(fee,create_payment(payment) if payment else None)
        return insert_or_complete_or_raise(new_fee)

    if deposit:
        if deposit.deposit_cart_id:
            cart = touch_cart(deposit.deposit_cart_id)
            if cart:
                return create_deposit_for_cart(cart,deposit.deposit_amount)
    return None