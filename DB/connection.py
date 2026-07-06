# from sqlalchemy import create_engine
# from dotenv import load_dotenv
# import os

# load_dotenv()

# def get_engine():
#     url = (
#         f"postgresql+psycopg2://"
#         f"{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
#         f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}"
#         f"/{os.getenv('DB_NAME')}"
#     )

#     return create_engine(url)

# if __name__=="__main__":
#     engine=get_engine()
#     with engine.connect() as conn:
#         print("Conectat in mod reusit")


# from sqlalchemy import create_engine
# from sqlalchemy.engine import make_url
# import streamlit as st
# import os
# from dotenv import load_dotenv

# load_dotenv()


# def _clean_value(value):
#     if isinstance(value, str):
#         return value.strip()
#     return value

# def get_engine():
#     def get_db_cred(key):
#         try:
#             if key in st.secrets:
#                 return _clean_value(st.secrets[key])
#         except Exception:
#             pass

#         return _clean_value(os.getenv(key))

#     database_url = get_db_cred('DATABASE_URL')
#     if database_url:
#         url = database_url.replace('postgres://', 'postgresql+psycopg2://', 1)
#         parsed_url = make_url(url)

#         connect_args = {}
#         if parsed_url.host and 'neon.tech' in parsed_url.host:
#             connect_args = {'sslmode': 'require'}

#         return create_engine(
#             url,
#             connect_args=connect_args,
#             pool_pre_ping=True,
#             pool_size=5,
#             max_overflow=10,
#         )

#     db_host = get_db_cred('DB_HOST')
#     db_user = get_db_cred('DB_USER')
#     db_password = get_db_cred('DB_PASSWORD')
#     db_port = get_db_cred('DB_PORT')
#     db_name = get_db_cred('DB_NAME')

#     if not all([db_host, db_user, db_password, db_port, db_name]):
#         raise RuntimeError(
#             'Database credentials are missing. Configure DATABASE_URL or DB_USER/DB_PASSWORD/DB_HOST/DB_PORT/DB_NAME in Streamlit secrets.'
#         )
    
#     url = (
#         f"postgresql+psycopg2://"
#         f"{db_user}:{db_password}"
#         f"@{db_host}:{db_port}"
#         f"/{db_name}"
#     )

#     connect_args = {}
#     if db_host and "neon.tech" in db_host:
#         connect_args = {"sslmode": "require"}

#     return create_engine(
#         url, 
#         connect_args=connect_args,
#         pool_pre_ping=True,
#         pool_size=5,
#         max_overflow=10
#     )

# if __name__=="__main__":
#     engine = get_engine()
#     with engine.connect() as conn:
#         print("Conectat in mod reusit")

import os
import streamlit as st
from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from dotenv import load_dotenv

load_dotenv()

def _clean_value(value):
    if isinstance(value, str):
        return value.strip()
    return value

def get_engine():
    try:
        if "DATABASE_URL" in st.secrets:
            db_url = _clean_value(st.secrets["DATABASE_URL"])
            
            if db_url.startswith("postgres://"):
                db_url = db_url.replace("postgres://", "postgresql+psycopg2://", 1)
            elif db_url.startswith("postgresql://") and "psycopg2" not in db_url:
                db_url = db_url.replace("postgresql://", "postgresql+psycopg2://", 1)
                
            parsed_url = make_url(db_url)
            connect_args = {"sslmode": "require"} if parsed_url.host and "neon.tech" in parsed_url.host else {}
            
            return create_engine(
                db_url,
                connect_args=connect_args,
                pool_pre_ping=True,
                pool_size=5,
                max_overflow=10,
            )
            
        elif "DB_HOST" in st.secrets:
            db_host = _clean_value(st.secrets["DB_HOST"])
            db_user = _clean_value(st.secrets["DB_USER"])
            db_password = _clean_value(st.secrets["DB_PASSWORD"])
            db_port = _clean_value(st.secrets["DB_PORT"])
            db_name = _clean_value(st.secrets["DB_NAME"])
            
            db_url = f"postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
            connect_args = {"sslmode": "require"} if "neon.tech" in db_host else {}
            
            return create_engine(
                db_url,
                connect_args=connect_args,
                pool_pre_ping=True,
                pool_size=5,
                max_overflow=10,
            )
    except Exception:
        pass

    db_host = _clean_value(os.getenv('DB_HOST'))
    db_user = _clean_value(os.getenv('DB_USER'))
    db_password = _clean_value(os.getenv('DB_PASSWORD'))
    db_port = _clean_value(os.getenv('DB_PORT'))
    db_name = _clean_value(os.getenv('DB_NAME'))

    if not all([db_host, db_user, db_password, db_port, db_name]):
        raise RuntimeError("Database credentials are missing. Verifică .env sau Secrets!")

    if db_host == "localhost":
        try:
            st.error("ATENȚIE: Aplicația încearcă să se conecteze la localhost pe Cloud! Verifică dacă ai un fișier .env urcat din greșeală pe GitHub.")
        except Exception:
            pass

    url = f"postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    connect_args = {"sslmode": "require"} if "neon.tech" in db_host else {}

    return create_engine(
        url, 
        connect_args=connect_args,
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=10
    )

if __name__=="__main__":
    engine = get_engine()
    with engine.connect() as conn:
        print(f"Conectat in mod reusit la: {engine.url.host}")