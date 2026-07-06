import streamlit as st
import sys
import os
from streamlit_autorefresh import st_autorefresh
from sqlalchemy import text
import pandas as pd
current_dir=os.path.dirname(os.path.abspath(__file__))
parent_dir=os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, parent_dir)
from DB.connection import get_engine

st.set_page_config(page_title="Analiza Produse", layout="wide")

from ANALYTICS import analiza_produse as ap

if not st.session_state.get("authentication_status"):
    st.error("Acces refuzat!")
    st.stop()

if st.session_state.get("role") != "manager":
    st.error("Acces neautorizat!")
    st.stop()

st_autorefresh(interval=30000, limit=None, key="smart_refresh_analiza")

def get_data_version():
    engine = get_engine()
    query = "SELECT COUNT(*), MAX(created_at) FROM fact_sales;"
    with engine.connect() as conn:
        result = conn.execute(text(query)).fetchone()
    return f"{result[0]}_{result[1]}"

current_version = get_data_version()

if "last_data_version" not in st.session_state:
    st.session_state["last_data_version"] = current_version

if current_version != st.session_state["last_data_version"]:
    st.toast("Date noi primite in platforma! Se actualizeaza ...")
    st.session_state["last_data_version"] = current_version


def main():
    st.title("Analiza performantei produselor")
    st.markdown("Analiza detaliata a vanzarilor si a profitabilitatii pe produse, categorii si branduri")
    st.markdown("---")
    df_products = ap.load_product_data(version_hash=current_version)



    st.markdown("""
    <div style="display:flex; align-items:center; gap:10px;">
    <div style="flex:1; height:1px; background-color:gray;"></div>
    <div style="font-size:30px;font-weight:bold;">
        Indicatori cheie KPIs
    </div>

    <div style="flex:1; height:1px; background-color:gray;"></div>
    </div>
    """, unsafe_allow_html=True)




    kpis=ap.calculate_product_kpis(df_products)
    col1,col2,col3= st.columns(3)
    with col1:
        st.metric(label="Total Produse", value=f"{kpis["total_products"]:,}")
    with col2:
        st.metric(label="Total Branduri", value=f"{kpis["total_brands"]:,}")
    with col3:
        st.metric(label="Total Categorii", value=f"{kpis["total_categories"]:,}")
    st.markdown("---")
    




    col4,col5,col6=st.columns(3)
    with col4:
        st.metric(label="Venit Total", value=f"${kpis["total_revenue"]:,.2f}")
    with col5:
        st.metric(label="Profit Total", value=f"${kpis["total_profit"]:,.2f}")
    with col6:
        st.metric(label="Marja Profit Medie", value=f"{kpis["avg_profit_margin"]:.2f}%")

    st.markdown("---")







    st.markdown("""
    <div style="display:flex; align-items:center; gap:10px;">
    <div style="flex:1; height:1px; background-color:gray;"></div>
    <div style="font-size:30px;font-weight:bold;">
        Analiza pe categorii
    </div>

    <div style="flex:1; height:1px; background-color:gray;"></div>
    </div>
    """, unsafe_allow_html=True)



    category_data=ap.get_category_summary(df_products)
    




    col1, col2=st.columns(2)
    with col1:
        fig_cat_pie=ap.plot_category_pie(category_data)
        st.plotly_chart(fig_cat_pie)
    
    with col2:
        fig_cat_bar=ap.plot_category_bar(category_data)
        st.plotly_chart(fig_cat_bar)
    st.markdown("---")







    st.markdown("""
    <div style="display:flex; align-items:center; gap:10px;">
    <div style="flex:1; height:1px; background-color:gray;"></div>
    <div style="font-size:30px;font-weight:bold;">
        Analiza pe branduri
    </div>

    <div style="flex:1; height:1px; background-color:gray;"></div>
    </div>
    """, unsafe_allow_html=True)



    brand_data=ap.get_brand_summary(df_products)
    fig_brands=ap.plot_top_brands(brand_data)
    st.plotly_chart(fig_brands)

    with st.expander("Tabel Branduri"):
        brand_display=brand_data.copy()
        brand_display.columns = ["Brand","Venit $","Profit $","Cantitate Vanduta","Nr. Produse","Marja Profit (%)"]
        st.dataframe(brand_display)
    st.markdown("---")










    st.markdown("""
    <div style="display:flex; align-items:center; gap:10px;">
    <div style="flex:1; height:1px; background-color:gray;"></div>
    <div style="font-size:30px;font-weight:bold;">
        Top produse dupa venit
    </div>

    <div style="flex:1; height:1px; background-color:gray;"></div>
    </div>
    """, unsafe_allow_html=True)




    top_products_data=ap.get_top_products(df_products)
    fig_top=ap.plot_top_products(top_products_data)
    st.plotly_chart(fig_top)




    col1,col2=st.columns(2)
    with col1:
        with st.expander("Detalii Top Produse"):
            top_display=top_products_data[["name","category","subcategory","brand","total_revenue","total_profit","total_quantity","nr_tranzactii", "profit_margin"]].copy()
            top_display.columns=["Produs","Categorie","Subcategorie","Brand","Venit $", "Profit $","Cantitate","Tranzactii","Marja (%)"]
            st.dataframe(top_display)
    with col2:
        with st.expander("Produse cu performanta scazuta"):
            low_perf_data=ap.get_low_performers(df_products)
            if not low_perf_data.empty:
                low_display=low_perf_data.copy()
                low_display.columns= ["Produs","Categorie","Subcategorie","Brand","Venit $","Profit $", "Marja (%)"]
                st.dataframe(low_display)
            else:
                st.info("Nu exista produse cu profit negativ")

    st.markdown("---")




    with st.expander("Rezumat Categorii"):
        cat_display =category_data.copy()
        cat_display.columns =["Categorie","Venit $","Profit $","Cantitate","Nr. Produse","Marja Profit (%)"]
        st.dataframe(cat_display)






if __name__ == "__main__":
    main()