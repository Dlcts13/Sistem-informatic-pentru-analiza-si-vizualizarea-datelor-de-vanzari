import pandas as pd
import numpy as np
import os 
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')))
from DB.models import DimProduct,DimDate,DimCustomer, DimRegion, FactSales


DB_URI="postgresql+psycopg2://licenta:licenta123@localhost:5432/sales_db"
engine= create_engine(DB_URI)

Session= sessionmaker(bind=engine)
session= Session()

def main():
    print("Citire fisier CSV")


    script_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(script_dir, "..", "RES", "Sample - Superstore.csv")

    df=pd.read_csv(csv_path,encoding="windows-1252")

    #==============Modificare date========
    print("Print trandformare date")
    df["Order Date"]=pd.to_datetime(df["Order Date"])
    df["revenue"]=df["Sales"]
    df["unit_price"]=df["Sales"]/ df["Quantity"]

    df["brand"]="Unknown brand"
    df["email"]="email@customer.com"

    #==========Incarcare dim=====
    print("Incarcare dimensiuni")

    
    product_cache={
        p.name:
        p.id for p in session.query(DimProduct).all()
    }

    customer_cache={
        c.name:
        c.id for c in session.query(DimCustomer).all()


    }

    date_cache= {
        d.date:
        d.id for d in session.query(DimDate).all()
    }

    region_cache={
        (r.city, r.country):
        r.id for r in session.query(DimRegion).all()

    }

    #DimDate
    unique_dates= df["Order Date"].dt.date.unique()
    for d in unique_dates:
        if d not in date_cache:
            dt_obj = pd.to_datetime(d)
            new_date= DimDate(
                date=d,
                year=dt_obj.year,
                month=dt_obj.month,
                quarter=dt_obj.quarter,
                week=dt_obj.week
            )

            session.add(new_date)
            session.commit()
            date_cache[d]=new_date.id


    #DimProduct
    for i, row in df[["Product Name", "Category", "Sub-Category", "brand"]].drop_duplicates().iterrows():
        if row["Product Name"] not in product_cache:
            new_prod= DimProduct(name=row["Product Name"], category=row["Category"], subcategory=row["Sub-Category"], brand=row["brand"])

            session.add(new_prod)
            session.commit()
            product_cache[row["Product Name"]]= new_prod.id


if __name__=="__main__" :
    main()
