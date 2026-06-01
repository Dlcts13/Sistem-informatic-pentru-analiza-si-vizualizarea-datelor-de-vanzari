import pandas as pd
import os
import sys
import argparse

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),"..")))
from ETL.base_loader import BaseDataLoader


class CSVLoader(BaseDataLoader):
    def __init__(self, csv_path: str=None):


        if csv_path is None:
            script_dir= os.path.dirname(os.path.abspath(__file__))
            csv_path= os.path.join(script_dir,"..", "RES","Sample - Superstore.csv")
        
        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"Fisierul CSV nu exista: {csv_path}")
        


        source_name=f"CSV Local: {os.path.basename(csv_path)}"
        super().__init__(source_name=source_name)
        


        self.csv_path = csv_path
    






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




    def extract_data(self)->pd.DataFrame:
        print("Citire fisier CSV")
        df=pd.read_csv(self.csv_path)
        


        df["revenue"]=df["Sales"]
        df["unit_price"]=df["Sales"]/df["Quantity"]
        


        return df
    








if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="CSVLoader",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    


    parser.add_argument(
        '--path', 
        type=str, 
        default=None,
        help='Calea catre fisierul CSV'
    )
    args = parser.parse_args()
    

    
    try:
        loader = CSVLoader(csv_path=args.path)
        loader.run()
    except Exception as e:
        print(f"EROARE: {str(e)}")
        sys.exit(1)
