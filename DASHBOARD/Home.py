import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
import subprocess
import os
import sys

st.set_page_config(page_title="Platforma Analiza", layout="wide")

if "credentials" in st.secrets:
    credentials = dict(st.secrets["credentials"])
    credentials["usernames"] = dict(credentials["usernames"])
    for user in credentials["usernames"]:
        credentials["usernames"][user] = dict(credentials["usernames"][user])
        
    cookie = dict(st.secrets["cookie"])
else:
    with open('config.yaml') as file:
        config = yaml.load(file, Loader=SafeLoader)
    credentials = config['credentials']
    cookie = config['cookie']

authenticator = stauth.Authenticate(
    credentials,
    cookie['name'],
    cookie['key'],
    cookie['expiry_days']
)

USER_ROLES = {
    "darius_manager": "manager",
    "agent_unu": "agent",
    "agent_doi": "agent"
}

authenticator.login()

if st.session_state["authentication_status"]:
    current_user = st.session_state["username"]
    st.session_state["role"] = USER_ROLES.get(current_user, "agent")

    with st.sidebar:
        st.write(f"👤 Utilizator: **{current_user}**")
        st.write(f"🔑 Rol: **{st.session_state['role'].upper()}**")
        authenticator.logout('Deconectare', 'main')
        
    st.title("Sistem informatic pentru analiza si vizualizarea datelor")
    st.markdown("---")

    st.subheader("Bun venit!")
    st.write("Sistemul se bazeaza pe un ETL pipeline extins, capabil sa suporte diferite surse de date, rezultand in informatii utile despre business.")
    st.markdown("---")

    DASHBOARD_DIR=os.path.dirname(os.path.abspath(__file__))
    PROJECT_ROOT=os.path.abspath(os.path.join(DASHBOARD_DIR, ".."))
    ETL_DIR=os.path.join(PROJECT_ROOT,"ETL")

    def run_etl_script(script_name, args=None):
        script_path=os.path.join(ETL_DIR, script_name)

        if not os.path.exists(script_path):
            st.error(f"Fisierul `{script_name}` nu a fost gasit in folderul ETL")
            return

        env_vars=os.environ.copy()
        env_vars["PYTHONIOENCODING"]="utf-8"
        env_vars["PYTHONUTF8"]="1"

        cmd=[sys.executable,script_path]
        if args:
            cmd.extend(args)
        with st.spinner(f"Se ruleaza `{script_name}`..."):
            try:
                result=subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    env=env_vars,
                    check=True
                )
                st.success(f"`{script_name}` a rulat cu succes")

                with st.expander("Vezi detaliile executiei"):
                    st.code(result.stdout,language="text")

            except subprocess.CalledProcessError as e:
                st.error(f"Eroare la rularea `{script_name}`")
                with st.expander("Vezi eroarea completa"):
                    st.code(e.stderr or e.stdout,language="text")
            except Exception as e:
                st.error(f"Eroare neasteptata: {e}")

    st.subheader("Panou de Control ETL")
    st.write("Configureaza extragerea datelor din diverse surse")
    st.markdown("---")

    with st.expander("Incarca date din fisier CSV", expanded=False):
        st.write("Selecteaza un fisier CSV pentru a-l incarca in baza de date")
        
        col1,col2= st.columns([3, 1])
        
        with col1:
            csv_path = st.text_input(
                "Calea fisierului CSV",
                value="RES/Sample - Superstore.csv",
                placeholder="Ex: RES/data.csv sau C:/Users/data.csv",
                key="csv_path"
            )
        with col2:
            st.write("")
            if st.button("Executa",key="run_csv",use_container_width=True):
                if csv_path.strip():
                    run_etl_script("load_csv_to_db.py", ["--path", csv_path])
                else:
                    st.error("Introduce o cale valida")

    st.write("")

    with st.expander("Incarca date din AWS S3",expanded=False):
        st.write("Configureaza parametrii de conexiune la AWS S3")
        col1,col2,col3=st.columns(3)
        
        with col1:
            s3_bucket=st.text_input(
                "Bucket name",
                value="licenta-sales-data",
                key="s3_bucket"
            )
        with col2:
            s3_key=st.text_input(
                "File key",
                value="data_aws_s3.csv",
                key="s3_key"
            )
        with col3:
            s3_region=st.text_input(
                "Regiunea AWS",
                value="eu-north-1",
                key="s3_region"
            )
        
        col_btn1,col_btn2=st.columns([3, 1])
        
        with col_btn2:
            if st.button("Executa",key="run_s3", use_container_width=True):
                if s3_bucket.strip() and s3_key.strip():
                    args=[
                        "--bucket",s3_bucket,
                        "--key",s3_key,
                        "--region", s3_region
                    ]
                    run_etl_script("load_aws_s3.py", args)
                else:
                    st.error("Completeaza bucket name si file key")

    st.write("")

    with st.expander("Incarca date din Google Sheets",expanded=False):
        st.write("Configureaza parametrii pentru Google Sheets")
        col1,col2=st.columns(2)

        with col1:
            gs_id=st.text_input(
                "Spreadsheet ID",
                value="164Mj4CzG7ES5uMhdrukEEDD_vnHW_aETSCzB1bVySm8",
                placeholder="Ex: ABC123XYZ",
                key="gs_id"
            )
        with col2:
            gs_sheet=st.text_input(
                "Sheet name",
                value="data_google_sheets",
                placeholder="Ex: Sheet1",
                key="gs_sheet"
            )
        gs_creds=st.text_input(
            "Calea credentiale Google",
            value="credentials_google.json",
            placeholder="Empty pentru cautare automata",
            key="gs_creds"
        )
        
        col_btn1,col_btn2=st.columns([3, 1])

        with col_btn2:
            if st.button("Executa",key="run_gs",use_container_width=True):
                if gs_id.strip() and gs_sheet.strip():
                    args=[
                        "--id",gs_id,
                        "--sheet",gs_sheet
                    ]
                    if gs_creds.strip():
                        args.extend(["--creds", gs_creds])
                    run_etl_script("load_google_sheets.py",args)
                else:
                    st.error("Completeaza Spreadsheet ID si Sheet name")

    st.markdown("---")

elif st.session_state["authentication_status"] is False:
    st.error('Username sau parolă incorecte!')
elif st.session_state["authentication_status"] is None:
    st.warning('Te rugăm să introduci datele de logare pentru a accesa platforma.')