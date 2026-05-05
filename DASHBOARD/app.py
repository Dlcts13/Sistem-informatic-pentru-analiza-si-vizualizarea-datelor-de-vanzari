import streamlit as st
import pandas as pd
import numpy as np
from sqlalchemy import create_engine


st.set_page_config(page_title="Sales Dashboard", layout="wide")

@st.cache_resource
def get_connection():
    DB_URI = "postgresql+psycopg2://licenta:licenta123@localhost:5432/sales_db"
    return create_engine(DB_URI)

@st.cache_data(ttl=3600)
def get_kpi_data():
    engine= get_connection()

    query= """ 
    SELECT 
    COUNT(id) AS total_orders,
    SUM(revenue) AS total_revenue,
    SUM(profit) AS total_profit
    FROM fact_sales
    """

    return pd.read_sql(query,engine)


def main():
    st.title("Platforma de Analiza Vanzari")
    st.subheader("KPIs")

    df_kpi=get_kpi_data()
    col1,col2,col3=st.columns(3)

    with col1:
        st.metric(label="Numar total comenzi:", value=f"{df_kpi["total_orders"].iloc[0]:,}")

    with col2:
        st.metric(label="Venit total:", value=f"{df_kpi["total_revenue"].iloc[0]:,.2f}")

    with col3:
        st.metric(label="Profit total:",value=f"{df_kpi["total_profit"].iloc[0]:,.2f}")


if __name__=="__main__":
    main()