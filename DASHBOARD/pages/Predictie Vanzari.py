import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import create_engine
from pandas.api.types import is_numeric_dtype
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor

st.set_page_config(page_title="Predictie Vanzari", layout="wide")

@st.cache_resource
def get_connection():
    DB_URI="postgresql+psycopg2://licenta:licenta123@localhost:5432/sales_db"
    return create_engine(DB_URI)

@st.cache_data(ttl=3600)
def load_timeseries_data():
    engine=get_connection()
    query="""
        SELECT 
            d.date,
            d.year,
            d.month,
            d.quarter,
            r.region,
            p.category,
            SUM(f.revenue) as daily_revenue,
            SUM(f.quantity) as daily_quantity,
            SUM(f.profit) as daily_profit,
            COUNT(DISTINCT f.id) as nr_orders
        FROM fact_sales f
        JOIN dim_date d ON f.date_id= d.id
        JOIN dim_region r ON f.region_id= r.id
        JOIN dim_product p ON f.product_id =p.id
        GROUP BY d.date,d.year,d.month,d.quarter, r.region, p.category
        ORDER BY d.date ASC
    """


    return pd.read_sql(query, engine)




def prepare_forecast_data(df, metric="daily_revenue",region=None,category=None):
    df_forecast = df.copy()
    
    if region:
        df_forecast = df_forecast[df_forecast["region"] == region]
    if category:
        df_forecast = df_forecast[df_forecast["category"] == category]
    
    df_agg =df_forecast.groupby("date").agg({
        "daily_revenue":"sum",
        "daily_quantity": "sum",
        "daily_profit": "sum",
        "nr_orders":"sum"
    }).reset_index()
    df_agg = df_agg.sort_values("date").reset_index(drop=True)



    return df_agg



def create_lag_features(df, metric_col, lags=[7, 14, 30]):
    df_feat = df.copy()
    
    for lag in lags:
        df_feat[f"{metric_col}_lag_{lag}"]=df_feat[metric_col].shift(lag)
    for window in [7, 14, 30]:
        df_feat[f"{metric_col}_ma_{window}"]= df_feat[metric_col].rolling(window=window).mean()
    
    df_feat["trend"]= range(len(df_feat))
    df_feat["day_of_week"]= pd.to_datetime(df_feat["date"]).dt.dayofweek
    df_feat["month"] =pd.to_datetime(df_feat["date"]).dt.month
    


    return df_feat.dropna()

def train_forecast_model(df, metric_col="daily_revenue", test_size=0.2):
    feature_cols=[col for col in df.columns if col not in ["date", metric_col]]
    X= df[feature_cols].values
    y= df[metric_col].values
    
    split_idx=int(len(df)*(1 - test_size))


    X_train, X_test= X[:split_idx], X[split_idx:]
    y_train, y_test =y[:split_idx], y[split_idx:]
    
    scaler=StandardScaler()
    X_train_scaled=scaler.fit_transform(X_train)
    X_test_scaled= scaler.transform(X_test)
    
    rf_model= RandomForestRegressor(n_estimators=100, random_state=42,n_jobs=-1)
    rf_model.fit(X_train_scaled, y_train)
    rf_train_score=rf_model.score(X_train_scaled, y_train)
    rf_test_score= rf_model.score(X_test_scaled, y_test)
    
    lr_model=LinearRegression()
    lr_model.fit(X_train_scaled, y_train)
    lr_train_score=lr_model.score(X_train_scaled, y_train)
    lr_test_score= lr_model.score(X_test_scaled, y_test)
    


    return {
        "rf_model":rf_model,
        "lr_model":lr_model,
        "scaler": scaler,
        "feature_cols":feature_cols,
        "rf_train_score": rf_train_score,
        "rf_test_score": rf_test_score,
        "lr_train_score":lr_train_score,
        "lr_test_score":lr_test_score,
        "y_test":y_test
    }

def generate_forecast(df, model_info, metric_col, forecast_days=30):
    last_row=df.iloc[-1].copy()
    forecasts= []
    current_df= df.copy()
    


    feature_cols=model_info["feature_cols"]
    scaler=model_info["scaler"]
    rf_model= model_info["rf_model"]
    lr_model= model_info["lr_model"]
    

    for i in range(forecast_days):
        last_date=pd.to_datetime(last_row["date"])
        next_date=last_date+pd.Timedelta(days=1)
        
        new_row = {
            "date":next_date,
            "trend": last_row["trend"]+ 1,
            "day_of_week":next_date.dayofweek,
            "month": next_date.month
        }
        


        for col in feature_cols:
            if col not in ["date", "trend", "day_of_week", "month"]:
                if col in last_row.index:
                    new_row[col] = last_row[col]
                else:
                    new_row[col] = 0
        
        X_new=np.array([new_row[col] for col in feature_cols]).reshape(1, -1)
        X_new_scaled=scaler.transform(X_new)
        
        rf_pred=rf_model.predict(X_new_scaled)[0]
        lr_pred=lr_model.predict(X_new_scaled)[0]
        

        m=0.6 * rf_pred + 0.4 * lr_pred
        
        forecasts.append({
            "date": next_date,
            "forecast": m,
            "rf_forecast":rf_pred,
            "lr_forecast":lr_pred
        })
        

        last_row = pd.Series({
            "date": next_date,
            metric_col: m,
            **new_row
        })
    



    return pd.DataFrame(forecasts)




def plot_historical_trend(df_hist, metric_col="daily_revenue", title="Trend istoric"):
    fig = go.Figure()
    

    fig.add_trace(go.Scatter(
        x=df_hist["date"],
        y=df_hist[metric_col],
        name="Valoare reala"
    ))
    


    fig.update_layout(
        title=title,
        xaxis_title="Data",
        yaxis_title="Valoare $",
    )


    return fig




def plot_forecast_chart(df_hist, df_forecast, metric_col="daily_revenue", title="Predictie vanzari"):
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df_hist["date"],
        y=df_hist[metric_col],
        name="Valoare reala",
    ))
    

    fig.add_trace(go.Scatter(
        x=df_forecast["date"],
        y=df_forecast["forecast"],
        name="Predictie (Ensemble)",
    ))
    
    fig.add_trace(go.Scatter(
        x=df_forecast["date"],
        y=df_forecast["rf_forecast"],
        name="Random Forest"
    ))
    
    fig.add_trace(go.Scatter(
        x=df_forecast["date"],
        y=df_forecast["lr_forecast"],
        name="Linear Regression"
    ))
    

    fig.update_layout(
        title=title,
        xaxis_title="Data",
        yaxis_title="Valoare $",
        legend=dict(x=0.01, y=0.99)
    )




    return fig




def plot_model_performance(model_info):
    models=["Random Forest", "Linear Regression"]
    train_scores=[model_info["rf_train_score"], model_info["lr_train_score"]]
    test_scores=[model_info["rf_test_score"], model_info["lr_test_score"]]
    
    fig = go.Figure(data=[
        go.Bar(name="Train Score", x=models, y=train_scores),
        go.Bar(name="Test Score", x=models, y=test_scores)
    ])
    

    fig.update_layout(
        title="Performanta Modelelor (R² Score)",
        barmode="group",
        yaxis_title="R² Score"
    )


    return fig




def plot_forecast_summary(df_forecast, metric_col="daily_revenue"):
    fig = px.histogram(
        df_forecast,
        x="forecast",
        nbins=20,
        title="Distributia Predictiilor",
        labels={"forecast": "Valoare Predictie $"},
    )


    
    return fig






def main():
    st.title("Predictie Vanzari")
    st.markdown("Model Machine Learning pentru predictia vanzarilor")
    st.markdown("---")

    df_raw = load_timeseries_data()



    with st.sidebar:
        st.header("Configurare Model")
        metric_selected=st.selectbox(
            "Selecteaza metrica de predictie:",
            options=["daily_revenue","daily_quantity","daily_profit","nr_orders"],
            format_func=lambda x: {
                "daily_revenue":"Venit Zilnic",
                "daily_quantity":"Cantitate Vanduta",
                "daily_profit":"Profit Zilnic",
                "nr_orders":"Numar Comenzi"
            }[x]
        )


        
        forecast_days=st.slider("Zile de predictie:",min_value=7,max_value=90,value=30,step=7)
        

        region_filter = st.selectbox(
            "Filtreaza dupa regiuneȘ",
            options=[None]+sorted(df_raw["region"].unique().tolist()),
            format_func=lambda x:"Toate regiunile" if x is None else x
        )


        
        category_filter= st.selectbox(
            "Filtreaza dupa categorie:",
            options=[None]+sorted(df_raw["category"].unique().tolist()),
            format_func=lambda x:"Toate categoriile" if x is None else x
        )






    df_forecast_prep=prepare_forecast_data(df_raw,metric=metric_selected,region=region_filter, category=category_filter)
    df_features = create_lag_features(df_forecast_prep, metric_col=metric_selected)
    
    with st.spinner("Se antreneaza modelul"):
        model_info=train_forecast_model(df_features, metric_col=metric_selected)

    with st.spinner(f"Se genereaza predictii pentru {forecast_days} zile"):
        df_forecasted=generate_forecast(df_features,model_info, metric_selected,forecast_days=forecast_days)





    st.markdown("""
    <div style="display:flex; align-items:center; gap:10px;">
    <div style="flex:1; height:1px; background-color:gray;"></div>
    <div style="font-size:30px;font-weight:bold;">
        Date Istorice
    </div>

    <div style="flex:1; height:1px; background-color:gray;"></div>
    </div>
    """, unsafe_allow_html=True)

    fig_hist= plot_historical_trend(df_forecast_prep,metric_col=metric_selected)
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
    fig_forecast=plot_forecast_chart(df_forecast_prep, df_forecasted, metric_col=metric_selected)
    st.plotly_chart(fig_forecast)
    st.markdown("---")




    col1, col2=st.columns(2)
    with col1:
        st.subheader("Performanta modelelor")
        fig_perf=plot_model_performance(model_info)
        st.plotly_chart(fig_perf)
    
    with col2:
        st.subheader("Distributia predictiilor")
        fig_dist=plot_forecast_summary(df_forecasted)
        st.plotly_chart(fig_dist)
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
    col1,col2,col3,col4,col5 =st.columns(5)
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
        st.metric(
            label="Abatere Std",
            value=f"${df_forecasted["forecast"].std():,.2f}"
        )
    with col5:
        avg_historical=df_forecast_prep[metric_selected].mean()
        percent_change=((df_forecasted["forecast"].mean()-avg_historical) /avg_historical * 100)
        st.metric(
            label="Schimbare vs Istoric",
            value=f"{percent_change:+.2f}%"
        )
    st.markdown("---")



    with st.expander("Tabel Predictii"):
        forecast_display=df_forecasted.copy()
        forecast_display["date"]=forecast_display["date"].dt.strftime("%Y-%m-%d")
        forecast_display["forecast"] = forecast_display["forecast"].apply(lambda x: f"${x:,.2f}")
        forecast_display["rf_forecast"] =forecast_display["rf_forecast"].apply(lambda x: f"${x:,.2f}")
        forecast_display["lr_forecast"]= forecast_display["lr_forecast"].apply(lambda x: f"${x:,.2f}")
        forecast_display.columns=["Data","Predictie Ensemble","Random Forest","Linear Regression"]
        st.dataframe(forecast_display)


    with st.expander("Informatii Model"):
        info_col1,info_col2=st.columns(2)
        with info_col1:
            st.write("**Random Forest Model:**")
            st.write(f"- Train R² Score: {model_info["rf_train_score"]:.4f}")
            st.write(f"- Test R² Score: {model_info["rf_test_score"]:.4f}")
        with info_col2:
            st.write("**Linear Regression Model:**")
            st.write(f"- Train R² Score: {model_info["lr_train_score"]:.4f}")
            st.write(f"- Test R² Score: {model_info["lr_test_score"]:.4f}")
        
        st.write("**Ensemble Model:** 60% Random Forest + 40% Linear Regression")



if __name__ == "__main__":
    main()
