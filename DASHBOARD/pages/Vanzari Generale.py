import streamlit as st
import sys
import os
current_dir= os.path.dirname(os.path.abspath(__file__))
parent_dir=os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, parent_dir)

from ANALYTICS import vanzari_generale as vg

st.set_page_config(page_title="Vanzari Generale", layout="wide")




def main():
    st.title("Vanzari Generale")
    st.markdown("Analiza performantei vanzarilor din intreaga organizatie")
    st.markdown("---")


    df=vg.load_dashboard_data()


    with st.sidebar:
        st.header("Filtre")
        lista_regiuni=sorted(df["region"].unique().tolist())
        lista_ani=sorted(df["year"].unique().tolist(), reverse=True)
        lista_categorii=sorted(df["category"].unique().tolist())


        regiuni_selectate=st.multiselect(
            "Selecteaza Regiuni:",
            options=lista_regiuni,
            default=lista_regiuni,
            key="regions"
        )
        ani_selectati= st.multiselect(
            "Selecteaza Ani:",
            options=lista_ani,
            default=[lista_ani[0]] if lista_ani else [],
            key="years"
        )
        categorii_selectate =st.multiselect(
            "Selecteaza Categorii:",
            options=lista_categorii,
            default=lista_categorii,
            key="categories"
        )







    df_filtered=df[
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
    kpis = vg.calculate_kpis(df_filtered)
    

    
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



    df_trend=vg.get_trend_data(df_filtered)
    fig_trend=vg.plot_trend_chart(df_trend)
    st.plotly_chart(fig_trend)


    st.markdown("---")




    col1,col2 =st.columns(2)
    with col1:
        regional_data=vg.get_regional_performance(df_filtered)
        fig_regional=vg.plot_regional_performance(regional_data)
        st.plotly_chart(fig_regional)
    with col2:
        category_data=vg.get_category_performance(df_filtered)
        fig_category= vg.plot_category_performance(category_data)
        st.plotly_chart(fig_category)


    st.markdown("---")






    col1,col2=st.columns(2)
    with col1:
        fig_status=vg.plot_profit_status(df_filtered)
        st.plotly_chart(fig_status)
    with col2:
        st.subheader("Rezumat Regional")
        regional_data_display=regional_data.copy()
        regional_data_display.columns= ["Regiune", "Venit $", "Profit $" ,"Comenzi"]
        st.dataframe(regional_data_display)




if __name__ == "__main__":
    main()