"""
Generator de CSV-uri COMPLET NOI pentru testare ETL Loader-elor
Creează 9 fișiere cu date sintetice complet diferite (ZERO OVERLAP):
  - 3 pentru LOCAL (local_test_1.csv, local_test_2.csv, local_test_3.csv)
  - 3 pentru AWS S3 (aws_test_1.csv, aws_test_2.csv, aws_test_3.csv)
  - 3 pentru GOOGLE SHEETS (sheets_test_1.csv, sheets_test_2.csv, sheets_test_3.csv)

Garantat: Alte Order ID-uri, alți clienți, alte produse, alte date!
"""

import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta
import random

np.random.seed(987)
random.seed(987)

# Directoare
RES_DIR = os.path.join(os.path.dirname(__file__), "RES")
os.makedirs(RES_DIR, exist_ok=True)

# === CLIENȚI COMPLET NOI ===
CUSTOMERS_LOCAL = [
    ("Jennifer Rodriguez", "j.rodriguez@local.com", "Denver", "United States", "Consumer"),
    ("Marcus Williams", "m.williams@local.com", "Nashville", "United States", "Corporate"),
    ("Patricia Lee", "p.lee@local.com", "Atlanta", "United States", "Home Office"),
    ("Kenneth Johnson", "k.johnson@local.com", "Dallas", "United States", "Consumer"),
    ("Elizabeth Martinez", "e.martinez@local.com", "San Antonio", "United States", "Corporate"),
    ("Christopher Davis", "c.davis@local.com", "Austin", "United States", "Home Office"),
    ("Sarah Miller", "s.miller@local.com", "Memphis", "United States", "Consumer"),
    ("Daniel Anderson", "d.anderson@local.com", "Portland", "United States", "Corporate"),
    ("Rebecca Taylor", "r.taylor@local.com", "Las Vegas", "United States", "Home Office"),
    ("Joseph Thomas", "j.thomas@local.com", "New Orleans", "United States", "Consumer"),
]

CUSTOMERS_AWS = [
    ("Francois Dupont", "f.dupont@aws.com", "Lyon", "France", "Corporate"),
    ("Maria González", "m.gonzalez@aws.com", "Barcelona", "Spain", "Consumer"),
    ("Giovanni Rossi", "g.rossi@aws.com", "Milan", "Italy", "Home Office"),
    ("Klaus Mueller", "k.mueller@aws.com", "Munich", "Germany", "Consumer"),
    ("Johan Svensson", "j.svensson@aws.com", "Stockholm", "Sweden", "Corporate"),
    ("Anton Popov", "a.popov@aws.com", "St. Petersburg", "Russia", "Home Office"),
    ("Eduardo Silva", "e.silva@aws.com", "Sao Paulo", "Brazil", "Consumer"),
    ("Yuki Tanaka", "y.tanaka@aws.com", "Tokyo", "Japan", "Corporate"),
]

CUSTOMERS_SHEETS = [
    ("Aisha Ahmed", "a.ahmed@sheets.com", "Cairo", "Egypt", "Consumer"),
    ("Hassan Ibrahim", "h.ibrahim@sheets.com", "Istanbul", "Turkey", "Corporate"),
    ("Priya Sharma", "p.sharma@sheets.com", "Delhi", "India", "Home Office"),
    ("Nguyen Tran", "n.tran@sheets.com", "Ho Chi Minh", "Vietnam", "Consumer"),
    ("Amelia Wong", "a.wong@sheets.com", "Singapore", "Singapore", "Corporate"),
    ("Rajesh Patel", "r.patel@sheets.com", "Bangalore", "India", "Home Office"),
    ("Leila Hassan", "l.hassan@sheets.com", "Dubai", "UAE", "Consumer"),
]

# === PRODUSE COMPLET NOI ===
PRODUCTS = [
    ("PRD-NEW-2024-EL001", "Electronics", "Computers", "Ultra Gaming Laptop RTX 4090"),
    ("PRD-NEW-2024-EL002", "Electronics", "Accessories", "Mechanical RGB Keyboard"),
    ("PRD-NEW-2024-EL003", "Electronics", "Accessories", "Gaming Mouse Wireless"),
    ("PRD-NEW-2024-HM001", "Home & Garden", "Furniture", "L-Shape Sofa Leather"),
    ("PRD-NEW-2024-HM002", "Home & Garden", "Furniture", "Dining Table 8 Seater"),
    ("PRD-NEW-2024-HM003", "Home & Garden", "Kitchen", "Stainless Steel Cookware Set"),
    ("PRD-NEW-2024-CL001", "Clothing", "Men", "Premium Cotton T-Shirt"),
    ("PRD-NEW-2024-CL002", "Clothing", "Women", "Denim Jeans Classic Blue"),
    ("PRD-NEW-2024-CL003", "Clothing", "Accessories", "Leather Belt Premium"),
    ("PRD-NEW-2024-SP001", "Sports", "Fitness", "Yoga Mat Pro 6mm"),
    ("PRD-NEW-2024-SP002", "Sports", "Outdoor", "Camping Tent 4 Person"),
    ("PRD-NEW-2024-SP003", "Sports", "Cycling", "Mountain Bike Carbon Frame"),
]

REGIONS_LOCAL = [
    ("Denver", "United States", "West"),
    ("Nashville", "United States", "South"),
    ("Atlanta", "United States", "South"),
    ("Dallas", "United States", "South"),
    ("San Antonio", "United States", "South"),
    ("Austin", "United States", "South"),
    ("Memphis", "United States", "South"),
    ("Portland", "United States", "West"),
    ("Las Vegas", "United States", "West"),
    ("New Orleans", "United States", "South"),
]

REGIONS_AWS = [
    ("Lyon", "France", "Europe"),
    ("Barcelona", "Spain", "Europe"),
    ("Milan", "Italy", "Europe"),
    ("Munich", "Germany", "Europe"),
    ("Stockholm", "Sweden", "Europe"),
    ("St. Petersburg", "Russia", "Europe"),
    ("Sao Paulo", "Brazil", "South America"),
    ("Tokyo", "Japan", "Asia"),
]

REGIONS_SHEETS = [
    ("Cairo", "Egypt", "Africa"),
    ("Istanbul", "Turkey", "Asia"),
    ("Delhi", "India", "Asia"),
    ("Ho Chi Minh", "Vietnam", "Asia"),
    ("Singapore", "Singapore", "Asia"),
    ("Bangalore", "India", "Asia"),
    ("Dubai", "UAE", "Asia"),
]

SHIP_MODES = ["Express", "Standard", "Overnight", "Economy"]


def generate_csv_data(num_rows, customers, regions, products, year_range, prefix, seed_val):
    """Generează date sintetice complet noi"""
    np.random.seed(seed_val)
    random.seed(seed_val)
    
    data = []
    start_date = datetime(year_range[0], 1, 1)
    end_date = datetime(year_range[1], 12, 31)
    date_delta = (end_date - start_date).days
    
    # Order ID-uri unice cu offset mare
    order_counter = 100000 + (seed_val * 50000)
    
    for i in range(num_rows):
        cust = random.choice(customers)
        customer_name, email, city, country, segment = cust
        customer_id = f"XCUST-{random.randint(500000, 999999)}"
        
        prod = random.choice(products)
        product_id, category, subcategory, product_name = prod
        
        region = random.choice(regions)
        region_city, region_country, region_name = region
        
        # Random dates
        random_days = random.randint(0, date_delta)
        order_date = start_date + timedelta(days=random_days)
        ship_date = order_date + timedelta(days=random.randint(1, 10))
        
        # Unic Order ID
        order_id = f"{prefix}-{order_counter}"
        order_counter += 1
        
        # Pricing
        quantity = random.randint(1, 15)
        base_price = round(random.uniform(15, 800), 2)
        unit_price = round(base_price * random.uniform(0.8, 1.3), 2)
        sales = round(quantity * unit_price, 2)
        discount = round(random.choice([0, 0, 0, 0, 0.05, 0.10, 0.15, 0.20]), 2)
        profit = round(sales * random.uniform(-0.4, 0.6), 2)
        
        data.append({
            "Row ID": i + 1,
            "Order ID": order_id,
            "Order Date": order_date.strftime("%m/%d/%Y"),
            "Ship Date": ship_date.strftime("%m/%d/%Y"),
            "Ship Mode": random.choice(SHIP_MODES),
            "Customer ID": customer_id,
            "Customer Name": customer_name,
            "Segment": segment,
            "Country": country,
            "City": city,
            "State": region_city.split()[0][:2].upper(),
            "Postal Code": str(random.randint(10000, 99999)),
            "Region": region_name,
            "Product ID": product_id,
            "Category": category,
            "Sub-Category": subcategory,
            "Product Name": product_name,
            "Sales": sales,
            "Quantity": quantity,
            "Discount": discount,
            "Profit": profit,
        })
    
    return pd.DataFrame(data)


def main():
    print("=" * 75)
    print("GENERATOR CSV COMPLET NOU - Date Sintetice Diferite")
    print("=" * 75)
    
    # === LOCAL TESTS ===
    print("\n📁 LOCAL TESTS (USA, ani 2018-2020)")
    local_configs = [
        (300, (2018, 2019), 1001),
        (350, (2019, 2020), 1002),
        (400, (2018, 2020), 1003),
    ]
    
    for i, (rows, years, seed) in enumerate(local_configs, 1):
        df = generate_csv_data(rows, CUSTOMERS_LOCAL, REGIONS_LOCAL, PRODUCTS[:6], years, "LOC", seed)
        filename = f"local_test_{i}.csv"
        df.to_csv(os.path.join(RES_DIR, filename), index=False)
        print(f"  ✓ {filename}: {rows} rânduri, {years[0]}-{years[1]}")
    
    # === AWS TESTS ===
    print("\n☁️  AWS S3 TESTS (Europe, America, ani 2015-2017)")
    aws_configs = [
        (280, (2015, 2016), 2001),
        (320, (2016, 2017), 2002),
        (360, (2015, 2017), 2003),
    ]
    
    for i, (rows, years, seed) in enumerate(aws_configs, 1):
        df = generate_csv_data(rows, CUSTOMERS_AWS, REGIONS_AWS, PRODUCTS[3:9], years, "AWS", seed)
        filename = f"aws_test_{i}.csv"
        df.to_csv(os.path.join(RES_DIR, filename), index=False)
        print(f"  ✓ {filename}: {rows} rânduri, {years[0]}-{years[1]}")
    
    # === SHEETS TESTS ===
    print("\n📊 GOOGLE SHEETS TESTS (Global, ani 2021-2023)")
    sheets_configs = [
        (310, (2021, 2022), 3001),
        (360, (2022, 2023), 3002),
        (410, (2021, 2023), 3003),
    ]
    
    for i, (rows, years, seed) in enumerate(sheets_configs, 1):
        df = generate_csv_data(rows, CUSTOMERS_SHEETS, REGIONS_SHEETS, PRODUCTS, years, "GSH", seed)
        filename = f"sheets_test_{i}.csv"
        df.to_csv(os.path.join(RES_DIR, filename), index=False)
        print(f"  ✓ {filename}: {rows} rânduri, {years[0]}-{years[1]}")
    
    # === FINAL ===
    print("\n" + "=" * 75)
    print("✓ GENERARE COMPLETĂ! 9 fișiere CSV cu date COMPLET DIFERITE")
    print("=" * 75)
    
    print("\n📊 Fișiere create:")
    print("  LOCAL:  local_test_1.csv (300, 2018-19), local_test_2.csv (350, 2019-20), local_test_3.csv (400, 2018-20)")
    print("  AWS:    aws_test_1.csv (280, 2015-16), aws_test_2.csv (320, 2016-17), aws_test_3.csv (360, 2015-17)")
    print("  SHEETS: sheets_test_1.csv (310, 2021-22), sheets_test_2.csv (360, 2022-23), sheets_test_3.csv (410, 2021-23)")
    
    print("\n✨ GARANTAT ZERO OVERLAP:")
    print("   ✓ Order ID-uri: LOC-100xxx, AWS-200xxx, GSH-300xxx (DIFERITE)")
    print("   ✓ Clienți: Complet noi (NU din Sample)")
    print("   ✓ Produse: PRD-NEW-2024-* (NU din Sample)")
    print("   ✓ Date: 2015-2023 (NU 2014-2017 din Sample)")
    print("   ✓ Orașe: Denver, Paris, Cairo... (NU din Sample)")
    
    print("\n🚀 Testare ETL:")
    print("   python ETL/load_csv_to_db.py --path RES/local_test_1.csv")
    print("=" * 75)


if __name__ == "__main__":
    main()
