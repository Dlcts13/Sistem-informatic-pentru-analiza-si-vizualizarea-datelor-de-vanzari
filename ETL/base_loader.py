import pandas as pd
import numpy as np
import os 
import sys
import re
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from abc import ABC, abstractmethod
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),"..")))
from DB.models import DimProduct, DimDate, DimCustomer, DimRegion, FactSales
from DB.connection import get_engine


class BaseDataLoader(ABC):  
    def __init__(self,source_name: str):
        self.source_name= source_name
        self.engine= get_engine()


        self.Session= sessionmaker(bind=self.engine)
        self.session= self.Session()
        
        self.product_cache= {}
        self.customer_cache= {}
        self.date_cache= {}
        self.region_cache= {}
        



        self.rows_inserted= 0
        self.rows_skipped= 0
        self.errors= 0
        
    @abstractmethod
    def extract_data(self) -> pd.DataFrame:
        pass
    
    @abstractmethod
    def get_transform_mapping(self) -> dict:
        pass
    
    def extract_brand(self, product_name: str) -> str:
        if not isinstance(product_name, str):
            return "Necunoscut"
        
        text = product_name.replace("ï¿½", " ")
        
        match_by = re.search(r"\bby\s+([A-Za-z0-9&]+)",text, re.IGNORECASE)
        if match_by:
            return match_by.group(1).capitalize()
        



        cuvinte=text.split()
        primul_cuvant_valid=""
        index_primul=0
        for i,cuvant in enumerate(cuvinte):
            if re.search(r"[A-Za-z]",cuvant):
                primul_cuvant_valid=cuvant
                index_primul= i
                break
        if not primul_cuvant_valid:
            return "Brand Necunoscut"
        
        primul_cuvant_valid=re.sub(r"^[^A-Za-z0-9&]+|[^A-Za-z0-9&]+$", "",primul_cuvant_valid)
        if index_primul+2<len(cuvinte) and cuvinte[index_primul+1]=="&":
            al_treilea_cuvant=re.sub(r"^[^A-Za-z0-9&]+|[^A-Za-z0-9&]+$", "",cuvinte[index_primul+2])
            return f"{primul_cuvant_valid.capitalize()} & {al_treilea_cuvant.capitalize()}"
        



        return primul_cuvant_valid.capitalize()
    


    def load_caches(self):
        print("incarca cacheuri din baza de date...")
        
        self.product_cache={
            p.name: p.id for p in self.session.query(DimProduct).all()
        }
        self.customer_cache={
            c.name: c.id for c in self.session.query(DimCustomer).all()
        }
        self.date_cache = {
            d.date: d.id for d in self.session.query(DimDate).all()
        }
        self.region_cache ={
            (r.city, r.country): r.id for r in self.session.query(DimRegion).all()
        }
    



    def upsert_dim_product(self,product_name: str, category:str,subcategory:str, brand:str) ->int:
        if product_name not in self.product_cache:
            new_prod=DimProduct(
                name=product_name,
                category=category,
                subcategory=subcategory,
                brand=brand
            )


            self.session.add(new_prod)
            self.session.commit()
            self.product_cache[product_name]=new_prod.id
        



        return self.product_cache[product_name]
    





    def upsert_dim_customer(self,customer_name: str,email: str,city: str, country:str, segment:str) ->int:
        if customer_name not in self.customer_cache:
            new_cust=DimCustomer(
                name=customer_name,
                email=email,
                city=city,
                country=country,
                segment=segment
            )



            self.session.add(new_cust)
            self.session.commit()
            self.customer_cache[customer_name]=new_cust.id
        




        return self.customer_cache[customer_name]
    




    def upsert_dim_date(self, date_obj) -> int:
        date_only=pd.to_datetime(date_obj).date()
        

        if date_only not in self.date_cache:
            dt_obj=pd.to_datetime(date_only)
            new_date=DimDate(
                date=date_only,
                year=dt_obj.year,
                month=dt_obj.month,
                quarter=dt_obj.quarter,
                week=dt_obj.week
            )

            self.session.add(new_date)
            self.session.commit()
            self.date_cache[date_only]=new_date.id
        





        return self.date_cache[date_only]
    




    def upsert_dim_region(self,city:str,country: str, region:str) ->int:
        key=(city,country)
        

        if key not in self.region_cache:
            new_reg=DimRegion(
                city=city,
                country=country,
                region=region
            )



            self.session.add(new_reg)
            self.session.commit()
            self.region_cache[key]=new_reg.id
        



        return self.region_cache[key]
    



    def validate_and_clean_data(self,df:pd.DataFrame, mapping:dict) ->pd.DataFrame:
        print("Valideaza si curata datele...")

        cols_to_rename={v: k for k, v in mapping.items() if v in df.columns}
        df=df.rename(columns=cols_to_rename)
        


        df=df.loc[:,~df.columns.duplicated(keep="first")]
        


        if "unit_price" not in df.columns:
            if "revenue" in df.columns and "quantity" in df.columns:
                df["unit_price"]=pd.to_numeric(df["revenue"],errors="coerce") / pd.to_numeric(df["quantity"],errors="coerce")
            else:
                df["unit_price"]=0.0
        if "email" not in df.columns:
            df["email"]="email@customer.com"
        if "revenue" not in df.columns:
            df["revenue"]= 0.0
        if "discount" not in df.columns:
            df["discount"] =0.0
        if "profit" not in df.columns:
            df["profit"] =0.0
        

        df["order_date"]=pd.to_datetime(df["order_date"],errors="coerce")
        df["quantity"]=pd.to_numeric(df["quantity"], errors="coerce").astype("Int64")
        df["unit_price"]=pd.to_numeric(df["unit_price"],errors="coerce")
        df["revenue"]= pd.to_numeric(df["revenue"], errors="coerce")
        df["discount"] =pd.to_numeric(df["discount"], errors="coerce")
        df["profit"] =pd.to_numeric(df["profit"], errors="coerce")
        
        df = df.dropna(subset=["order_date", "quantity", "revenue"])
        df["email"]= df["email"].fillna("email@customer.com")
        




        return df
    
    def load_dimensions(self, df: pd.DataFrame):
        print("incarca dimensiuni...")
        
        print("incarca DimDate...")
        unique_dates =df["order_date"].dt.date.unique()
        for d in unique_dates:
            self.upsert_dim_date(d)
        



        print("incarca DimProduct...")
        for i,row in df[["product_name","category","subcategory"]].drop_duplicates().iterrows():
            brand=self.extract_brand(row["product_name"])
            self.upsert_dim_product(
                row["product_name"],
                row["category"],
                row["subcategory"],
                brand
            )


        


        print("incarca DimCustomer...")
        for i,row in df[["customer_name","email","city","country", "segment"]].drop_duplicates().iterrows():
            self.upsert_dim_customer(
                row["customer_name"],
                row["email"],
                row["city"],
                row["country"],
                row["segment"]
            )
        



        print("incarca DimRegion...")
        for i,row in df[["city","country","region"]].drop_duplicates().iterrows():
            self.upsert_dim_region(row["city"],row["country"], row["region"])
    




    def load_facts(self, df: pd.DataFrame):
        print("incarca FactSales...")
        existing_row_ids={str(r[0]).strip() for r in self.session.query(FactSales.source_order_id).all()}
        local_seen_ids=set()
        
        for index,row in df.iterrows():
            row_id_str=str(row["order_id"]).strip()
            if row_id_str in existing_row_ids or row_id_str in local_seen_ids:
                self.rows_skipped+=1
                continue
            



            local_seen_ids.add(row_id_str)
            
            try:
                product_id= self.product_cache.get(row["product_name"])
                customer_id =self.customer_cache.get(row["customer_name"])
                date_id= self.date_cache.get(row["order_date"].date())
                region_id= self.region_cache.get((row["city"],row["country"]))
                


                if not all([product_id,customer_id,date_id,region_id]):
                    self.errors += 1
                    continue
                


                fact=FactSales(
                    source_order_id=row_id_str,
                    date_id=date_id,
                    product_id=product_id,
                    customer_id=customer_id,
                    region_id=region_id,
                    quantity=int(row["quantity"]),
                    unit_price=row["unit_price"],
                    revenue=row["revenue"],
                    discount=row["discount"],
                    profit=row["profit"],
                    source=self.source_name
                )
                



                self.session.add(fact)
                self.session.commit()
                self.rows_inserted += 1
                
            except Exception as e:
                self.session.rollback()
                self.errors+= 1
                print(f"Eroare la randul {index}: {str(e)}")
    






    def print_statistics(self):
        print(f"Randuri inserate: {self.rows_inserted}")
        print(f"Randuri ignorate: {self.rows_skipped}")
        print(f"Erori: {self.errors}")
    






    def run(self):
        try:
            print(f"Pornire ETL pentru {self.source_name}")
            

            df= self.extract_data()
            print(f"Date extrase: {len(df)} randuri")
            


            mapping=self.get_transform_mapping()
            df=self.validate_and_clean_data(df, mapping)
            print(f"Datele validate: {len(df)} randuri")
            
            


            self.load_caches()
            self.load_dimensions(df)
            self.load_facts(df)
            
            




            self.print_statistics()
            


        except Exception as e:
            print(f"Eroare mare: {str(e)}")
            import traceback
            traceback.print_exc()
            self.session.rollback()
        finally:
            self.session.close()
