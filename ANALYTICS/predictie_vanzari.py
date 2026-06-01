import pandas as pd
import numpy as np
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import TimeSeriesSplit, cross_val_score
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
from statsmodels.tsa.stattools import adfuller
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.holtwinters import ExponentialSmoothing
import plotly.graph_objects as go
import plotly.express as px
import warnings
warnings.filterwarnings("ignore")
try:
    from pmdarima import auto_arima
except:
    auto_arima = None
from sqlalchemy import create_engine




def get_connection():
    return create_engine("postgresql://licenta:licenta123@localhost:5432/sales_db")




def check_database_schema():
    conn=get_connection()
    


    tables=["fact_sales","dim_date","dim_region","dim_product"]
    schema_info={}





    for table in tables:
        try:
            query=f"SELECT * FROM {table} LIMIT 0"
            df=pd.read_sql(query, conn)
            schema_info[table]=df.columns.tolist()
        except Exception as e:
            schema_info[table]=f"Error: {str(e)}"
    


    conn.dispose()


    return schema_info







def load_timeseries_data():
    conn=get_connection()
    query= """
    SELECT 
        dd.id as date_key,
        CAST(dd.date AS DATE) as date,
        r.region,
        p.category,
        SUM(fs.revenue) as daily_revenue,
        SUM(fs.quantity) as daily_quantity,
        COUNT(DISTINCT fs.source_order_id) as nr_orders
    FROM fact_sales fs
    JOIN dim_date dd ON fs.date_id = dd.id
    JOIN dim_region r ON fs.region_id = r.id
    JOIN dim_product p ON fs.product_id = p.id
    GROUP BY dd.id, CAST(dd.date AS DATE), r.region, p.category
    ORDER BY date ASC
    """



    df=pd.read_sql(query, conn)
    conn.dispose()



    return df






def prepare_forecast_data(df,metric="daily_revenue",region=None, category=None):
    df_forecast=df.copy()
    if region:
        df_forecast=df_forecast[df_forecast["region"]== region]



    if category:
        df_forecast=df_forecast[df_forecast["category"]== category]
    df_agg=df_forecast.groupby("date").agg({
        "daily_revenue":"sum",
        "daily_quantity":"sum",
        "nr_orders":"sum"
    }).reset_index()



    df_agg=df_agg.sort_values("date").reset_index(drop=True)




    return df_agg







def create_advanced_features(df,metric_col, lags=[7, 14, 30, 60, 90]):


    df_feat=df.copy()
    df_feat=df_feat.sort_values("date").reset_index(drop=True)


    for lag in lags:
        df_feat[f"{metric_col}_lag_{lag}"]=df_feat[metric_col].shift(lag)
    for window in [7, 14, 30, 60]:
        df_feat[f"{metric_col}_ma_{window}"]=df_feat[metric_col].rolling(window=window).mean()
    for span in [7, 30]:
        df_feat[f"{metric_col}_ewma_{span}"]=df_feat[metric_col].ewm(span=span).mean()
    for window in [7, 30]:
        df_feat[f"{metric_col}_std_{window}"]=df_feat[metric_col].rolling(window=window).std()





    df_feat[f"{metric_col}_roc_7"]=df_feat[metric_col].pct_change(7)
    df_feat[f"{metric_col}_roc_30"]= df_feat[metric_col].pct_change(30)
    df_feat = df_feat.replace([np.inf, -np.inf],np.nan)
    df_feat["trend"]=np.arange(len(df_feat))
    df_feat["day_of_week"]=pd.to_datetime(df_feat["date"]).dt.dayofweek
    df_feat["month"]=pd.to_datetime(df_feat["date"]).dt.month
    df_feat["quarter"]=pd.to_datetime(df_feat["date"]).dt.quarter
    df_feat["day_of_month"]= pd.to_datetime(df_feat["date"]).dt.day
    df_feat["day_of_year"]=pd.to_datetime(df_feat["date"]).dt.dayofyear
    df_feat["is_weekend"]= (pd.to_datetime(df_feat["date"]).dt.dayofweek>= 5).astype(int)



    for col in df_feat.columns:
        if col!="date" and df_feat[col].dtype!= "object":
            df_feat[col]= df_feat[col].fillna(0)


    df_feat=df_feat.replace([np.inf,-np.inf], 0)




    return df_feat




def test_stationarity(timeseries,name="Series"):
    adf_result=adfuller(timeseries.dropna(), autolag="AIC")



    try:
        adf_stat=float(adf_result[0])
        p_val=float(adf_result[1])
        crit_vals=adf_result[4] if len(adf_result)>4 else {}
    except (TypeError, IndexError, ValueError):
        adf_stat, p_val, crit_vals = 0.0, 1.0, {}
    



    return {
        "adf_statistic":adf_stat,
        "p_value":p_val,
        "is_stationary":p_val<0.05,
        "critical_values":crit_vals,
        "name": name
    }





def find_arima_order(timeseries, seasonal_period=7):


    if auto_arima is not None:
        try:
            model=auto_arima(timeseries,seasonal=False,stepwise=True, trace=False,error_action="ignore", suppress_warnings=True,max_p=10, max_d=3, max_q=10)
            return model.order
        except:
            return (1, 1, 1)
        



    return (1, 1, 1)







def train_arima_auto(timeseries,test_size=0.2, metric_col="daily_revenue"):
    split_idx=int(len(timeseries)* (1-test_size))
    ts_train=timeseries[:split_idx]
    ts_test=timeseries[split_idx:]




    if auto_arima is not None:
        try:
            model=auto_arima(ts_train, seasonal=False, stepwise=True,trace=False, error_action="ignore", suppress_warnings=True,max_p=10, max_d=3, max_q=10)
            arima_order=model.order
        except:
            arima_order=(1, 1, 1)
    else:
        arima_order=(1, 1, 1)






    try:
        arima_model=ARIMA(ts_train,order=arima_order)
        arima_fit=arima_model.fit()
        arima_train_pred=arima_fit.fittedvalues.values
        arima_test_pred=arima_fit.get_forecast(steps=len(ts_test)).predicted_mean.values
        arima_train_score=r2_score(ts_train[-len(arima_train_pred):],arima_train_pred)
        arima_test_score=r2_score(ts_test[:len(arima_test_pred)],arima_test_pred[:len(ts_test)])
        arima_test_mape=np.mean(np.abs((ts_test-arima_test_pred[:len(ts_test)]) / ts_test))
    except:
        arima_train_score, arima_test_score, arima_test_mape= -0.1, -0.1, 0.0
        arima_train_pred=np.zeros(len(ts_train))
        arima_test_pred=np.zeros(len(ts_test))





    return arima_train_score, arima_test_score, arima_order, arima_train_pred, arima_test_pred, arima_test_mape


def train_forecast_model(df,metric_col="daily_revenue",test_size=0.2):



    feature_cols=[col for col in df.columns if col not in ["date",metric_col]]
    X_df=df[feature_cols].copy()

    y = df[metric_col].values




    for col in X_df.columns:
        X_df[col]=X_df[col].replace([np.inf, -np.inf], np.nan)




    for col in X_df.columns:
        nan_count=X_df[col].isna().sum()
        if nan_count > 0:
            print(f"  {col}: {nan_count}")


    X_df=X_df.interpolate(method="linear",limit_direction="both", axis=0)
    for col in X_df.columns:
        if X_df[col].isna().sum()>0:
            median_val= X_df[col].median()
            if pd.isna(median_val):
                median_val= 0
            X_df[col].fillna(median_val, inplace=True)



    for col in X_df.columns:
        Q1=X_df[col].quantile(0.25)
        Q3=X_df[col].quantile(0.75)
        IQR=Q3 - Q1
        lower_bound=Q1-3* IQR
        upper_bound=Q3+3* IQR
        X_df[col]=X_df[col].clip(lower=max(lower_bound, -1e6), upper=min(upper_bound, 1e6))
    X_df = X_df.fillna(0)



    for col in X_df.columns:
        X_df[col]=pd.to_numeric(X_df[col],errors="coerce").fillna(0)
    assert not X_df.isnull().any().any(), "NaN values still present after cleaning"
    assert not np.isinf(X_df.values).any(), "Infinite values still present after cleaning"


    
    X=X_df.values
    scaler=StandardScaler()
    X_scaled=scaler.fit_transform(X)
    split_idx=int(len(X) * (1-test_size))
    X_train, X_test=X_scaled[:split_idx], X_scaled[split_idx:]
    y_train, y_test=y[:split_idx], y[split_idx:]



    gb_model=GradientBoostingRegressor(n_estimators=100, learning_rate=0.05,max_depth=5, min_samples_split=10, random_state=42)
    gb_model.fit(X_train, y_train)
    gb_train_pred=gb_model.predict(X_train)
    gb_test_pred=gb_model.predict(X_test)
    gb_train_score= r2_score(y_train,gb_train_pred)
    gb_test_score= r2_score(y_test,gb_test_pred)
    gb_train_mae= mean_absolute_error(y_train,gb_train_pred)
    gb_test_mae=mean_absolute_error(y_test,gb_test_pred)
    gb_test_mape= np.mean(np.abs((y_test- gb_test_pred)/y_test))




    tscv=TimeSeriesSplit(n_splits=3)
    gb_cv_scores=cross_val_score(gb_model,X_scaled,y,cv=tscv, scoring="r2")



    lr_model=Ridge(alpha=10.0)
    lr_model.fit(X_train,y_train)
    lr_train_pred=lr_model.predict(X_train)
    lr_test_pred=lr_model.predict(X_test)
    



    lr_train_score=r2_score(y_train,lr_train_pred)
    lr_test_score=r2_score(y_test,lr_test_pred)
    lr_train_mae=mean_absolute_error(y_train,lr_train_pred)
    lr_test_mae=mean_absolute_error(y_test,lr_test_pred)
    lr_test_mape= np.mean(np.abs((y_test-lr_test_pred)/y_test))
    lr_cv_scores=cross_val_score(lr_model,X_scaled,y,cv=tscv,scoring="r2")



    arima_train_score,arima_test_score,arima_order,arima_train_pred, arima_test_pred, arima_test_mape= (
        train_arima_auto(df[metric_col].values,test_size=test_size,metric_col=metric_col)
    )


    
    try:
        exp_model=ExponentialSmoothing(df[metric_col].values,trend="add",seasonal=None)
        exp_fit=exp_model.fit()
        exp_test_start=split_idx
        exp_forecast=exp_fit.fittedvalues[exp_test_start:]




        if len(exp_forecast)<len(y_test):
            exp_forecast=np.pad(exp_forecast, (0, len(y_test)-len(exp_forecast)),mode="edge")
        exp_smooth_test_score=r2_score(y_test[:len(exp_forecast)], exp_forecast[:len(y_test)])
        exp_smooth_test_mape=np.mean(np.abs((y_test[:len(exp_forecast)]- exp_forecast[:len(y_test)]) /y_test[:len(exp_forecast)]))
        exp_smooth_model = exp_fit


    except:
        exp_smooth_test_score=-1.0
        exp_smooth_test_mape=0.0
        exp_smooth_model=None
    feature_importance=pd.DataFrame({
        "feature":feature_cols,
        "importance": gb_model.feature_importances_
    }).sort_values("importance", ascending=False)



    best_overall_r2=max(gb_test_score,lr_test_score,arima_test_score)
    best_overall_r2=max(gb_test_score,lr_test_score,arima_test_score)




    return {
        "gb_train_score":gb_train_score,
        "gb_test_score":gb_test_score,
        "gb_train_mae":gb_train_mae,
        "gb_test_mae":gb_test_mae,
        "gb_test_mape":gb_test_mape,
        "gb_cv_mean":gb_cv_scores.mean(),
        "gb_cv_std":gb_cv_scores.std(),
        "gb_model": gb_model,
        "gb_test_pred": gb_test_pred,
        "lr_train_score": lr_train_score,
        "lr_test_score": lr_test_score,
        "lr_train_mae": lr_train_mae,
        "lr_test_mae": lr_test_mae,
        "lr_test_mape": lr_test_mape,
        "lr_cv_mean": lr_cv_scores.mean(),
        "lr_cv_std": lr_cv_scores.std(),
        "lr_model": lr_model,
        "lr_test_pred": lr_test_pred,
        "arima_train_score": arima_train_score,
        "arima_test_score": arima_test_score,
        "arima_order": arima_order,
        "arima_test_mape": arima_test_mape,
        "exp_smooth_test_score": exp_smooth_test_score,
        "exp_smooth_test_mape": exp_smooth_test_mape,
        "exp_smooth_model": exp_smooth_model,
        "y_test": y_test,
        "y_train": y_train,
        "feature_importance": feature_importance,
        "dataset_size": len(df),
        "train_size": len(y_train),
        "test_size": len(y_test),
        "best_overall_r2": best_overall_r2,
        "scaler": scaler
    }






def generate_forecast(df,model_info, metric_col,forecast_days=30):
    feature_cols=[col for col in df.columns if col not in ["date",metric_col]]



    X_latest=df[feature_cols].iloc[-1:].values
    X_latest_scaled=model_info["scaler"].transform(X_latest)


    last_actual_value=df[metric_col].iloc[-1]
    last_date = df["date"].max()



    future_dates=pd.date_range(start=last_date+pd.Timedelta(days=1),periods=forecast_days,freq="D")
    gb_forecasts= []
    lr_forecasts=[]
    ensemble_forecasts=[]




    for i, date in enumerate(future_dates):
        gb_pred=model_info["gb_model"].predict(X_latest_scaled)[0]
        lr_pred= model_info["lr_model"].predict(X_latest_scaled)[0]
        ensemble_pred= 0.5*gb_pred + 0.5* lr_pred
        hist_mean= df[metric_col].mean()
        hist_std= df[metric_col].std()
        gb_pred= np.clip(gb_pred, hist_mean- 3*hist_std, hist_mean+ 3*hist_std)
        lr_pred=np.clip(lr_pred,hist_mean- 3*hist_std,hist_mean+ 3*hist_std)
        ensemble_pred =np.clip(ensemble_pred, hist_mean- 3*hist_std,hist_mean +3*hist_std)



        gb_forecasts.append(gb_pred)
        lr_forecasts.append(lr_pred)



        ensemble_forecasts.append(ensemble_pred)



    df_forecast=pd.DataFrame({
        "date":future_dates,
        "forecast":ensemble_forecasts,
        "gb_forecast":gb_forecasts,
        "lr_forecast": lr_forecasts,
        "rf_forecast": gb_forecasts
    })




    return df_forecast






def plot_historical_trend(df_hist, metric_col="daily_revenue",title="Trend istoric"):
    fig=go.Figure()
    fig.add_trace(go.Scatter(x=df_hist["date"], y=df_hist[metric_col],mode="lines",name="Historic",line=dict(color="blue")))
    fig.update_layout(title=title, xaxis_title="Date",yaxis_title=metric_col,hovermode="x unified")



    return fig




def plot_forecast_chart(df_hist,df_forecast,metric_col="daily_revenue",title="Predictie vanzari"):
    fig=go.Figure()


    fig.add_trace(go.Scatter(x=df_hist["date"],y=df_hist[metric_col],mode="lines", name="Istoric", line=dict(color="blue")))
    fig.add_trace(go.Scatter(x=df_forecast["date"], y=df_forecast["forecast"],mode="lines+markers", name="Ensemble (GB+Ridge)",line=dict(color="red", width=3)))
    fig.add_trace(go.Scatter(x=df_forecast["date"], y=df_forecast["gb_forecast"],mode="lines", name="Gradient Boosting", line=dict(dash="dash")))
    fig.add_trace(go.Scatter(x=df_forecast["date"], y=df_forecast["lr_forecast"],mode="lines", name="Ridge", line=dict(dash="dot")))
    fig.update_layout(title=title, xaxis_title="Date",yaxis_title=metric_col,hovermode="x unified", height=500)



    return fig


