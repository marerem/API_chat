from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base
from app.main import app
import pytest
from app.config import setting
from app.database import get_db,Base
#u can use alambic istead of sqlachamy
from alembic import command 
#You can hard code or just
#SQLALCHEMY_DATABASE_URL = "postgresql://postgres:Masha2938481998@localhost:5432/postgres_test"
SQLALCHEMY_DATABASE_URL = f"postgresql://{setting.database_username}:{setting.database_password}@{setting.database_hostname}/{setting.database_name}_test"

engine = create_engine(SQLALCHEMY_DATABASE_URL)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

#Base.metadata.create_all(bind=engine)

# Dependency
"""
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
"""
#app.dependency_overrides[get_db] = override_get_db

#client = TestClient(app)

@pytest.fixture()
def session():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture()
def client(session):
    #Base.metadata.drop_all(bind=engine)
    #Base.metadata.create_all(bind=engine)
    #command.upgrade("head")#create all tables
    #run our code before we return our test 
    def override_get_db():
   
        try:
            yield session
        finally:
            session.close()
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    
    # run our code after our test finishes 
    #command.downgrade("base")