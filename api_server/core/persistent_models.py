"""
This file is destined to keep the sensitive models away from 
sqlacodegen's instruction of 





"""



from sqlalchemy import Table,BigInteger,TIMESTAMP,DECIMAL,JSON,  DateTime, Enum, Float, ForeignKeyConstraint, Index, Integer, String, Text, text,Column, Date, DateTime, Float, Index, Integer, LargeBinary, String, Text,  select, func
from sqlalchemy.orm import column_property

from sqlalchemy.sql.sqltypes import NullType

from geoalchemy2 import Geometry
from sqlalchemy.orm import column_property
from sqlalchemy.sql import func

from sqlalchemy import Column, Date, DateTime, Float, ForeignKeyConstraint, Index, Integer, String, Text
from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy.sql.sqltypes import NullType

from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()
metadata = Base.metadata


class Location(Base):
    """
        The Location model represents a geospatial point associated with an address and several domain entities (persons, providers, orders, and images).
    It stores a geographic POINT using SRID 4326 for spatial operations and indexing.

Developers must be careful when using location_position directly.
This field is a raw spatial Geometry object; attempting to serialize or inspect it without conversion may raise exceptions depending on the database driver.
To avoid issues, always use position_wkt, which exposes the geometry in a safe, readable WKT (Well-Known Text) format.
    """
    __tablename__ = 'location'
    __table_args__ = (
        ForeignKeyConstraint(['location_address_id'], ['address.id_address'], name='fk_location_1'),
        Index('fk_location_1_idx', 'location_address_id'),
        Index('spatial', 'location_position')
    )

    id_location = Column(Integer, primary_key=True)
    location_position = Column(Geometry('POINT', srid=4326), nullable=False)
    position_wkt = column_property(func.ST_AsText(location_position)) 
    location_name = Column(String(45))
    location_address_id = Column(Integer)
    location_postal_code = Column(Integer)

    location_address = relationship('Address', back_populates='location')
    person = relationship('Person', back_populates='person_location')
    product_provider = relationship('ProductProvider', back_populates='product_provider_location')
    location_image = relationship('LocationImage', back_populates='location')
    placed_order = relationship('PlacedOrder', back_populates='location')


class BusinessOperation(Base):
    """
    Business Operations View Model

    This model maps to the `business_operation` database view that consolidates
    all business transactions from both cart-based and order-based systems.

    The view provides:
    • Complete financial transaction history
    • Payment status and balance tracking
    • Supplier relationship mapping
    • Source type identification for each transaction

    Used for:
    • Financial reporting and analytics
    • Supplier performance monitoring
    • Payment reconciliation
    • Business intelligence dashboards

    Note: This is a read-only view model. Direct modifications are not supported.
    """
    __tablename__ = 'business_operation'
    
    supplier_id = Column(Integer, primary_key=True)
    order_id = Column(Integer)
    cart_id = Column(Integer)
    client = Column(Integer)
    seller_id = Column(Integer)
    total_amount = Column(Float(asdecimal=True))
    invoice_status = Column(String(50))
    total_paid = Column(DECIMAL(37, 4), server_default=text("'0.0000'"))
    total_deposited = Column(DECIMAL(37, 4), server_default=text("'0.0000'"))
    balance_due = Column(Float(asdecimal=True))
    payment_status = Column(String(14))
    source_table = Column(String(12))



# class BusinessOperationWithTotals(Base):
#     __tablename__ = 'business_operation_with_totals'
    
#     # Primary key columns (nullable for summary rows)
#     supplier_id = Column(Integer, nullable=True)
#     order_id = Column(Integer, nullable=True)
#     cart_id = Column(Integer, nullable=True)
    
#     # Business data columns
#     client = Column(Integer, nullable=True)
#     seller_id = Column(Integer, nullable=True)
#     total_amount = Column(Float(asdecimal=True))
#     invoice_status = Column(String(50))
#     total_paid = Column(DECIMAL(37, 4), server_default=text("'0.0000'"))
#     total_deposited = Column(DECIMAL(37, 4), server_default=text("'0.0000'"))
#     balance_due = Column(Float(asdecimal=True))
#     payment_status = Column(String(14))
#     source_table = Column(String(12))
    
#     # Row type to distinguish between detail and summary rows
#     row_type = Column(String(20), nullable=False)  # 'detail', 'supplier_summary', 'grand_total'
    
#     # Since this is a view with union of different row types, we need to define
#     # a composite primary key that works for all row types
#     __mapper_args__ = {
#         'primary_key': [supplier_id, order_id, cart_id, row_type]
#     }
    
#     def __repr__(self):
#         return f"<BusinessOperationWithTotals(row_type='{self.row_type}', supplier_id={self.supplier_id}, amount={self.total_amount})>"
    
#     @property
#     def is_detail_row(self):
#         """Check if this is a detail row."""
#         return self.row_type == 'detail'
    
#     @property
#     def is_supplier_summary(self):
#         """Check if this is a supplier summary row."""
#         return self.row_type == 'supplier_summary'
    
#     @property
#     def is_grand_total(self):
#         """Check if this is a grand total row."""
#         return self.row_type == 'grand_total'
    
#     @property
#     def is_summary_row(self):
#         """Check if this is any type of summary row."""
#         return self.row_type in ['supplier_summary', 'grand_total']












