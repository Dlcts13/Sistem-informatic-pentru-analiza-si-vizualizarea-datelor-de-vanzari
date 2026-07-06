import streamlit as st
import sys
import os
from sqlalchemy import text
from streamlit_autorefresh import st_autorefresh
from google import genai

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, parent_dir)

st.set_page_config(page_title="Raport AI", layout="wide")

from DB.connection import get_engine
from ANALYTICS import vanzari_generale as vg 

if not st.session_state.get("authentication_status"):
    st.error("Acces refuzat!")
    st.stop()

if st.session_state.get("role") != "manager":
    st.error("Acces neautorizat!")
    st.stop()

st_autorefresh(interval=300000, limit=None, key="smart_refresh_raport_ai")

def get_data_version():
    engine = get_engine()
    query = "SELECT COUNT(*), MAX(created_at) FROM fact_sales;"
    with engine.connect() as conn:
        result = conn.execute(text(query)).fetchone()
    return f"{result[0]}_{result[1]}"

current_version = get_data_version()

if "last_data_version_raport_ai" not in st.session_state:
    st.session_state["last_data_version_raport_ai"] = current_version

if current_version != st.session_state["last_data_version_raport_ai"]:
    st.toast("Date noi primite in platforma! Se actualizeaza ...")
    st.session_state["last_data_version_raport_ai"] = current_version

def main():
    st.title("Raport Managerial AI")
    st.markdown("Genereaza o sinteza si recomandari bazate pe cele mai recente date financiare.")
    st.markdown("---")
    
    df = vg.load_dashboard_data(version_hash=current_version)

    if st.button("Genereaza Raport AI", use_container_width=True):
        
        with st.spinner("AI-ul analizeaza performanta financiara..."):
            try:
                api_key = st.secrets.get("GEMINI_API_KEY") if "GEMINI_API_KEY" in st.secrets else os.environ.get("GEMINI_API_KEY")
                client = genai.Client(api_key=api_key)
                
                venit_total = df['revenue'].sum() if 'revenue' in df.columns else 0
                profit_total = df['profit'].sum() if 'profit' in df.columns else 0
                
                prompt = f"""
                Ești un analist financiar senior la o companie de retail.
                Datele financiare actualizate sunt:
                - Venit Total: ${venit_total:,.2f}
                - Profit Total: ${profit_total:,.2f}
                
                Scrie un raport executiv scurt de 2 paragrafe pentru CEO-ul companiei. 
                Sintetizează aceste rezultate și oferă 3 recomandări strategice de business (bullet points) pentru a crește profitabilitatea în luna următoare.
                Folosește un ton profesional, optimist și formatare Markdown (bold pentru idei principale).
                """
                
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=prompt
                )
                
                st.success("Raport generat cu succes!")
                st.markdown(response.text)
                
            except Exception as e:
                st.error(f"Eroare la conectarea cu AI: {str(e)}")

if __name__ == "__main__":
    main()