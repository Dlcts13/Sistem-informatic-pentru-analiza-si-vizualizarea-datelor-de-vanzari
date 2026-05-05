import pandas as pd
import numpy as np
import os 
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import re

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')))
from DB.models import DimProduct,DimDate,DimCustomer, DimRegion, FactSales


DB_URI="postgresql+psycopg2://licenta:licenta123@localhost:5432/sales_db"
engine= create_engine(DB_URI)

Session= sessionmaker(bind=engine)
session= Session()


def extrage_brand(nume_produs):
    if not isinstance(nume_produs,str):
        return "Necunoscut"
    
    text= nume_produs.replace("ï¿½"," ")

    match_by = re.search(r"\bby\s+([A-Za-z0-9&]+)", text, re.IGNORECASE)
    if match_by:
        return match_by.group(1).capitalize()
    

    cuvinte= text.split()

    primul_cuvant_valid= ""
    index_primul=0

    for i,cuvant in enumerate(cuvinte):
        if re.search(r"[A-Za-z]", cuvant):
            primul_cuvant_valid= cuvant
            index_primul=i
            break

    if not primul_cuvant_valid:
        return "Brand Necunoscut"
    

    primul_cuvant_valid= re.sub(r"^[^A-Za-z0-9&]+|[^A-Za-z0-9&]+$", "", primul_cuvant_valid)
    
    if index_primul +2 <len(cuvinte) and cuvinte[index_primul+1]=="&":
        al_treilea_cuvant =re.sub(r"^[^A-Za-z0-9&]+|[^A-Za-z0-9&]+$", "", cuvinte[index_primul+2])
        return f"{primul_cuvant_valid.capitalize()} & {al_treilea_cuvant.capitalize()}"
    

    return primul_cuvant_valid.capitalize()




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


    #Problema mare la brand trebuie extras din nume produs dar variaza masiv de obicei primul/primele 2 cuvinte
    # df["brand"]="Unknown brand"
    df["brand"]= df["Product Name"].apply(extrage_brand)



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


    print("Incarcat DimDate")
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

    print("Incarcat DimProduct")
    #DimProduct
    for i, row in df[["Product Name", "Category", "Sub-Category", "brand"]].drop_duplicates().iterrows():
        if row["Product Name"] not in product_cache:
            new_prod= DimProduct(name=row["Product Name"], category=row["Category"], subcategory=row["Sub-Category"], brand=row["brand"])

            session.add(new_prod)
            session.commit()
            product_cache[row["Product Name"]]= new_prod.id

    print("Incarcat DimCustomer")
    #DimCustomer
    for i,row in df[["Customer Name", "City", "Country", "Segment", "email"]].drop_duplicates().iterrows():
        if row["Customer Name"] not in customer_cache:
            new_cust = DimCustomer(name=row["Customer Name"], email=row["email"], city=row["City"], country=row["Country"], segment=row["Segment"])
            session.add(new_cust)
            session.commit()
            customer_cache[row["Customer Name"]]=new_cust.id

    print("Incarcat DimRegion")
    #DimREgion
    for i, row in df[["City", "Country", "Region"]].drop_duplicates().iterrows():
        key= (row["City"], row["Country"])
        if key not in region_cache:
            new_reg= DimRegion(city=row["City"], country=row["Country"], region=row["Region"])
            session.add(new_reg)

            session.commit()
            region_cache[key]= new_reg.id
    



    print("Incarcat FactSales")
    session.commit()



    existing_row_ids= {str(r[0]).strip for r in session.query(FactSales.source_order_id).all()}

    facts_to_insert=[]

    local_seen_ids =set()

    randuri_inserate=0
    randuri_sarite=0
    erori=0

    for index,row in df.iterrows():
        row_id_str=str(row["Row ID"]).strip()

        if row_id_str in existing_row_ids or row_id_str in local_seen_ids:
            randuri_sarite=randuri_sarite+1
            continue

        local_seen_ids.add(row_id_str)

        fact = FactSales(
            source_order_id=row_id_str,
            date_id=date_cache[row["Order Date"].date()],
            product_id= product_cache[row["Product Name"]],
            customer_id=customer_cache[row["Customer Name"]],
            region_id=region_cache[(row["City"],row["Country"])],
            quantity=row["Quantity"],
            unit_price=row["unit_price"],
            revenue=row["revenue"],
            discount=row["Discount"],
            profit=row["Profit"],
            source="Sample - Superstore.csv"
        )
        facts_to_insert.append(fact)

        try:
            session.add(fact)
            session.commit()
            randuri_inserate=randuri_inserate+1

        except Exception as e:
            session.rollback()
            erori=erori+1

        print("\n" + "="*30)
        print("="*30)
        print(f"Vanzari noi inserate cu succes: {randuri_inserate}")
        print(f"Vanzari ignorate: {randuri_sarite}")
        print(f"Erori: {erori}")
        print("="*30 + "\n")




if __name__=="__main__" :
    main()
