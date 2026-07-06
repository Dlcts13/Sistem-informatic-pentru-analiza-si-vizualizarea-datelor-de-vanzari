import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from sqlalchemy import create_engine
from DB.connection import get_engine

@st.cache_resource
def get_connection():
    return get_engine()


@st.cache_data(ttl=3600)
def load_dashboard_data(version_hash=None):
    engine=get_connection()
    query="""
        SELECT 
            f.id as order_id, 
            d.date,
            d.year,
            d.month,
            r.region,
            p.category,
            f.quantity,
            f.revenue,
            f.profit,
            CASE WHEN f.profit> 0 THEN 'Profitabil' ELSE 'Neprofitabil' END as profit_status
        FROM fact_sales f
        JOIN dim_date d ON f.date_id = d.id
        JOIN dim_region r ON f.region_id = r.id
        JOIN dim_product p ON f.product_id = p.id
        ORDER BY d.date DESC
    """



    return pd.read_sql(query, engine)




def calculate_kpis(df):

    total_orders=df["order_id"].nunique()
    total_revenue= df["revenue"].sum()
    total_profit=df["profit"].sum()
    profit_margin=(total_profit/total_revenue*100) if total_revenue > 0 else 0
    avg_order_value =total_revenue /total_orders if total_orders > 0 else 0
    


    return {
        "total_orders":total_orders,
        "total_revenue":total_revenue,
        "total_profit":total_profit,
        "profit_margin":profit_margin,
        "avg_order_value": avg_order_value
    }





def get_trend_data(df):
    df_trend=df.groupby("date").agg({
        "revenue":"sum",
        "profit": "sum",
        "order_id":"nunique"
    }).reset_index()

    df_trend.columns=["date","revenue","profit","nr_orders"]



    return df_trend


def get_regional_performance(df):


    regional_data=df.groupby("region").agg({
        "revenue":"sum",
        "profit":"sum",
        "order_id": "nunique"
    }).reset_index()

    regional_data.columns=["region","revenue","profit", "orders"]
    regional_data = regional_data.sort_values("revenue",ascending=False)




    return regional_data




def get_category_performance(df):
    category_data= df.groupby("category").agg({
        "revenue":"sum",
        "profit":"sum",
        "quantity": "sum"
    }).reset_index()

    category_data.columns=["category","revenue","profit","quantity"]
    category_data["profit_rate"] =(category_data["profit"]/category_data["revenue"] * 100).round(2)



    return category_data.sort_values("revenue",ascending=False)



def plot_trend_chart(df_trend):
    fig= go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df_trend["date"], y=df_trend["revenue"],
        name="Venit Total"
    ))
    fig.add_trace(go.Scatter(
        x=df_trend["date"], y=df_trend["profit"],
        name="Profit Total"
    ))
    fig.update_layout(
        title="Evolutie Venit vs Profit",
        xaxis_title="Data",
        yaxis_title="Valoare $",
    )




    return fig


def plot_regional_performance(regional_data):
    fig = px.bar(
        regional_data,
        x="revenue",
        y="region",
        orientation="h",
        color="profit",
        labels={"revenue":"Venit Total $","region": "Regiune","profit": "Profit $"},
        title="Performanta pe regiuni"
    )



    return fig


def plot_category_performance(category_data):
    fig = px.bar(
        category_data,
        x="revenue",
        y="category",
        orientation="h",
        text="profit_rate",
        labels={"revenue":"Venit Total $","category":"Categorie","profit_rate": "Rata Profit (%)"},
        title="Performanta pe Categorii"
    )

    fig.update_traces(texttemplate="%{text:.2f}%")



    return fig




def plot_profit_status(df):
    status_data=df.groupby("profit_status")["order_id"].nunique().reset_index()
    status_data.columns=["profit_status","nr_comenzi"]
    
    fig = px.pie(
        status_data,
        values="nr_comenzi",
        names="profit_status",
        title="Distributia Comenzilor Profitabile vs Neprofitabile"
    )



    return fig
