from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from . config import setting
SQLALCHEMY_DATABASE_URL = f"postgresql://{setting.database_username}:{setting.database_password}@{setting.database_hostname}/{setting.database_name}"
#SQLALCHEMY_DATABASE_URL = "postgresql://postgres:Masha2938481998@localhost/postgres"
# SQLALCHEMY_DATABASE_URL = "postgresql://<username>:<password>@<ip-adress/hostname>/<database_name>"

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()