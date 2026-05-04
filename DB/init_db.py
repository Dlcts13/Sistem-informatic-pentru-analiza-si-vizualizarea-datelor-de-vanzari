from DB.connection import get_engine
from DB.models import Base

def init_database():
    engine=get_engine()
    Base.metadata.create_all(engine)
    print("Tabelele au fost create")

if __name__=="__main__":
    init_database()