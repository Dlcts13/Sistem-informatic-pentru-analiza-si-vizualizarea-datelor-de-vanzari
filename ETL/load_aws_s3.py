import pandas as pd
import boto3
import sys
import os
import argparse
from io import BytesIO
from dotenv import load_dotenv

load_dotenv()

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),"..")))
from ETL.base_loader import BaseDataLoader


class AWSS3Loader(BaseDataLoader):
    def __init__(
        self,
        bucket_name: str = None,
        file_key: str = None,
        aws_access_key_id: str = None,
        aws_secret_access_key: str = None,
        region_name: str = "eu-north-1",
        source_name: str = None
    ):
        

        if bucket_name is None:
            bucket_name=os.getenv("AWS_BUCKET_NAME", "licenta-sales-data")
        if file_key is None:
            file_key=os.getenv("AWS_FILE_KEY","data_aws_s3.csv")
        

        if source_name is None:
            source_name= f"AWS S3: {bucket_name}/{file_key}"
        




        super().__init__(source_name=source_name)
        


        self.bucket_name=bucket_name
        self.file_key= file_key
        self.region_name =region_name
        



        if aws_access_key_id is None:
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID")
        if aws_secret_access_key is None:
            aws_secret_access_key= os.getenv("AWS_SECRET_ACCESS_KEY")

        if not aws_access_key_id or not aws_secret_access_key:
            raise ValueError(
                "AWS credentials not found"
            )



        


        self.s3_client=boto3.client(
            "s3",
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=region_name
        )
    





    def extract_data(self)-> pd.DataFrame:
        print(f"Citire fisier din S3: s3://{self.bucket_name}/{self.file_key}")
        
        try:
            file_extension=self.file_key.split(".")[-1].lower()
            
            response=self.s3_client.get_object(
                Bucket=self.bucket_name,
                Key=self.file_key
            )
            


            file_content=pd.io.common.BytesIO(response["Body"].read())
            


            if file_extension== "csv":
                df= pd.read_csv(file_content)
            elif file_extension in ["xlsx","xls"]:
                df= pd.read_excel(file_content)
            else:
                raise ValueError(f"Format nesuportat: {file_extension}")
            


            
            if "unit_price" not in df.columns:
                if "Sales" in df.columns and "Quantity" in df.columns:
                    df["unit_price"]=pd.to_numeric(df["Sales"],errors="coerce")/pd.to_numeric(df["Quantity"],errors="coerce")
                elif "revenue" in df.columns and "Quantity" in df.columns:
                    df["unit_price"]=pd.to_numeric(df["revenue"], errors="coerce")/pd.to_numeric(df["Quantity"], errors="coerce")
            

            if "revenue" not in df.columns and "Sales" in df.columns:
                df["revenue"]=df["Sales"]
            



            print(f"Date extrase succes: {len(df)} randuri")


            return df
            


        except Exception as e:
            print(f"Eroare la citire: {str(e)}")



            return pd.DataFrame()
    



    def get_transform_mapping(self) -> dict:
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
        description="AWSS3Loader",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    



    parser.add_argument(
        '--bucket',
        type=str,
        default=None,
        help='Numele bucket-ului S3'
    )
    parser.add_argument(
        '--key',
        type=str,
        default=None,
        help='Path-ul fisierului in bucket'
    )
    parser.add_argument(
        '--region',
        type=str,
        default="eu-north-1",
        help='AWS region'
    )
    



    args=parser.parse_args()
    


    try:
        loader=AWSS3Loader(
            bucket_name=args.bucket,
            file_key=args.key,
            region_name=args.region
        )
        loader.run()
    except Exception as e:
        print(f"EROARE: {str(e)}")
        sys.exit(1)
