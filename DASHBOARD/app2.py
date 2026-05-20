import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine

st.set_page_config(page_title="Sales Dashboard", layout="wide")

@st.cache_resource
def get_connection():
    DB_URI = "postgresql+psycopg2://licenta:licenta123@localhost:5432/sales_db"
    return create_engine(DB_URI)

@st.cache_data(ttl=3600)
def get_kpi_data():
    engine = get_connection()
    query = """
        SELECT 
            COUNT(id) AS total_orders,
            SUM(revenue) AS total_revenue,
            SUM(profit) AS total_profit
        FROM fact_sales
    """
    return pd.read_sql(query, engine)

@st.cache_data(ttl=3600)
def get_trend_data():
    engine = get_connection()
    query = """
        SELECT 
            d.date,
            SUM(f.revenue) AS daily_revenue
        FROM fact_sales f
        JOIN dim_date d ON f.date_id = d.id
        GROUP BY d.date
        ORDER BY d.date
    """
    return pd.read_sql(query, engine)

def main():
    st.sidebar.header("Filtreaza Datele")
    st.sidebar.info("filtre")
    
    st.title("Platforma de analiza")
    st.markdown("---")
    
    st.subheader("Indicatori de Performanta")
    df_kpi = get_kpi_data()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="Numar total comenzi", value=f"{df_kpi['total_orders'].iloc[0]:,}")
    with col2:
        st.metric(label="Venit total $", value=f"{df_kpi['total_revenue'].iloc[0]:,.2f}")
    with col3:
        st.metric(label="Profit total $", value=f"{df_kpi['total_profit'].iloc[0]:,.2f}")

    st.markdown("<br>", unsafe_allow_html=True)

    st.subheader("Evolutie venituri in timp")
    df_trend = get_trend_data()
    
    if not df_trend.empty:
        fig = px.line(
            df_trend, 
            x="date", 
            y="daily_revenue", 
            title="Venituri Zilnice",
            labels={"date": "Data Comenzii", "daily_revenue": "Venit ($)"},
            template="plotly_white"
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Lipsa de date")

if __name__ == "__main__":
    main()