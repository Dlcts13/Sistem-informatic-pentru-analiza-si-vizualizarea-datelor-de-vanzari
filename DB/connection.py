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


from sqlalchemy import create_engine
import streamlit as st
import os
from dotenv import load_dotenv

load_dotenv()

def get_engine():
    def get_db_cred(key):
        if key in st.secrets:
            return st.secrets[key]
        return os.getenv(key)

    db_host = get_db_cred('DB_HOST')
    
    url = (
        f"postgresql+psycopg2://"
        f"{get_db_cred('DB_USER')}:{get_db_cred('DB_PASSWORD')}"
        f"@{db_host}:{get_db_cred('DB_PORT')}"
        f"/{get_db_cred('DB_NAME')}"
    )

    connect_args = {}
    if db_host and "neon.tech" in db_host:
        connect_args = {"sslmode": "require"}

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
        print("Conectat in mod reusit")