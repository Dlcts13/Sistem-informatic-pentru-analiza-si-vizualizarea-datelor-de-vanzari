import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import create_engine
from pandas.api.types import is_numeric_dtype

st.set_page_config(page_title="Vanzari Generale", layout="wide")


@st.cache_resource
def get_connection():
    DB_URI= "postgresql+psycopg2://licenta:licenta123@localhost:5432/sales_db"
    return create_engine(DB_URI)

@st.cache_data(ttl=3600)
def load_dashboard_data():
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
    profit_margin=(total_profit/ total_revenue*100) if total_revenue > 0 else 0
    avg_order_value =total_revenue /total_orders if total_orders > 0 else 0
    
    return {
        "total_orders":total_orders,
        "total_revenue":total_revenue,
        "total_profit":total_profit,
        "profit_margin":profit_margin,
        "avg_order_value": avg_order_value
    }



def get_trend_data(df):
    df_trend = df.groupby("date").agg({
        "revenue": "sum",
        "profit": "sum",
        "order_id":"nunique"
    }).reset_index()


    df_trend.columns = ["date","revenue","profit","nr_orders"]



    return df_trend

def get_regional_performance(df):
    regional_data=df.groupby("region").agg({
        "revenue":"sum",
        "profit":"sum",
        "order_id": "nunique"
    }).reset_index()

    regional_data.columns=["region", "revenue", "profit", "orders"]
    regional_data = regional_data.sort_values("revenue", ascending=False)




    return regional_data

def get_category_performance(df):
    category_data= df.groupby("category").agg({
        "revenue":"sum",
        "profit": "sum",
        "quantity": "sum"
    }).reset_index()

    category_data.columns=["category", "revenue","profit","quantity"]


    category_data["profit_rate"] =(category_data["profit"]/category_data["revenue"] * 100).round(2)





    return category_data.sort_values("revenue",ascending=False)


def plot_trend_chart(df_trend):
    fig = go.Figure()
    
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
        labels={"revenue": "Venit Total $","region": "Regiune","profit": "Profit $"},
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
        labels={"revenue": "Venit Total $","category": "Categorie","profit_rate": "Rata Profit (%)"},
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

def main():
    st.title("Vanzari Generale")
    st.markdown("Analiza performantei vanzarilor din intreaga organizatie")
    st.markdown("---")


    df = load_dashboard_data()


    with st.sidebar:
        st.header("Filtre")
        lista_regiuni=sorted(df["region"].unique().tolist())
        lista_ani=sorted(df["year"].unique().tolist(), reverse=True)
        lista_categorii = sorted(df["category"].unique().tolist())


        regiuni_selectate = st.multiselect(
            "Selecteaza Regiuni:",
            options=lista_regiuni,
            default=lista_regiuni,
            key="regions"
        )
        


        ani_selectati = st.multiselect(
            "Selecteaza Ani:",
            options=lista_ani,
            default=[lista_ani[0]] if lista_ani else [],
            key="years"
        )
        
        categorii_selectate = st.multiselect(
            "Selecteaza Categorii:",
            options=lista_categorii,
            default=lista_categorii,
            key="categories"
        )







    df_filtered = df[
        (df["region"].isin(regiuni_selectate)) & 
        (df["year"].isin(ani_selectati)) &
        (df["category"].isin(categorii_selectate))
    ]





    st.markdown("""
    <div style="display:flex; align-items:center; gap:10px;">
    <div style="flex:1; height:1px; background-color:gray;"></div>
    <div style="font-size:30px;font-weight:bold;">
        Indicatori Cheie de Performanta KPIs
    </div>

    <div style="flex:1; height:1px; background-color:gray;"></div>
    </div>
    """, unsafe_allow_html=True)



    kpis = calculate_kpis(df_filtered)
    
    col1,col2,col3,col4,col5 =st.columns(5)
    with col1:
        st.metric(
            label="Comenzi",
            value=f"{kpis['total_orders']:,}",
            delta="Total comenzi"
        )
    with col2:
        st.metric(
            label="Venit Total",
            value=f"${kpis['total_revenue']:,.2f}",
            delta="Total venituri"
        )
    with col3:
        st.metric(
            label="Profit Total",
            value=f"${kpis['total_profit']:,.2f}",
            delta="Total profit"
        )
    with col4:
        st.metric(
            label="Marja Profit",
            value=f"{kpis['profit_margin']:.2f}%",
            delta="% din venit"
        )
    with col5:
        st.metric(
            label="Valoare Medie Comanda",
            value=f"${kpis['avg_order_value']:,.2f}",
            delta="AOV"
        )



    st.markdown("---")
    


    st.markdown("""
    <div style="display:flex; align-items:center; gap:10px;">
    <div style="flex:1; height:1px; background-color:gray;"></div>
    <div style="font-size:30px;font-weight:bold;">
        Analiza trendurilor
    </div>

    <div style="flex:1; height:1px; background-color:gray;"></div>
    </div>
    """, unsafe_allow_html=True)



    df_trend=get_trend_data(df_filtered)
    fig_trend=plot_trend_chart(df_trend)
    st.plotly_chart(fig_trend)


    st.markdown("---")




    col1,col2 =st.columns(2)
    with col1:
        regional_data=get_regional_performance(df_filtered)
        fig_regional=plot_regional_performance(regional_data)
        st.plotly_chart(fig_regional)
    with col2:
        category_data=get_category_performance(df_filtered)
        fig_category= plot_category_performance(category_data)
        st.plotly_chart(fig_category)


    st.markdown("---")






    col1,col2=st.columns(2)
    with col1:
        fig_status=plot_profit_status(df_filtered)
        st.plotly_chart(fig_status)
    with col2:
        st.subheader("Rezumat Regional")
        regional_data_display=regional_data.copy()
        regional_data_display.columns= ["Regiune", "Venit $", "Profit $" ,"Comenzi"]
        st.dataframe(regional_data_display)




if __name__ == "__main__":
    main()