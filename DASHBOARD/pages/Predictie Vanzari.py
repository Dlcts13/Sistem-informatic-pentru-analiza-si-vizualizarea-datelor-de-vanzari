import streamlit as st
import pandas as pd
import sys
import os
from streamlit_autorefresh import st_autorefresh
from sqlalchemy import text
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from DB.connection import get_engine

current_dir=os.path.dirname(os.path.abspath(__file__))
parent_dir=os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, parent_dir)
st.set_page_config(page_title="Predictie Vanzari", layout="wide")

from ANALYTICS import predictie_vanzari as pv

if not st.session_state.get("authentication_status"):
    st.error("Acces refuzat!")
    st.stop()

if st.session_state.get("role") != "manager":
    st.error("Acces neautorizat!")
    st.stop()

st_autorefresh(interval=300000, limit=None, key="smart_refresh_predictie")

def get_data_version():
    engine = get_engine()
    query = "SELECT COUNT(*), MAX(created_at) FROM fact_sales;"
    with engine.connect() as conn:
        result = conn.execute(text(query)).fetchone()
    return f"{result[0]}_{result[1]}"

current_version = get_data_version()

if "last_data_version_pred" not in st.session_state:
    st.session_state["last_data_version_pred"] = current_version

if current_version != st.session_state["last_data_version_pred"]:
    st.toast("Date noi primite in platforma! Se actualizeaza ...")
    st.session_state["last_data_version_pred"] = current_version


def main():
    st.title("Predictie Vanzari")
    st.markdown("Model Machine Learning pentru predictia vanzarilor")
    st.markdown("---")

    df_raw = pv.load_timeseries_data(version_hash=current_version)



    with st.sidebar:
        st.header("Configurare Model")
        metric_selected=st.selectbox(
            "Selecteaza metrica de predictie:",
            options=["daily_revenue","daily_quantity","nr_orders"],
            format_func=lambda x: {
                "daily_revenue":"Venit Zilnic",
                "daily_quantity":"Cantitate Vanduta",
                "nr_orders":"Numar Comenzi"
            }[x]
        )


        
        forecast_days=st.slider("Zile de predictie:",min_value=7,max_value=90,value=30,step=7)
        

        region_filter = st.selectbox(
            "Filtreaza dupa regiune",
            options=[None]+sorted(df_raw["region"].unique().tolist()),
            format_func=lambda x:"Toate regiunile" if x is None else x
        )


        
        category_filter= st.selectbox(
            "Filtreaza dupa categorie:",
            options=[None]+sorted(df_raw["category"].unique().tolist()),
            format_func=lambda x:"Toate categoriile" if x is None else x
        )






    df_forecast_prep=pv.prepare_forecast_data(df_raw,metric=metric_selected,region=region_filter, category=category_filter)
    df_features = pv.create_advanced_features(df_forecast_prep, metric_col=metric_selected)
    
    with st.spinner("Se antreneaza modelul"):
        model_info=pv.train_forecast_model(df_features, metric_col=metric_selected)

    with st.spinner(f"Se genereaza predictii pentru {forecast_days} zile"):
        df_forecasted=pv.generate_forecast(df_features,model_info, metric_selected,forecast_days=forecast_days)





    st.markdown("""
    <div style="display:flex; align-items:center; gap:10px;">
    <div style="flex:1; height:1px; background-color:gray;"></div>
    <div style="font-size:30px;font-weight:bold;">
        Date Istorice
    </div>

    <div style="flex:1; height:1px; background-color:gray;"></div>
    </div>
    """, unsafe_allow_html=True)

    fig_hist= pv.plot_historical_trend(df_forecast_prep,metric_col=metric_selected)
    st.plotly_chart(fig_hist)
    st.markdown("---")




    st.markdown("""
    <div style="display:flex; align-items:center; gap:10px;">
    <div style="flex:1; height:1px; background-color:gray;"></div>
    <div style="font-size:30px;font-weight:bold;">
        Predictii pentru urmatoarele zile
    </div>

    <div style="flex:1; height:1px; background-color:gray;"></div>
    </div>
    """, unsafe_allow_html=True)
    fig_forecast=pv.plot_forecast_chart(df_forecast_prep, df_forecasted, metric_col=metric_selected)
    st.plotly_chart(fig_forecast)
    st.markdown("---")




    st.markdown("""
    <div style="display:flex; align-items:center; gap:10px;">
    <div style="flex:1; height:1px; background-color:gray;"></div>
    <div style="font-size:30px;font-weight:bold;">
        Statistici predictie
    </div>

    <div style="flex:1; height:1px; background-color:gray;"></div>
    </div>
    """, unsafe_allow_html=True)
    col1,col2,col3,col4 =st.columns(4)

    
    with col1:
        st.metric(
            label="Predictie Medie",
            value=f"${df_forecasted["forecast"].mean():,.2f}"
        )
    with col2:
        st.metric(
            label="Predictie Min",
            value=f"${df_forecasted["forecast"].min():,.2f}"
        )
    with col3:
        st.metric(
            label="Predictie Max",
            value=f"${df_forecasted["forecast"].max():,.2f}"
        )
    with col4:
        avg_historical=df_forecast_prep[metric_selected].mean()
        percent_change=((df_forecasted["forecast"].mean()-avg_historical)/avg_historical * 100)
        st.metric(
            label="Schimbare vs Istoric",
            value=f"{percent_change:+.2f}%"
        )


    st.markdown("---")



    with st.expander("Tabel Predictii"):
        forecast_display=df_forecasted[["date","forecast","rf_forecast","lr_forecast"]].copy()
        forecast_display["date"]=forecast_display["date"].dt.strftime("%Y-%m-%d")
        forecast_display["forecast"] = forecast_display["forecast"].apply(lambda x: f"${x:,.2f}")
        forecast_display["rf_forecast"] =forecast_display["rf_forecast"].apply(lambda x: f"${x:,.2f}")
        forecast_display["lr_forecast"]= forecast_display["lr_forecast"].apply(lambda x: f"${x:,.2f}")
        forecast_display.columns=["Data","Predictie Ensemble","Random Forest","Linear Regression"]
        st.dataframe(forecast_display)


if __name__ == "__main__":
    main()
