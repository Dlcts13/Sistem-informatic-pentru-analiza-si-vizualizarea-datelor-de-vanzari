import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from sqlalchemy import create_engine

from DB.connection import get_engine

# @st.cache_resource
# def get_connection():
#     DB_URI="postgresql+psycopg2://licenta:licenta123@localhost:5432/sales_db"
#     return create_engine(DB_URI)


@st.cache_data(ttl=3600)
def load_product_data():
    engine = get_engine()
    query="""
        SELECT p.id,p.name, p.category, p.subcategory,p.brand,
            SUM(f.revenue) as total_revenue,
            SUM(f.quantity) as total_quantity,
            SUM(f.profit) as total_profit,
            COUNT(DISTINCT f.id) as nr_tranzactii
        FROM fact_sales f
        JOIN dim_product p ON f.product_id = p.id
        GROUP BY p.id, p.name, p.category, p.subcategory, p.brand
        ORDER BY total_revenue DESC
    """
    with engine.connect() as conn:
        df = pd.read_sql(query, conn)
        
    return df

    # return pd.read_sql(query, engine)






def calculate_product_kpis(df):
    return {
        "total_products": df["name"].nunique(),
        "total_brands": df["brand"].nunique(),
        "total_categories": df["category"].nunique(),
        "total_revenue": df["total_revenue"].sum(),
        "total_profit": df["total_profit"].sum(),
        "avg_profit_margin":((df["total_profit"]/df["total_revenue"]*100).mean()) if df["total_revenue"].sum()>0 else 0
    }




def get_category_summary(df):
    category_summary=df.groupby("category").agg({
        "total_revenue":"sum",
        "total_profit":"sum",
        "total_quantity":"sum",
        "name": "nunique"
    }).reset_index()



    category_summary.columns=["category","revenue","profit","quantity","nr_produse"]
    category_summary["profit_margin"]=(category_summary["profit"] / category_summary["revenue"] *100).round(2)






    return category_summary.sort_values("revenue", ascending=False)







def get_brand_summary(df):
    brand_summary=df[df["brand"]!="Necunoscut"].groupby("brand").agg({
        "total_revenue":"sum",
        "total_profit": "sum",
        "total_quantity" : "sum",
        "name":"nunique"
    }).reset_index()

    brand_summary.columns= ["brand", "revenue", "profit", "quantity", "nr_produse"]
    brand_summary["profit_margin"] =(brand_summary["profit"] /brand_summary["revenue"] *100).round(2)




    return brand_summary.sort_values("revenue", ascending=False).head(15)


def get_top_products(df, limit=10):
    cols_to_keep=["name","category","subcategory","brand", "total_revenue", "total_profit","total_quantity", "nr_tranzactii"]
    top_products = df[cols_to_keep].nlargest(limit, "total_revenue").reset_index(drop=True).copy()

    top_products["profit_margin"] =(top_products["total_profit"]/ top_products["total_revenue"] *100).round(2)




    return top_products






def get_low_performers(df, limit=10):
    df_copy=df.copy()
    df_copy["profit_margin"]=(df_copy["total_profit"] /df_copy["total_revenue"] *100)
    low_perf= df_copy[df_copy["total_profit"]< 0].nsmallest(limit, "total_profit")[["name","category", "subcategory","brand", "total_revenue", "total_profit", "profit_margin"]
    ].reset_index(drop=True)




    return low_perf





def plot_category_pie(category_data):
    fig = px.pie(
        category_data,
        values="revenue",
        names="category",
        title="Distributia veniturilor pe categorii",
    )
    fig.update_traces(textposition="inside", textinfo="percent+label")




    return fig






def plot_category_bar(category_data):
    fig= go.Figure()
    fig.add_trace(go.Bar(x=category_data["category"], y=category_data["revenue"],name="Venit"))
    fig.add_trace(go.Bar(x=category_data["category"],y=category_data["profit"],name="Profit",))
    


    fig.update_layout(
        title="Venit vs Profit pe Categorii",
        xaxis_title="Categorie",
        yaxis_title="Valoare $",
    )

    return fig


def plot_top_brands(brand_data):
    fig = px.bar(brand_data, x="revenue", y="brand", orientation="h",color="profit_margin",
        labels={"revenue": "Venit Total $", "brand": "Brand", "profit_margin": "Marja Profit (%)"},
        title="Top Branduri dupa venit"
    )




    return fig





def plot_top_products(top_prod_data):
    top_prod_data["display_name"]=top_prod_data["name"].str[:35]



    fig = px.bar(top_prod_data,x="total_revenue", y="display_name", orientation="h", color="profit_margin",
        labels={"total_revenue":"Venit $", "display_name": "Produs", "profit_margin":"Marja Profit (%)"},
        title="Top Produse dupa venit"
    )

    return fig
