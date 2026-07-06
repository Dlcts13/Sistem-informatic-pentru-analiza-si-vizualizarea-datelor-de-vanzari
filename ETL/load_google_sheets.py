import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import sys
import os
import argparse
import streamlit as st

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),"..")))
from ETL.base_loader import BaseDataLoader


class GoogleSheetsLoader(BaseDataLoader):
    def __init__(
        self,
        spreadsheet_id: str =None,
        sheet_name: str= None,
        credentials_path: str= None,
        source_name: str= None
    ):





        if spreadsheet_id is None:
            spreadsheet_id=os.getenv("GOOGLE_SHEETS_ID","164Mj4CzG7ES5uMhdrukEEDD_vnHW_aETSCzB1bVySm8")
        if sheet_name is None:
            sheet_name =os.getenv("GOOGLE_SHEETS_NAME","data_google_sheets")
        if source_name is None:
            source_name= f"Google Sheets: {sheet_name}"
        
        super().__init__(source_name=source_name)
        
        self.spreadsheet_id= spreadsheet_id
        self.sheet_name= sheet_name




        
        # if credentials_path is None:
        #     credentials_path=os.getenv("GOOGLE_SHEETS_CREDENTIALS_PATH")
        #     if not credentials_path or not os.path.exists(credentials_path):
        #         standard_paths = [
        #             "credentials_google.json",
        #             os.path.join(os.path.dirname(__file__),"..","credentials_google.json"),
        #             "conectaregooglecloud/licenta-497517-e8484745f645.json"
        #         ]



        #         for path in standard_paths:
        #             if os.path.exists(path):
        #                 credentials_path= path
        #                 break
        


        # if not credentials_path or not os.path.exists(credentials_path):
        #     raise FileNotFoundError(
        #         f"Credentiale Google Sheets nu gasite\n"
        #         f"Cale cautata: {credentials_path}"
        #     )
        



        # scope= ["https://www.googleapis.com/auth/spreadsheets.readonly"]
        # creds=Credentials.from_service_account_file(credentials_path, scopes=scope)
        # self.client = gspread.authorize(creds)
        scope = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
        
        # 1. Incearca direct din Streamlit Secrets (Cloud)
        try:
            if "gcp_service_account" in st.secrets:
                gcp_info = dict(st.secrets["gcp_service_account"])
                creds = Credentials.from_service_account_info(gcp_info, scopes=scope)
            else:
                creds = None
        except Exception:
            creds = None

        # 2. Fallback local (Laptop) daca nu a gasit in cloud
        if creds is None:
            if credentials_path is None:
                standard_paths = [
                    "credentials_google.json",
                    os.path.join(os.path.dirname(__file__),"..","credentials_google.json"),
                    "conectaregooglecloud/licenta-497517-e8484745f645.json"
                ]
                credentials_path = next((p for p in standard_paths if os.path.exists(p)), None)
            
            if not credentials_path or not os.path.exists(credentials_path):
                raise FileNotFoundError("Credentiale Google Sheets nu gasite nici in Cloud, nici local!")
                
            creds = Credentials.from_service_account_file(credentials_path, scopes=scope)

        self.client = gspread.authorize(creds)
    






    def extract_data(self) -> pd.DataFrame:
        print(f"Citire Google Sheets: {self.sheet_name}")
        



        try:
            print(f"Conectare spreadsheet: {self.spreadsheet_id}")
            spreadsheet=self.client.open_by_key(self.spreadsheet_id)
            available_sheets=[ws.title for ws in spreadsheet.worksheets()]
            print(f"Sheet-uri disponibile: {available_sheets}")
            worksheet= spreadsheet.worksheet(self.sheet_name)
            print(f"Sheet gasit: {self.sheet_name}")
            


            data= worksheet.get_all_records()
            print(f"Randuri extrase: {len(data)}")
            


            df= pd.DataFrame(data)
            


            if "unit_price" not in df.columns and "Total_Revenue" in df.columns and "Units_Sold" in df.columns:
                df["unit_price"]=pd.to_numeric(df["Total_Revenue"], errors="coerce")/pd.to_numeric(df["Units_Sold"], errors="coerce")
            


            print(f"Date extrase cu succes: {len(df)} randuri")


            return df
            



        except Exception as e:
            print(f"Eroare de citire")
            print(f"Type: {type(e).__name__}")
            print(f"Message: {str(e)}")
            import traceback
            traceback.print_exc()
            return pd.DataFrame()
    




    def get_transform_mapping(self)-> dict:
        return {
            'order_id': 'Order ID',
            'order_date': 'Order Date',
            'product_name': 'Product Name',
            'category': 'Category',
            'subcategory': 'Sub-Category',
            'customer_name': 'Customer Name',
            'city': 'City',
            'country': 'Country',
            'region': 'Region',
            'segment': 'Segment',
            'quantity': 'Quantity',
            'unit_price': 'unit_price',
            'revenue': 'Sales',
            'discount': 'Discount',
            'profit': 'Profit'
        }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="GoogleSheetsLoader",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )


    
    parser.add_argument(
        '--id',
        type=str,
        default=None,
        help='ID-ul Google Sheets din URL'
    )
    parser.add_argument(
        '--sheet',
        type=str,
        default=None,
        help='Numele tab-ului din spreadsheet'
    )
    parser.add_argument(
        '--creds',
        type=str,
        default=None,
        help='Calea catre fisierul JSON cu credentiale Google'
    )
    


    args = parser.parse_args()
    


    try:
        loader= GoogleSheetsLoader(
            spreadsheet_id=args.id,
            sheet_name=args.sheet,
            credentials_path=args.creds
        )
        loader.run()
    except Exception as e:
        print(f"EROARE: {str(e)}")
        sys.exit(1)
