from sqlalchemy import Column, DECIMAL, Date, DateTime, Enum, Float, ForeignKeyConstraint, Index, Integer, JSON, String, TIMESTAMP, Text, text
from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy.sql.sqltypes import NullType
from sqlalchemy.orm import declarative_base, relationship

from core.persistent_models import Base,metadata,Location

class Address(Base):
    __tablename__ = 'address'

    id_address = Column(Integer, primary_key=True)
    address_street = Column(String(45))
    address_city = Column(String(45))
    address_postal_code = Column(String(45))
    address_country = Column(String(45))

    delivery = relationship('Delivery', foreign_keys='[Delivery.delivery_address_id]', back_populates='delivery_address')
    delivery_ = relationship('Delivery', foreign_keys='[Delivery.delivery_current_address_id]', back_populates='delivery_current_address')
    location = relationship('Location', back_populates='location_address')


class AppUserType(Base):
    __tablename__ = 'app_user_type'

    id_app_user_type = Column(Integer, primary_key=True)
    app_user_type_desc = Column(String(45))

    app_user = relationship('AppUser', back_populates='app_user_type')


class BloodType(Base):
    __tablename__ = 'blood_type'

    id_blood_type = Column(Integer, primary_key=True)
    blood_type_desc = Column(String(45))

    person = relationship('Person', back_populates='person_blood_type')


class Cart(Base):
    __tablename__ = 'cart'
    __table_args__ = (
        ForeignKeyConstraint(['cart_client_user'], ['app_user.id_app_user'], name='fk_cart_2'),
        ForeignKeyConstraint(['cart_delivery'], ['delivery.id_delivery'], name='fk_cart_4'),
        ForeignKeyConstraint(['cart_person_ref'], ['person.id_person'], name='fk_cart_3'),
        ForeignKeyConstraint(['cart_product_provider_id'], ['product_provider.id_product_provider'], ondelete='RESTRICT', onupdate='CASCADE', name='cart_ibfk_1'),
        ForeignKeyConstraint(['cart_selling_user'], ['app_user.id_app_user'], name='fk_cart_1'),
        Index('fk_cart_2', 'cart_client_user'),
        Index('fk_cart_3_idx', 'cart_person_ref'),
        Index('fk_cart_4_idx', 'cart_delivery'),
        Index('idx_cart_provider', 'cart_product_provider_id'),
        Index('idx_cart_status', 'cart_status'),
        Index('idx_cart_user', 'cart_selling_user')
    )

    cart_id = Column(Integer, primary_key=True)
    cart_product_provider_id = Column(Integer, comment='Provider owning the cart')
    cart_selling_user = Column(Integer, comment='Customer / patient / client id')
    cart_status = Column(String(50), server_default=text("'open'"), comment='open, pending, completed, canceled')
    cart_total_amount = Column(DECIMAL(15, 4), server_default=text("'0.0000'"))
    cart_notes = Column(Text)
    cart_created_at = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
    cart_updated_at = Column(TIMESTAMP)
    cart_person_ref = Column(Integer)
    cart_client_user = Column(Integer)
    cart_due_date = Column(Date)
    cart_delivery = Column(Integer)

    app_user = relationship('AppUser', foreign_keys=[cart_client_user], back_populates='cart')
    delivery = relationship('Delivery', back_populates='cart')
    person = relationship('Person', back_populates='cart')
    cart_product_provider = relationship('ProductProvider', back_populates='cart')
    app_user_ = relationship('AppUser', foreign_keys=[cart_selling_user], back_populates='cart_')
    invoice = relationship('Invoice', back_populates='invoice_cart')
    receipt = relationship('Receipt', back_populates='cart')
    deposit = relationship('Deposit', back_populates='deposit_cart')
    ordered_item = relationship('OrderedItem', back_populates='cart')
    ordered_service = relationship('OrderedService', back_populates='ordered_service_cart')


class Delivery(Base):
    __tablename__ = 'delivery'
    __table_args__ = (
        ForeignKeyConstraint(['delivery_address_id'], ['address.id_address'], name='fk_delivery_1'),
        ForeignKeyConstraint(['delivery_broker_id'], ['delivery_broker.id_delivery_broker'], name='fk_delivery_5'),
        ForeignKeyConstraint(['delivery_current_address_id'], ['address.id_address'], name='fk_delivery_2'),
        ForeignKeyConstraint(['delivery_placed_order'], ['placed_order.id_placed_order'], name='fk_delivery_3'),
        ForeignKeyConstraint(['delivery_provider_id'], ['product_provider.id_product_provider'], name='fk_delivery_4'),
        Index('fk_delivery_1_idx', 'delivery_address_id'),
        Index('fk_delivery_2_idx', 'delivery_current_address_id'),
        Index('fk_delivery_3_idx', 'delivery_placed_order'),
        Index('fk_delivery_4_idx', 'delivery_provider_id'),
        Index('fk_delivery_5_idx', 'delivery_broker_id')
    )

    id_delivery = Column(Integer, primary_key=True)
    recipient_person = Column(Integer)
    recipient_provider = Column(Integer)
    delivery_package_count = Column(String(45))
    delivery_total_weight = Column(DECIMAL(10, 0))
    delivery_cargo_dimensions = Column(String(255))
    delivery_goods_description = Column(Text)
    hs_code = Column(String(255))
    delivery_merchant_name = Column(String(255))
    delivery_shipping_method = Column(String(255))
    delivery_special_instructions = Column(String(45))
    delivery_created_at = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
    delivery_updated_at = Column(TIMESTAMP)
    delivery_status = Column(String(255), server_default=text("'PENDING'"))
    delivery_address_id = Column(Integer)
    delivery_current_address_id = Column(Integer)
    delivery_fee = Column(Float(asdecimal=True), server_default=text("'0'"))
    delivery_placed_order = Column(Integer)
    delivery_provider_id = Column(Integer)
    delivery_broker_id = Column(Integer)

    cart = relationship('Cart', back_populates='delivery')
    delivery_address = relationship('Address', foreign_keys=[delivery_address_id], back_populates='delivery')
    delivery_broker = relationship('DeliveryBroker', back_populates='delivery')
    delivery_current_address = relationship('Address', foreign_keys=[delivery_current_address_id], back_populates='delivery_')
    placed_order = relationship('PlacedOrder', back_populates='delivery')
    delivery_provider = relationship('ProductProvider', back_populates='delivery')


class DiseaseSeverity(Base):
    __tablename__ = 'disease_severity'

    id_disease_severity = Column(Integer, primary_key=True)
    disease_severity_desc = Column(String(45))

    patient = relationship('Patient', back_populates='patient_disease_severity')


class Ingredient(Base):
    __tablename__ = 'ingredient'

    id_ingredient = Column(Integer, primary_key=True)
    ingredient_name = Column(String(45))
    ingredient_icon_url = Column(String(255))
    ingredient_quantifier = Column(String(45))

    recipe_contains_ingredient = relationship('RecipeContainsIngredient', back_populates='contained_ingredient')


class Invoice(Base):
    __tablename__ = 'invoice'
    __table_args__ = (
        ForeignKeyConstraint(['invoice_cart_id'], ['cart.cart_id'], ondelete='RESTRICT', onupdate='CASCADE', name='invoice_ibfk_1'),
        Index('idx_invoice_cart', 'invoice_cart_id'),
        Index('idx_invoice_status', 'invoice_status')
    )

    invoice_id = Column(Integer, primary_key=True)
    invoice_cart_id = Column(Integer)
    invoice_number = Column(String(100))
    invoice_total_amount = Column(DECIMAL(15, 4))
    invoice_status = Column(String(50), server_default=text("'unpaid'"), comment='unpaid, paid, canceled')
    invoice_issue_date = Column(Date)
    invoice_due_date = Column(Date)
    invoice_notes = Column(Text)
    invoice_created_at = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
    invoice_updated_at = Column(TIMESTAMP)

    invoice_cart = relationship('Cart', back_populates='invoice')
    payment = relationship('Payment', back_populates='payment_invoice')
    placed_order = relationship('PlacedOrder', back_populates='invoice')
    deposit = relationship('Deposit', back_populates='deposit_invoice')


class Payment(Base):
    __tablename__ = 'payment'
    __table_args__ = (
        ForeignKeyConstraint(['payment_invoice_id'], ['invoice.invoice_id'], ondelete='RESTRICT', onupdate='CASCADE', name='payment_ibfk_1'),
        Index('idx_invoice', 'payment_invoice_id'),
        Index('idx_status', 'payment_status')
    )

    payment_id = Column(Integer, primary_key=True)
    payment_invoice_id = Column(Integer)
    payment_amount = Column(DECIMAL(15, 4))
    payment_method = Column(String(100), comment='cash, card, bank, mobile')
    payment_status = Column(String(50), server_default=text("'completed'"))
    payment_reference = Column(String(255), comment='Bank or transaction reference')
    payment_notes = Column(Text)
    payment_created_at = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
    payment_updated_at = Column(TIMESTAMP)

    payment_invoice = relationship('Invoice', back_populates='payment')
    receipt = relationship('Receipt', back_populates='receipt_payment')
    additional_fee = relationship('AdditionalFee', back_populates='additional_fee_payment')


class PersonDetails(Base):
    __tablename__ = 'person_details'

    id_person_details = Column(Integer, primary_key=True)
    person_first_name = Column(String(45))
    person_last_name = Column(String(45))
    person_birth_date = Column(Date)
    person_gender = Column(String(45))
    person_nationality = Column(String(45))
    person_phone = Column(String(45))

    person = relationship('Person', back_populates='person_details')


class PlacedOrder(Base):
    __tablename__ = 'placed_order'
    __table_args__ = (
        ForeignKeyConstraint(['ordering_user_id'], ['app_user.id_app_user'], ondelete='RESTRICT', onupdate='RESTRICT', name='fk_placed_order_1'),
        ForeignKeyConstraint(['placed_order_invoice_ref'], ['invoice.invoice_id'], name='fk_placed_order_4'),
        ForeignKeyConstraint(['placed_order_location_ref'], ['location.id_location'], name='fk_placed_order_2'),
        ForeignKeyConstraint(['placed_order_receipt_ref'], ['receipt.receipt_id'], name='fk_placed_order_3'),
        Index('fk_placed_order_1_idx', 'ordering_user_id'),
        Index('fk_placed_order_2_idx', 'placed_order_location_ref'),
        Index('fk_placed_order_3_idx', 'placed_order_receipt_ref'),
        Index('fk_placed_order_4_idx', 'placed_order_invoice_ref')
    )

    id_placed_order = Column(Integer, primary_key=True)
    order_discount = Column(Float(asdecimal=True))
    total_price = Column(Float(asdecimal=True))
    ordering_user_id = Column(Integer)
    placed_order_location_ref = Column(Integer)
    placed_order_state_ref = Column(Integer)
    placed_order_last_mod = Column(TIMESTAMP)
    placed_order_invoice_ref = Column(Integer)
    placed_order_receipt_ref = Column(Integer)
    placed_order_creation = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))

    delivery = relationship('Delivery', back_populates='placed_order')
    ordering_user = relationship('AppUser', back_populates='placed_order')
    invoice = relationship('Invoice', back_populates='placed_order')
    location = relationship('Location', back_populates='placed_order')
    receipt = relationship('Receipt', back_populates='placed_order')
    ordered_item = relationship('OrderedItem', back_populates='placed_order')


class Plan(Base):
    __tablename__ = 'plan'

    id_plan = Column(Integer, primary_key=True)
    plan_name = Column(String(45))
    plan_price = Column(DECIMAL(10, 2))
    billing_cycle = Column(Enum('monthly', 'yearly'), server_default=text("'monthly'"))
    plan_type = Column(Enum('individual', 'organization'), server_default=text("'individual'"))
    plan_created_at = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
    plan_updated_at = Column(TIMESTAMP)

    app_user = relationship('AppUser', back_populates='plan')


class ProductCategory(Base):
    __tablename__ = 'product_category'

    id_product_category = Column(Integer, primary_key=True)
    product_category_desc = Column(String(45))
    product_category_icon = Column(String(255))

    iproduct = relationship('Iproduct', back_populates='iproduct_category')
    product = relationship('Product', back_populates='product_category')


class ProductProviderType(Base):
    __tablename__ = 'product_provider_type'

    id_product_provider_type = Column(Integer, primary_key=True)
    product_provider_type_desc = Column(String(45))
    product_provider_ref = Column(Integer)

    product_provider = relationship('ProductProvider', back_populates='product_provider_type')


class ProvidedServiceCategory(Base):
    __tablename__ = 'provided_service_category'
    __table_args__ = (
        Index('idx_provided_service_category_active', 'provided_service_category_deleted_at'),
        Index('idx_provided_service_category_created_at', 'provided_service_category_created_at'),
        Index('idx_provided_service_category_name', 'provided_service_category_name')
    )

    provided_service_category_id = Column(Integer, primary_key=True)
    provided_service_category_name = Column(String(255))
    provided_service_category_icon_url = Column(String(500))
    provided_service_category_avg_duration = Column(DECIMAL(10, 2), comment='Average duration in minutes')
    provided_service_category_description = Column(Text)
    provided_service_category_created_at = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
    provided_service_category_updated_at = Column(TIMESTAMP)
    provided_service_category_deleted_at = Column(TIMESTAMP)

    provided_service = relationship('ProvidedService', back_populates='provided_service_category')


class ProviderDetails(Base):
    __tablename__ = 'provider_details'

    idprovider_details_id = Column(Integer, primary_key=True)
    provider_name = Column(String(45))
    provider_contact_info = Column(Text)

    product_provider = relationship('ProductProvider', back_populates='product_provider_details')


class Reaction(Base):
    __tablename__ = 'reaction'

    id_reaction = Column(Integer, primary_key=True)
    reaction_type = Column(String(45))

    comment_reaction = relationship('CommentReaction', back_populates='reaction')
    provider_reaction = relationship('ProviderReaction', back_populates='reaction')
    recipe_reaction = relationship('RecipeReaction', back_populates='reaction')
    product_reaction = relationship('ProductReaction', back_populates='reaction')


class Receipt(Base):
    __tablename__ = 'receipt'
    __table_args__ = (
        ForeignKeyConstraint(['receipt_cart_ref'], ['cart.cart_id'], name='fk_receipt_1'),
        ForeignKeyConstraint(['receipt_payment_id'], ['payment.payment_id'], ondelete='CASCADE', onupdate='CASCADE', name='receipt_ibfk_1'),
        Index('fk_receipt_1_idx', 'receipt_cart_ref'),
        Index('idx_payment', 'receipt_payment_id')
    )

    receipt_id = Column(Integer, primary_key=True)
    receipt_amount = Column(DECIMAL(15, 4), nullable=False)
    receipt_payment_id = Column(Integer)
    receipt_number = Column(String(100))
    receipt_notes = Column(Text)
    receipt_created_at = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
    receipt_cart_ref = Column(Integer)

    placed_order = relationship('PlacedOrder', back_populates='receipt')
    cart = relationship('Cart', back_populates='receipt')
    receipt_payment = relationship('Payment', back_populates='receipt')
    deposit = relationship('Deposit', back_populates='deposit_receipt')


class RecipeCategory(Base):
    __tablename__ = 'recipe_category'

    id_recipe_category = Column(Integer, primary_key=True)
    recipe_category_desc = Column(String(45))
    recipe_category_icon = Column(String(255))

    recipe = relationship('Recipe', back_populates='recipe_category')


class SerologyIndicator(Base):
    __tablename__ = 'serology_indicator'

    id_serology_indicator = Column(Integer, primary_key=True)
    serology_indicator_name = Column(String(45))
    serology_indicator_desc = Column(String(300))

    serology = relationship('Serology', back_populates='indicator')


class Symptom(Base):
    __tablename__ = 'symptom'

    id_symptom = Column(Integer, primary_key=True)
    symptom_name = Column(String(45))
    symptom_desc = Column(String(300))

    presented_symptom = relationship('PresentedSymptom', back_populates='symptom')


class Wallet(Base):
    __tablename__ = 'wallet'

    id_wallet = Column(Integer, primary_key=True)
    wallet_type = Column(String(45))
    wallet_currency = Column(String(45))
    wallet_balance = Column(Float(asdecimal=True))
    wallet_status = Column(String(45))

    delivery_broker = relationship('DeliveryBroker', back_populates='delivery_broker_wallet')
    money_transaction = relationship('MoneyTransaction', foreign_keys='[MoneyTransaction.money_transaction_wallet_destination_id]', back_populates='money_transaction_wallet_destination')
    money_transaction_ = relationship('MoneyTransaction', foreign_keys='[MoneyTransaction.money_transaction_wallet_source_id]', back_populates='money_transaction_wallet_source')
    provider_organisation = relationship('ProviderOrganisation', back_populates='provider_organisation_wallet')
    app_user = relationship('AppUser', back_populates='app_user_wallet')
    product_provider = relationship('ProductProvider', back_populates='product_provider_wallet')


class DeliveryBroker(Base):
    __tablename__ = 'delivery_broker'
    __table_args__ = (
        ForeignKeyConstraint(['delivery_broker_wallet_id'], ['wallet.id_wallet'], name='fk_delivery_broker_1'),
        Index('fk_delivery_broker_1_idx', 'delivery_broker_wallet_id')
    )

    id_delivery_broker = Column(Integer, primary_key=True)
    delivery_broker_name = Column(String(255))
    delivery_broker_label = Column(String(255))
    delivery_broker_logo_url = Column(String(255))
    delivery_broker_image_url = Column(String(255))
    delivery_broker_wallet_id = Column(Integer)

    delivery = relationship('Delivery', back_populates='delivery_broker')
    delivery_broker_wallet = relationship('Wallet', back_populates='delivery_broker')


class Deposit(Base):
    __tablename__ = 'deposit'
    __table_args__ = (
        ForeignKeyConstraint(['deposit_cart_id'], ['cart.cart_id'], ondelete='SET NULL', onupdate='CASCADE', name='deposit_ibfk_1'),
        ForeignKeyConstraint(['deposit_invoice_id'], ['invoice.invoice_id'], ondelete='SET NULL', onupdate='CASCADE', name='deposit_ibfk_2'),
        ForeignKeyConstraint(['deposit_receipt_id'], ['receipt.receipt_id'], name='fk_deposit_1'),
        Index('fk_deposit_1_idx', 'deposit_receipt_id'),
        Index('idx_cart', 'deposit_cart_id'),
        Index('idx_invoice', 'deposit_invoice_id')
    )

    deposit_id = Column(Integer, primary_key=True)
    deposit_amount = Column(DECIMAL(15, 4), nullable=False)
    deposit_method = Column(String(100), nullable=False)
    deposit_cart_id = Column(Integer)
    deposit_invoice_id = Column(Integer)
    deposit_reference = Column(String(255))
    deposit_notes = Column(Text)
    deposit_created_at = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
    deposit_updated_at = Column(TIMESTAMP)
    deposit_receipt_id = Column(Integer)

    deposit_cart = relationship('Cart', back_populates='deposit')
    deposit_invoice = relationship('Invoice', back_populates='deposit')
    deposit_receipt = relationship('Receipt', back_populates='deposit')


class Iproduct(Base):
    __tablename__ = 'iproduct'
    __table_args__ = (
        ForeignKeyConstraint(['iproduct_category_id'], ['product_category.id_product_category'], name='fk_iproduct_1'),
        Index('fk_iproduct_1_idx', 'iproduct_category_id')
    )

    id_iproduct = Column(Integer, primary_key=True)
    iproduct_barcode = Column(String(45))
    iproduct_brand = Column(String(255))
    iproduct_estimated_price = Column(DECIMAL(8, 2), server_default=text("'0.00'"))
    iproduct_price_currency = Column(String(45), server_default=text("'DZD'"))
    iproduct_gluten_status = Column(Enum('gluten_free', 'contains_gluten', 'may_contain_gluten', 'unknown'), server_default=text("'unknown'"))
    iproduct_info_source = Column(String(255))
    iproduct_last_price_update = Column(DateTime)
    iproduct_created_at = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
    iproduct_last_update = Column(TIMESTAMP)
    iproduct_model_name = Column(String(255))
    iproduct_image_url = Column(String(255))
    iproduct_name = Column(String(255))
    iproduct_info_confidence = Column(DECIMAL(5, 4))
    iproduct_category_id = Column(Integer)

    iproduct_category = relationship('ProductCategory', back_populates='iproduct')
    product = relationship('Product', back_populates='product_origin')


class MoneyTransaction(Base):
    __tablename__ = 'money_transaction'
    __table_args__ = (
        ForeignKeyConstraint(['money_transaction_wallet_destination_id'], ['wallet.id_wallet'], name='fk_money_transaction_2'),
        ForeignKeyConstraint(['money_transaction_wallet_source_id'], ['wallet.id_wallet'], name='fk_money_transaction_1'),
        Index('fk_money_transaction_1_idx', 'money_transaction_wallet_source_id'),
        Index('fk_money_transaction_2_idx', 'money_transaction_wallet_destination_id')
    )

    id_money_transaction = Column(Integer, primary_key=True)
    money_transaction_document_url = Column(String(255))
    money_transaction_amount = Column(Float(asdecimal=True), server_default=text("'0'"))
    money_transaction_reference = Column(String(255))
    money_transaction_creation = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
    money_transaction_last_updated = Column(TIMESTAMP)
    money_transaction_wallet_source_id = Column(Integer)
    money_transaction_wallet_destination_id = Column(Integer)
    money_transaction_status = Column(String(45))

    money_transaction_wallet_destination = relationship('Wallet', foreign_keys=[money_transaction_wallet_destination_id], back_populates='money_transaction')
    money_transaction_wallet_source = relationship('Wallet', foreign_keys=[money_transaction_wallet_source_id], back_populates='money_transaction_')


class ProviderOrganisation(Base):
    __tablename__ = 'provider_organisation'
    __table_args__ = (
        ForeignKeyConstraint(['provider_organisation_wallet_id'], ['wallet.id_wallet'], name='fk_provider_organisation_1'),
        Index('fk_provider_organisation_1_idx', 'provider_organisation_wallet_id')
    )

    idprovider_organisation = Column(Integer, primary_key=True)
    provider_organisation_name = Column(String(45))
    provider_organisation_desc = Column(String(300))
    provider_organisation_wallet_id = Column(Integer)

    provider_organisation_wallet = relationship('Wallet', back_populates='provider_organisation')
    organisation_image = relationship('OrganisationImage', back_populates='org_ref')
    product_provider = relationship('ProductProvider', back_populates='product_provider_org')
    conversation = relationship('Conversation', back_populates='conversation_org')
    management_rule = relationship('ManagementRule', back_populates='provider_organisation')
    service_contribution = relationship('ServiceContribution', back_populates='provider_organisation')


class LocationImage(Base):
    __tablename__ = 'location_image'
    __table_args__ = (
        ForeignKeyConstraint(['image_location_ref'], ['location.id_location'], name='fk_location_image_1'),
        Index('fk_location_image_1_idx', 'image_location_ref')
    )

    id_location_image = Column(Integer, primary_key=True)
    location_image_url = Column(String(255))
    image_location_ref = Column(Integer)

    location = relationship('Location', back_populates='location_image')


class OrganisationImage(Base):
    __tablename__ = 'organisation_image'
    __table_args__ = (
        ForeignKeyConstraint(['org_ref_id'], ['provider_organisation.idprovider_organisation'], name='fk_organisation_image_1'),
        Index('fk_organisation_image_1_idx', 'org_ref_id')
    )

    id_org_image = Column(Integer, primary_key=True)
    org_image_url = Column(String(255))
    org_ref_id = Column(Integer)

    org_ref = relationship('ProviderOrganisation', back_populates='organisation_image')


class Person(Base):
    __tablename__ = 'person'
    __table_args__ = (
        ForeignKeyConstraint(['person_blood_type_id'], ['blood_type.id_blood_type'], onupdate='RESTRICT', name='fk_person_2'),
        ForeignKeyConstraint(['person_details_id'], ['person_details.id_person_details'], name='fk_person_1'),
        ForeignKeyConstraint(['person_location_id'], ['location.id_location'], name='fk_person_3'),
        Index('fk_person_1_idx', 'person_details_id'),
        Index('fk_person_2_idx', 'person_blood_type_id'),
        Index('fk_person_3_idx', 'person_location_id')
    )

    id_person = Column(Integer, primary_key=True)
    person_details_id = Column(Integer)
    person_blood_type_id = Column(Integer)
    person_location_id = Column(Integer)

    cart = relationship('Cart', back_populates='person')
    person_blood_type = relationship('BloodType', back_populates='person')
    person_details = relationship('PersonDetails', back_populates='person')
    person_location = relationship('Location', back_populates='person')
    app_user = relationship('AppUser', back_populates='app_user_person')
    patient = relationship('Patient', back_populates='patient_person')
    service_contribution = relationship('ServiceContribution', back_populates='person')


class AppUser(Base):
    __tablename__ = 'app_user'
    __table_args__ = (
        ForeignKeyConstraint(['app_user_person_id'], ['person.id_person'], name='fk_app_user_3'),
        ForeignKeyConstraint(['app_user_subscription_ref'], ['plan.id_plan'], name='fk_app_user_2'),
        ForeignKeyConstraint(['app_user_type_id'], ['app_user_type.id_app_user_type'], ondelete='RESTRICT', onupdate='RESTRICT', name='fk_app_user_1'),
        ForeignKeyConstraint(['app_user_wallet_id'], ['wallet.id_wallet'], name='fk_app_user_4'),
        Index('fk_app_user_1_idx', 'app_user_type_id'),
        Index('fk_app_user_2_idx', 'app_user_subscription_ref'),
        Index('fk_app_user_3_idx', 'app_user_person_id'),
        Index('fk_app_user_4_idx', 'app_user_wallet_id')
    )

    id_app_user = Column(Integer, primary_key=True)
    app_user_name = Column(String(100))
    app_user_password = Column(String(256))
    app_user_person_id = Column(Integer)
    app_user_type_id = Column(Integer)
    app_user_preferences = Column(Text)
    app_user_image_url = Column(String(255))
    app_user_last_active = Column(TIMESTAMP)
    app_user_last_updated = Column(TIMESTAMP)
    app_user_creation = Column(TIMESTAMP)
    app_user_subscription_ref = Column(Integer)
    app_user_email = Column(String(255))
    app_user_wallet_id = Column(Integer)

    cart = relationship('Cart', foreign_keys='[Cart.cart_client_user]', back_populates='app_user')
    cart_ = relationship('Cart', foreign_keys='[Cart.cart_selling_user]', back_populates='app_user_')
    placed_order = relationship('PlacedOrder', back_populates='ordering_user')
    app_user_person = relationship('Person', back_populates='app_user')
    plan = relationship('Plan', back_populates='app_user')
    app_user_type = relationship('AppUserType', back_populates='app_user')
    app_user_wallet = relationship('Wallet', back_populates='app_user')
    comment = relationship('Comment', back_populates='app_user')
    notification = relationship('Notification', back_populates='app_user')
    product_provider = relationship('ProductProvider', back_populates='app_user')
    recipe = relationship('Recipe', back_populates='recipe_owner')
    report = relationship('Report', back_populates='app_user')
    additional_fee = relationship('AdditionalFee', back_populates='additional_fee_user')
    comment_reaction = relationship('CommentReaction', back_populates='app_user')
    conversation = relationship('Conversation', foreign_keys='[Conversation.conversation_destination_user_id]', back_populates='conversation_destination_user')
    conversation_ = relationship('Conversation', foreign_keys='[Conversation.conversation_sender_user_id]', back_populates='conversation_sender_user')
    management_rule = relationship('ManagementRule', back_populates='app_user')
    product = relationship('Product', back_populates='app_user')
    provider_reaction = relationship('ProviderReaction', back_populates='app_user')
    recipe_reaction = relationship('RecipeReaction', back_populates='app_user')
    product_reaction = relationship('ProductReaction', back_populates='app_user')
    service_contribution = relationship('ServiceContribution', back_populates='app_user')


class Patient(Base):
    __tablename__ = 'patient'
    __table_args__ = (
        ForeignKeyConstraint(['patient_disease_severity_id'], ['disease_severity.id_disease_severity'], name='fk_patient_2'),
        ForeignKeyConstraint(['patient_person_id'], ['person.id_person'], name='fk_patient_1'),
        Index('fk_patient_1_idx', 'patient_person_id'),
        Index('fk_patient_2_idx', 'patient_disease_severity_id')
    )

    id_patient = Column(Integer, primary_key=True)
    patient_person_id = Column(Integer)
    patient_disease_severity_id = Column(Integer)

    patient_disease_severity = relationship('DiseaseSeverity', back_populates='patient')
    patient_person = relationship('Person', back_populates='patient')
    serology = relationship('Serology', back_populates='patient')
    symptoms_occurence = relationship('SymptomsOccurence', back_populates='patient')


class Comment(Base):
    __tablename__ = 'comment'
    __table_args__ = (
        ForeignKeyConstraint(['comment_owner'], ['app_user.id_app_user'], name='fk_comment_2'),
        ForeignKeyConstraint(['replying_to'], ['comment.idcomment'], name='fk_comment_1'),
        Index('fk_comment_1_idx', 'replying_to'),
        Index('fk_comment_2_idx', 'comment_owner')
    )

    idcomment = Column(Integer, primary_key=True)
    comment_owner = Column(Integer)
    comment_content = Column(Text)
    replying_to = Column(Integer)
    comment_creation = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
    comment_visibility = Column(TINYINT)
    comment_edition = Column(TIMESTAMP)

    app_user = relationship('AppUser', back_populates='comment')
    comment = relationship('Comment', remote_side=[idcomment], back_populates='comment_reverse')
    comment_reverse = relationship('Comment', remote_side=[replying_to], back_populates='comment')
    comment_reaction = relationship('CommentReaction', back_populates='comment')


class Notification(Base):
    __tablename__ = 'notification'
    __table_args__ = (
        ForeignKeyConstraint(['notification_user_ref'], ['app_user.id_app_user'], name='fk_notification_1'),
        Index('fk_notification_1_idx', 'notification_user_ref')
    )

    id_notification = Column(Integer, primary_key=True)
    notification_code = Column(String(255))
    notification_params = Column(Text)
    notification_user_ref = Column(Integer)
    notification_created_at = Column(DateTime)
    notification_read_at = Column(DateTime)

    app_user = relationship('AppUser', back_populates='notification')


class ProductProvider(Base):
    __tablename__ = 'product_provider'
    __table_args__ = (
        ForeignKeyConstraint(['product_provider_details_id'], ['provider_details.idprovider_details_id'], ondelete='RESTRICT', onupdate='RESTRICT', name='fk_product_provider_3'),
        ForeignKeyConstraint(['product_provider_location_id'], ['location.id_location'], name='fk_product_provider_4'),
        ForeignKeyConstraint(['product_provider_org_id'], ['provider_organisation.idprovider_organisation'], ondelete='RESTRICT', onupdate='RESTRICT', name='fk_product_provider_2'),
        ForeignKeyConstraint(['product_provider_owner'], ['app_user.id_app_user'], name='fk_product_provider_5'),
        ForeignKeyConstraint(['product_provider_type_id'], ['product_provider_type.id_product_provider_type'], ondelete='RESTRICT', onupdate='RESTRICT', name='fk_product_provider_1'),
        ForeignKeyConstraint(['product_provider_wallet_id'], ['wallet.id_wallet'], name='fk_product_provider_6'),
        Index('fk_product_provider_1_idx', 'product_provider_type_id'),
        Index('fk_product_provider_2_idx', 'product_provider_org_id'),
        Index('fk_product_provider_3_idx', 'product_provider_details_id'),
        Index('fk_product_provider_4_idx', 'product_provider_location_id'),
        Index('fk_product_provider_5_idx', 'product_provider_owner'),
        Index('fk_product_provider_6_idx', 'product_provider_wallet_id')
    )

    id_product_provider = Column(Integer, primary_key=True)
    product_provider_details_id = Column(Integer)
    product_provider_type_id = Column(Integer)
    product_provider_location_id = Column(Integer)
    product_provider_org_id = Column(Integer)
    product_provider_owner = Column(Integer)
    product_provider_wallet_id = Column(Integer)

    cart = relationship('Cart', back_populates='cart_product_provider')
    delivery = relationship('Delivery', back_populates='delivery_provider')
    product_provider_details = relationship('ProviderDetails', back_populates='product_provider')
    product_provider_location = relationship('Location', back_populates='product_provider')
    product_provider_org = relationship('ProviderOrganisation', back_populates='product_provider')
    app_user = relationship('AppUser', back_populates='product_provider')
    product_provider_type = relationship('ProductProviderType', back_populates='product_provider')
    product_provider_wallet = relationship('Wallet', back_populates='product_provider')
    additional_fee = relationship('AdditionalFee', back_populates='additional_fee_on_provider')
    conversation = relationship('Conversation', back_populates='conversation_provider')
    management_rule = relationship('ManagementRule', back_populates='product_provider')
    product = relationship('Product', back_populates='product_provider')
    provided_service = relationship('ProvidedService', back_populates='provided_service_product_provider')
    provider_image = relationship('ProviderImage', back_populates='provider_ref')
    provider_reaction = relationship('ProviderReaction', back_populates='product_provider')
    service_package = relationship('ServicePackage', back_populates='service_package_product_provider')
    service_contribution = relationship('ServiceContribution', back_populates='product_provider')


class Recipe(Base):
    __tablename__ = 'recipe'
    __table_args__ = (
        ForeignKeyConstraint(['recipe_category_id'], ['recipe_category.id_recipe_category'], name='fk_recipe_2'),
        ForeignKeyConstraint(['recipe_owner_id'], ['app_user.id_app_user'], name='fk_recipe_1'),
        Index('fk_recipe_1_idx', 'recipe_owner_id'),
        Index('fk_recipe_2_idx', 'recipe_category_id')
    )

    id_recipe = Column(Integer, primary_key=True)
    recipe_owner_id = Column(Integer)
    recipe_category_id = Column(Integer)
    recipe_preparation_time = Column(String(45))
    recipe_instructions = Column(Text)
    recipe_name = Column(String(45))
    recipe_description = Column(String(300))
    recipe_creation = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
    recipe_last_updated = Column(TIMESTAMP)

    recipe_category = relationship('RecipeCategory', back_populates='recipe')
    recipe_owner = relationship('AppUser', back_populates='recipe')
    recipe_contains_ingredient = relationship('RecipeContainsIngredient', back_populates='containing_recipe')
    recipe_image = relationship('RecipeImage', back_populates='recipe_ref')
    recipe_reaction = relationship('RecipeReaction', back_populates='recipe')


class Report(Base):
    __tablename__ = 'report'
    __table_args__ = (
        ForeignKeyConstraint(['report_owner'], ['app_user.id_app_user'], name='fk_report_1'),
        Index('fk_report_1_idx', 'report_owner')
    )

    id_report = Column(Integer, primary_key=True)
    report_text = Column(Text)
    report_owner = Column(Integer)

    app_user = relationship('AppUser', back_populates='report')


class Serology(Base):
    __tablename__ = 'serology'
    __table_args__ = (
        ForeignKeyConstraint(['indicator_id'], ['serology_indicator.id_serology_indicator'], name='fk_serology_1'),
        ForeignKeyConstraint(['patient_id'], ['patient.id_patient'], name='fk_diagnosis_1'),
        Index('fk_diagnosis_1_idx', 'patient_id'),
        Index('fk_serology_1_idx', 'indicator_id')
    )

    id_serology = Column(Integer, primary_key=True)
    indicator_id = Column(Integer)
    serology_date = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
    patient_id = Column(Integer)
    indicator_value = Column(String(45))

    indicator = relationship('SerologyIndicator', back_populates='serology')
    patient = relationship('Patient', back_populates='serology')


class SymptomsOccurence(Base):
    __tablename__ = 'symptoms_occurence'
    __table_args__ = (
        ForeignKeyConstraint(['symptoms_occurence_ref_patient'], ['patient.id_patient'], name='fk_symptoms_causality_1'),
        Index('fk_symptoms_causality_1_idx', 'symptoms_occurence_ref_patient')
    )

    id_symptoms_occurence = Column(Integer, primary_key=True)
    symptoms_occurence_submission_time = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
    symptoms_occurence_reason = Column(String(300))
    reason_date = Column(TIMESTAMP)
    symptoms_occurence_ref_patient = Column(Integer)

    patient = relationship('Patient', back_populates='symptoms_occurence')
    presented_symptom = relationship('PresentedSymptom', back_populates='symptoms_occurence')


class AdditionalFee(Base):
    __tablename__ = 'additional_fee'
    __table_args__ = (
        ForeignKeyConstraint(['additional_fee_on_provider_id'], ['product_provider.id_product_provider'], name='fk_additional_fee_2'),
        ForeignKeyConstraint(['additional_fee_payment_id'], ['payment.payment_id'], ondelete='CASCADE', onupdate='CASCADE', name='additional_fee_ibfk_1'),
        ForeignKeyConstraint(['additional_fee_user_id'], ['app_user.id_app_user'], name='fk_additional_fee_1'),
        Index('fk_additional_fee_1_idx', 'additional_fee_user_id'),
        Index('fk_additional_fee_2_idx', 'additional_fee_on_provider_id'),
        Index('idx_payment', 'additional_fee_payment_id')
    )

    additional_fee_id = Column(Integer, primary_key=True)
    additional_fee_payment_id = Column(Integer)
    additional_fee_name = Column(String(255))
    additional_fee_amount = Column(DECIMAL(15, 4))
    additional_fee_description = Column(Text)
    additional_fee_created_at = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
    additional_fee_updated_at = Column(TIMESTAMP)
    additional_fee_document_url = Column(String(255))
    additional_fee_user_id = Column(Integer)
    additional_fee_on_provider_id = Column(Integer)

    additional_fee_on_provider = relationship('ProductProvider', back_populates='additional_fee')
    additional_fee_payment = relationship('Payment', back_populates='additional_fee')
    additional_fee_user = relationship('AppUser', back_populates='additional_fee')


class CommentReaction(Base):
    __tablename__ = 'comment_reaction'
    __table_args__ = (
        ForeignKeyConstraint(['comment_reacting_user'], ['app_user.id_app_user'], name='fk_product_reaction_11'),
        ForeignKeyConstraint(['comment_reaction_ref'], ['reaction.id_reaction'], name='fk_product_reaction_21'),
        ForeignKeyConstraint(['reacted_on_comment'], ['comment.idcomment'], name='fk_product_reaction_30'),
        Index('fk_product_reaction_1_idx', 'comment_reacting_user'),
        Index('fk_product_reaction_2_idx', 'comment_reaction_ref'),
        Index('fk_product_reaction_30_idx', 'reacted_on_comment')
    )

    id_comment_reaction = Column(Integer, primary_key=True)
    comment_reacting_user = Column(Integer)
    comment_reaction_ref = Column(Integer)
    reacted_on_comment = Column(Integer)

    app_user = relationship('AppUser', back_populates='comment_reaction')
    reaction = relationship('Reaction', back_populates='comment_reaction')
    comment = relationship('Comment', back_populates='comment_reaction')


class Conversation(Base):
    __tablename__ = 'conversation'
    __table_args__ = (
        ForeignKeyConstraint(['conversation_destination_user_id'], ['app_user.id_app_user'], name='fk_message_2'),
        ForeignKeyConstraint(['conversation_org_id'], ['provider_organisation.idprovider_organisation'], name='fk_message_4'),
        ForeignKeyConstraint(['conversation_provider_id'], ['product_provider.id_product_provider'], name='fk_message_3'),
        ForeignKeyConstraint(['conversation_sender_user_id'], ['app_user.id_app_user'], name='fk_message_1'),
        Index('fk_message_1_idx', 'conversation_sender_user_id'),
        Index('fk_message_2_idx', 'conversation_destination_user_id'),
        Index('fk_message_3_idx', 'conversation_provider_id'),
        Index('fk_message_4_idx', 'conversation_org_id')
    )

    id_conversation = Column(Integer, primary_key=True)
    conversation_created_at = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
    conversation_org_id = Column(Integer)
    conversation_provider_id = Column(Integer)
    conversation_sender_user_id = Column(Integer)
    conversation_destination_user_id = Column(Integer)

    conversation_destination_user = relationship('AppUser', foreign_keys=[conversation_destination_user_id], back_populates='conversation')
    conversation_org = relationship('ProviderOrganisation', back_populates='conversation')
    conversation_provider = relationship('ProductProvider', back_populates='conversation')
    conversation_sender_user = relationship('AppUser', foreign_keys=[conversation_sender_user_id], back_populates='conversation_')


class ManagementRule(Base):
    __tablename__ = 'management_rule'
    __table_args__ = (
        ForeignKeyConstraint(['rule_ref_org'], ['provider_organisation.idprovider_organisation'], name='fk_management_rule_1'),
        ForeignKeyConstraint(['rule_ref_provider'], ['product_provider.id_product_provider'], name='fk_management_rule_2'),
        ForeignKeyConstraint(['rule_ref_user'], ['app_user.id_app_user'], ondelete='RESTRICT', onupdate='RESTRICT', name='fk_management_rule_3'),
        Index('fk_management_rule_1_idx', 'rule_ref_org'),
        Index('fk_management_rule_2_idx', 'rule_ref_provider'),
        Index('fk_management_rule_3_idx', 'rule_ref_user')
    )

    id_management_rule = Column(Integer, primary_key=True)
    rule_ref_org = Column(Integer)
    rule_ref_provider = Column(Integer)
    rule_ref_user = Column(Integer)
    management_rule_code = Column(Integer)
    management_rule_status = Column(Enum('PENDING', 'REJECTED', 'SUSPENDED', 'OBSOLETE', 'ACTIVE'), server_default=text("'PENDING'"))
    management_rule_expiry = Column(DateTime)

    provider_organisation = relationship('ProviderOrganisation', back_populates='management_rule')
    product_provider = relationship('ProductProvider', back_populates='management_rule')
    app_user = relationship('AppUser', back_populates='management_rule')


class PresentedSymptom(Base):
    __tablename__ = 'presented_symptom'
    __table_args__ = (
        ForeignKeyConstraint(['presented_symptom_ref_symptom'], ['symptom.id_symptom'], name='fk_presented_symptom_1'),
        ForeignKeyConstraint(['presented_symptom_ref_symptoms_occurence'], ['symptoms_occurence.id_symptoms_occurence'], name='fk_presented_symptom_2'),
        Index('fk_presented_symptom_1_idx', 'presented_symptom_ref_symptom'),
        Index('fk_presented_symptom_2_idx', 'presented_symptom_ref_symptoms_occurence')
    )

    id_presented_symptom = Column(Integer, primary_key=True)
    presented_symptom_ref_symptoms_occurence = Column(Integer)
    presented_symptom_ref_symptom = Column(Integer)

    symptom = relationship('Symptom', back_populates='presented_symptom')
    symptoms_occurence = relationship('SymptomsOccurence', back_populates='presented_symptom')


class Product(Base):
    __tablename__ = 'product'
    __table_args__ = (
        ForeignKeyConstraint(['product_category_id'], ['product_category.id_product_category'], name='fk_product_2'),
        ForeignKeyConstraint(['product_origin_id'], ['iproduct.id_iproduct'], name='fk_product_4'),
        ForeignKeyConstraint(['product_owner'], ['app_user.id_app_user'], ondelete='RESTRICT', onupdate='RESTRICT', name='fk_product_3'),
        ForeignKeyConstraint(['product_provider_id'], ['product_provider.id_product_provider'], name='fk_product_1'),
        Index('fk_product_1_idx', 'product_provider_id'),
        Index('fk_product_2_idx', 'product_category_id'),
        Index('fk_product_3_idx', 'product_owner'),
        Index('fk_product_4_idx', 'product_origin_id')
    )

    id_product = Column(Integer, primary_key=True)
    product_name = Column(String(45))
    product_brand = Column(String(45))
    product_provider_id = Column(Integer)
    product_category_id = Column(Integer)
    product_barcode = Column(String(45))
    last_updated = Column(DateTime)
    created = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
    product_description = Column(String(300))
    product_price = Column(Float(asdecimal=True))
    product_quantity = Column(Integer)
    product_quantifier = Column(String(45))
    product_owner = Column(Integer)
    product_origin_id = Column(Integer)

    product_category = relationship('ProductCategory', back_populates='product')
    product_origin = relationship('Iproduct', back_populates='product')
    app_user = relationship('AppUser', back_populates='product')
    product_provider = relationship('ProductProvider', back_populates='product')
    ordered_item = relationship('OrderedItem', back_populates='ordered_product')
    product_image = relationship('ProductImage', back_populates='product_ref')
    product_reaction = relationship('ProductReaction', back_populates='product')
    service_resource_requirement = relationship('ServiceResourceRequirement', back_populates='product')


class ProvidedService(Base):
    __tablename__ = 'provided_service'
    __table_args__ = (
        ForeignKeyConstraint(['provided_service_category_id'], ['provided_service_category.provided_service_category_id'], ondelete='RESTRICT', onupdate='CASCADE', name='provided_service_ibfk_1'),
        ForeignKeyConstraint(['provided_service_product_provider_id'], ['product_provider.id_product_provider'], ondelete='RESTRICT', onupdate='CASCADE', name='provided_service_ibfk_2'),
        Index('idx_provided_service_active', 'provided_service_is_active', 'provided_service_deleted_at'),
        Index('idx_provided_service_category', 'provided_service_category_id'),
        Index('idx_provided_service_created_at', 'provided_service_created_at'),
        Index('idx_provided_service_name', 'provided_service_name'),
        Index('idx_provided_service_price_range', 'provided_service_base_price', 'provided_service_final_price'),
        Index('idx_provided_service_provider', 'provided_service_product_provider_id')
    )

    provided_service_id = Column(Integer, primary_key=True)
    provided_service_name = Column(String(255))
    provided_service_description = Column(Text)
    provided_service_category_id = Column(Integer)
    provided_service_product_provider_id = Column(Integer, comment='References i_product_provider.id_product_provider')
    provided_service_base_price = Column(DECIMAL(15, 4))
    provided_service_final_price = Column(DECIMAL(15, 4))
    provided_service_actual_duration = Column(DECIMAL(10, 2))
    provided_service_is_active = Column(TINYINT(1), server_default=text("'1'"))
    provided_service_pricing_config = Column(JSON)
    provided_service_created_at = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
    provided_service_updated_at = Column(TIMESTAMP)
    provided_service_deleted_at = Column(TIMESTAMP)

    provided_service_category = relationship('ProvidedServiceCategory', back_populates='provided_service')
    provided_service_product_provider = relationship('ProductProvider', back_populates='provided_service')
    ordered_service = relationship('OrderedService', back_populates='ordered_service_service')
    service_contribution = relationship('ServiceContribution', back_populates='provided_service')
    service_package_item = relationship('ServicePackageItem', back_populates='service_package_item_service')
    service_resource_requirement = relationship('ServiceResourceRequirement', back_populates='service_resource_requirement_service')
    service_staff_requirement = relationship('ServiceStaffRequirement', back_populates='service_staff_requirement_service')


class ProviderImage(Base):
    __tablename__ = 'provider_image'
    __table_args__ = (
        ForeignKeyConstraint(['provider_ref_id'], ['product_provider.id_product_provider'], name='fk_provider_image_1'),
        Index('fk_provider_image_1_idx', 'provider_ref_id')
    )

    id_provider_image = Column(Integer, primary_key=True)
    provider_image_url = Column(String(255))
    provider_ref_id = Column(Integer)

    provider_ref = relationship('ProductProvider', back_populates='provider_image')


class ProviderReaction(Base):
    __tablename__ = 'provider_reaction'
    __table_args__ = (
        ForeignKeyConstraint(['product_reacting_user'], ['app_user.id_app_user'], name='fk_product_reaction_12'),
        ForeignKeyConstraint(['product_reaction_ref'], ['reaction.id_reaction'], name='fk_product_reaction_22'),
        ForeignKeyConstraint(['reacted_on_provider'], ['product_provider.id_product_provider'], name='fk_product_reaction_31'),
        Index('fk_product_reaction_1_idx', 'product_reacting_user'),
        Index('fk_product_reaction_2_idx', 'product_reaction_ref'),
        Index('fk_product_reaction_31_idx', 'reacted_on_provider')
    )

    id_product_reaction = Column(Integer, primary_key=True)
    product_reacting_user = Column(Integer)
    product_reaction_ref = Column(Integer)
    reacted_on_provider = Column(Integer)
    provider_reaction_value = Column(Float, server_default=text("'0'"))

    app_user = relationship('AppUser', back_populates='provider_reaction')
    reaction = relationship('Reaction', back_populates='provider_reaction')
    product_provider = relationship('ProductProvider', back_populates='provider_reaction')


class RecipeContainsIngredient(Base):
    __tablename__ = 'recipe_contains_ingredient'
    __table_args__ = (
        ForeignKeyConstraint(['contained_ingredient_id'], ['ingredient.id_ingredient'], name='fk_recipe_contains_ingredient_2'),
        ForeignKeyConstraint(['containing_recipe_id'], ['recipe.id_recipe'], ondelete='RESTRICT', onupdate='RESTRICT', name='fk_recipe_contains_ingredient_1'),
        Index('fk_recipe_contains_ingredient_1_idx', 'containing_recipe_id'),
        Index('fk_recipe_contains_ingredient_2_idx', 'contained_ingredient_id')
    )

    idrecipe_contains_ingredient_id = Column(Integer, primary_key=True)
    containing_recipe_id = Column(Integer)
    contained_ingredient_id = Column(Integer)
    contained_quantity = Column(String(45))

    contained_ingredient = relationship('Ingredient', back_populates='recipe_contains_ingredient')
    containing_recipe = relationship('Recipe', back_populates='recipe_contains_ingredient')


class RecipeImage(Base):
    __tablename__ = 'recipe_image'
    __table_args__ = (
        ForeignKeyConstraint(['recipe_ref_id'], ['recipe.id_recipe'], name='fk_recipe_image_1'),
        Index('fk_recipe_image_1_idx', 'recipe_ref_id')
    )

    id_recipe_image = Column(Integer, primary_key=True)
    recipe_image_url = Column(String(255))
    recipe_ref_id = Column(Integer)

    recipe_ref = relationship('Recipe', back_populates='recipe_image')


class RecipeReaction(Base):
    __tablename__ = 'recipe_reaction'
    __table_args__ = (
        ForeignKeyConstraint(['reacted_on_recipe'], ['recipe.id_recipe'], name='fk_recipe_reaction_1'),
        ForeignKeyConstraint(['recipe_reacting_user'], ['app_user.id_app_user'], name='fk_product_reaction_10'),
        ForeignKeyConstraint(['recipe_reaction_ref'], ['reaction.id_reaction'], name='fk_product_reaction_20'),
        Index('fk_product_reaction_1_idx', 'recipe_reacting_user'),
        Index('fk_product_reaction_2_idx', 'recipe_reaction_ref'),
        Index('fk_recipe_reaction_1_idx', 'reacted_on_recipe')
    )

    id_recipe_reaction = Column(Integer, primary_key=True)
    recipe_reacting_user = Column(Integer)
    recipe_reaction_ref = Column(Integer)
    reacted_on_recipe = Column(Integer)

    recipe = relationship('Recipe', back_populates='recipe_reaction')
    app_user = relationship('AppUser', back_populates='recipe_reaction')
    reaction = relationship('Reaction', back_populates='recipe_reaction')


class ServicePackage(Base):
    __tablename__ = 'service_package'
    __table_args__ = (
        ForeignKeyConstraint(['service_package_product_provider_id'], ['product_provider.id_product_provider'], ondelete='RESTRICT', onupdate='CASCADE', name='service_package_ibfk_1'),
        Index('idx_service_package_active', 'service_package_is_active'),
        Index('idx_service_package_provider', 'service_package_product_provider_id'),
        Index('idx_service_package_validity', 'service_package_valid_from', 'service_package_valid_to')
    )

    service_package_id = Column(Integer, primary_key=True)
    service_package_name = Column(String(255))
    service_package_description = Column(Text)
    service_package_product_provider_id = Column(Integer)
    service_package_price = Column(DECIMAL(15, 4))
    service_package_discount_percentage = Column(DECIMAL(5, 2))
    service_package_is_active = Column(TINYINT(1), server_default=text("'1'"))
    service_package_valid_from = Column(Date)
    service_package_valid_to = Column(Date)
    service_package_created_at = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
    service_package_updated_at = Column(TIMESTAMP)

    service_package_product_provider = relationship('ProductProvider', back_populates='service_package')
    service_package_item = relationship('ServicePackageItem', back_populates='service_package_item_package')


class OrderedItem(Base):
    __tablename__ = 'ordered_item'
    __table_args__ = (
        ForeignKeyConstraint(['order_ref'], ['placed_order.id_placed_order'], name='fk_ordered_item_3'),
        ForeignKeyConstraint(['ordered_item_cart_ref'], ['cart.cart_id'], name='fk_ordered_item_2'),
        ForeignKeyConstraint(['ordered_product_id'], ['product.id_product'], ondelete='RESTRICT', onupdate='RESTRICT', name='fk_ordered_item_1'),
        Index('fk_ordered_item_1_idx', 'ordered_product_id'),
        Index('fk_ordered_item_2_idx', 'ordered_item_cart_ref'),
        Index('fk_ordered_item_3_idx', 'order_ref')
    )

    id_ordered_item = Column(Integer, primary_key=True)
    ordered_product_id = Column(Integer)
    ordered_quantity = Column(Integer)
    applied_vat = Column(Float(asdecimal=True))
    order_ref = Column(Integer)
    unit_price = Column(Float(asdecimal=True))
    product_discount = Column(Float(asdecimal=True))
    ordered_item_cart_ref = Column(Integer)
    ordered_item_delivery_status = Column(String(45))
    ordered_item_delivery_fee = Column(Float(asdecimal=True), server_default=text("'0'"))

    placed_order = relationship('PlacedOrder', back_populates='ordered_item')
    cart = relationship('Cart', back_populates='ordered_item')
    ordered_product = relationship('Product', back_populates='ordered_item')


class OrderedService(Base):
    __tablename__ = 'ordered_service'
    __table_args__ = (
        ForeignKeyConstraint(['ordered_service_cart_id'], ['cart.cart_id'], ondelete='CASCADE', onupdate='CASCADE', name='ordered_service_ibfk_1'),
        ForeignKeyConstraint(['ordered_service_location_id'], ['location.id_location'], name='fk_ordered_service_1'),
        ForeignKeyConstraint(['ordered_service_service_id'], ['provided_service.provided_service_id'], ondelete='RESTRICT', onupdate='CASCADE', name='ordered_service_ibfk_2'),
        Index('fk_ordered_service_1_idx', 'ordered_service_location_id'),
        Index('idx_cart', 'ordered_service_cart_id'),
        Index('idx_service', 'ordered_service_service_id')
    )

    ordered_service_id = Column(Integer, primary_key=True)
    ordered_service_cart_id = Column(Integer)
    ordered_service_service_id = Column(Integer, comment='References provided_service')
    ordered_service_quantity = Column(Integer, server_default=text("'1'"))
    ordered_service_unit_price = Column(DECIMAL(15, 4))
    ordered_service_total_price = Column(DECIMAL(15, 4))
    ordered_service_notes = Column(Text)
    ordered_service_created_at = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
    ordered_service_updated_at = Column(TIMESTAMP)
    ordered_service_scheduled_at = Column(TIMESTAMP)
    ordered_service_location_id = Column(Integer)
    ordered_service_delivery_fee = Column(Float(asdecimal=True), server_default=text("'0'"))
    ordered_service_delivery_status = Column(String(45))

    ordered_service_cart = relationship('Cart', back_populates='ordered_service')
    ordered_service_location = relationship('Location', back_populates='ordered_service')
    ordered_service_service = relationship('ProvidedService', back_populates='ordered_service')


class ProductImage(Base):
    __tablename__ = 'product_image'
    __table_args__ = (
        ForeignKeyConstraint(['product_ref_id'], ['product.id_product'], name='fk_product_image_1'),
        Index('fk_product_image_1_idx', 'product_ref_id')
    )

    id_product_image = Column(Integer, primary_key=True)
    product_image_url = Column(String(255))
    product_ref_id = Column(Integer)

    product_ref = relationship('Product', back_populates='product_image')


class ProductReaction(Base):
    __tablename__ = 'product_reaction'
    __table_args__ = (
        ForeignKeyConstraint(['product_reacting_user'], ['app_user.id_app_user'], name='fk_product_reaction_1'),
        ForeignKeyConstraint(['product_reaction_ref'], ['reaction.id_reaction'], name='fk_product_reaction_2'),
        ForeignKeyConstraint(['reacted_on_product'], ['product.id_product'], name='fk_product_reaction_3'),
        Index('fk_product_reaction_1_idx', 'product_reacting_user'),
        Index('fk_product_reaction_2_idx', 'product_reaction_ref'),
        Index('fk_product_reaction_3_idx', 'reacted_on_product')
    )

    id_product_reaction = Column(Integer, primary_key=True)
    product_reacting_user = Column(Integer)
    product_reaction_ref = Column(Integer)
    reacted_on_product = Column(Integer)
    product_reaction_value = Column(Float, server_default=text("'0'"))

    app_user = relationship('AppUser', back_populates='product_reaction')
    reaction = relationship('Reaction', back_populates='product_reaction')
    product = relationship('Product', back_populates='product_reaction')


class ServiceContribution(Base):
    __tablename__ = 'service_contribution'
    __table_args__ = (
        ForeignKeyConstraint(['service_contribution_org_ref'], ['provider_organisation.idprovider_organisation'], name='fk_service_contribution_2'),
        ForeignKeyConstraint(['service_contribution_person_ref'], ['person.id_person'], name='fk_service_contribution_4'),
        ForeignKeyConstraint(['service_contribution_provider_ref'], ['product_provider.id_product_provider'], name='fk_service_contribution_6'),
        ForeignKeyConstraint(['service_contribution_user_ref'], ['app_user.id_app_user'], name='fk_service_contribution_3'),
        ForeignKeyConstraint(['service_ref'], ['provided_service.provided_service_id'], name='fk_service_contribution_5'),
        Index('fk_service_contribution_2_idx', 'service_contribution_org_ref'),
        Index('fk_service_contribution_3_idx', 'service_contribution_user_ref'),
        Index('fk_service_contribution_4_idx', 'service_contribution_person_ref'),
        Index('fk_service_contribution_5_idx', 'service_ref'),
        Index('fk_service_contribution_6_idx', 'service_contribution_provider_ref')
    )

    id_service_contribution = Column(Integer, primary_key=True)
    service_contribution_duration = Column(String(45))
    service_contribution_price = Column(Float)
    service_contribution_currency = Column(String(45))
    service_contribution_org_ref = Column(Integer)
    service_contribution_user_ref = Column(Integer)
    service_contribution_person_ref = Column(Integer)
    service_ref = Column(Integer)
    service_contribution_start = Column(TIMESTAMP)
    service_contribution_provider_ref = Column(Integer)

    provider_organisation = relationship('ProviderOrganisation', back_populates='service_contribution')
    person = relationship('Person', back_populates='service_contribution')
    product_provider = relationship('ProductProvider', back_populates='service_contribution')
    app_user = relationship('AppUser', back_populates='service_contribution')
    provided_service = relationship('ProvidedService', back_populates='service_contribution')


class ServicePackageItem(Base):
    __tablename__ = 'service_package_item'
    __table_args__ = (
        ForeignKeyConstraint(['service_package_item_package_id'], ['service_package.service_package_id'], ondelete='CASCADE', onupdate='CASCADE', name='service_package_item_ibfk_1'),
        ForeignKeyConstraint(['service_package_item_service_id'], ['provided_service.provided_service_id'], ondelete='CASCADE', onupdate='CASCADE', name='service_package_item_ibfk_2'),
        Index('idx_service_package_item_service', 'service_package_item_service_id'),
        Index('uk_package_service', 'service_package_item_package_id', 'service_package_item_service_id', unique=True)
    )

    service_package_item_id = Column(Integer, primary_key=True)
    service_package_item_package_id = Column(Integer)
    service_package_item_service_id = Column(Integer)
    service_package_item_sequence_order = Column(Integer, server_default=text("'1'"))
    service_package_item_quantity = Column(Integer, server_default=text("'1'"))
    service_package_item_notes = Column(Text)

    service_package_item_package = relationship('ServicePackage', back_populates='service_package_item')
    service_package_item_service = relationship('ProvidedService', back_populates='service_package_item')


class ServiceResourceRequirement(Base):
    __tablename__ = 'service_resource_requirement'
    __table_args__ = (
        ForeignKeyConstraint(['service_resource_requirement_product_ref'], ['product.id_product'], name='fk_service_resource_requirement_1'),
        ForeignKeyConstraint(['service_resource_requirement_service_id'], ['provided_service.provided_service_id'], ondelete='CASCADE', onupdate='CASCADE', name='service_resource_requirement_ibfk_1'),
        Index('fk_service_resource_requirement_1_idx', 'service_resource_requirement_product_ref'),
        Index('idx_resource_requirement_name', 'service_resource_requirement_name'),
        Index('idx_resource_requirement_service', 'service_resource_requirement_service_id'),
        Index('idx_resource_requirement_type', 'service_resource_requirement_type')
    )

    service_resource_requirement_id = Column(Integer, primary_key=True)
    service_resource_requirement_service_id = Column(Integer)
    service_resource_requirement_name = Column(String(255))
    service_resource_requirement_type = Column(String(100))
    service_resource_requirement_quantity = Column(Integer, server_default=text("'1'"))
    service_resource_requirement_cost_per_unit = Column(DECIMAL(15, 4))
    service_resource_requirement_is_consumable = Column(TINYINT(1), server_default=text("'0'"))
    service_resource_requirement_notes = Column(Text)
    service_resource_requirement_created_at = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
    service_resource_requirement_updated_at = Column(TIMESTAMP)
    service_resource_requirement_product_ref = Column(Integer)

    product = relationship('Product', back_populates='service_resource_requirement')
    service_resource_requirement_service = relationship('ProvidedService', back_populates='service_resource_requirement')


class ServiceStaffRequirement(Base):
    __tablename__ = 'service_staff_requirement'
    __table_args__ = (
        ForeignKeyConstraint(['service_staff_requirement_service_id'], ['provided_service.provided_service_id'], ondelete='CASCADE', onupdate='CASCADE', name='service_staff_requirement_ibfk_1'),
        Index('idx_service_staff_requirement_role', 'service_staff_requirement_role'),
        Index('idx_service_staff_requirement_service', 'service_staff_requirement_service_id')
    )

    service_staff_requirement_id = Column(Integer, primary_key=True)
    service_staff_requirement_service_id = Column(Integer)
    service_staff_requirement_role = Column(String(100))
    service_staff_requirement_min_count = Column(Integer, server_default=text("'1'"))
    service_staff_requirement_max_count = Column(Integer)
    service_staff_requirement_hourly_rate = Column(DECIMAL(15, 4))
    service_staff_requirement_allocated_hours = Column(DECIMAL(5, 2))
    service_staff_requirement_notes = Column(Text)
    service_staff_requirement_created_at = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
    service_staff_requirement_updated_at = Column(TIMESTAMP)

    service_staff_requirement_service = relationship('ProvidedService', back_populates='service_staff_requirement')
