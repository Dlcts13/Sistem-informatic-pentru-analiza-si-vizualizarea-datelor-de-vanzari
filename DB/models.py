from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, DateTime
from sqlalchemy.orm import declarative_base,relationship
from datetime import datetime

Base = declarative_base() 

class DimProduct(Base):
    __tablename__ = "dim_product"

    id=Column(Integer,primary_key=True)
    name=Column(String(200))
    category=Column(String(200))
    subcategory=Column(String(200))
    brand=Column(String(200))

    sales=relationship("FactSales",back_populates="product")

class DimCustomer(Base):
    __tablename__="dim_customer"
    id=Column(Integer,primary_key=True)
    name=Column(String(200))
    email=Column(String(200))
    city=Column(String(200))
    country=Column(String(200))
    segment=Column(String(200))

    sales=relationship("FactSales",back_populates="customer")


class DimDate(Base):
    __tablename__="dim_date"

    id=Column(Integer,primary_key=True)
    date=Column(Date)
    year=Column(Integer)
    month=Column(Integer)
    quarter=Column(Integer)
    week=Column(Integer)

    sales=relationship("FactSales",back_populates="date")

class DimRegion(Base):
    __tablename__="dim_region"

    id=Column(Integer,primary_key=True)
    city=Column(String(200))
    country=Column(String(200))
    region=Column(String(200))

    sales=relationship("FactSales",back_populates="region")

class FactSales(Base):
    __tablename__="fact_sales"
    id= Column(Integer,primary_key=True)


    source_order_id=Column(String(200),unique=True,nullable=False)




    date_id=Column(Integer,ForeignKey("dim_date.id"))
    product_id=Column(Integer,ForeignKey("dim_product.id"))
    customer_id=Column(Integer,ForeignKey("dim_customer.id"))
    region_id=Column(Integer,ForeignKey("dim_region.id"))



    quantity=Column(Integer)
    unit_price=Column(Float)
    revenue=Column(Float)
    discount=Column(Float)
    profit=Column(Float)

    source=Column(String(200)) #de unde scot datele
    created_at = Column(DateTime,default=datetime.utcnow)


    date=relationship("DimDate",back_populates="sales")
    product=relationship("DimProduct",back_populates="sales")
    customer=relationship("DimCustomer",back_populates="sales")
    region=relationship("DimRegion",back_populates="sales")