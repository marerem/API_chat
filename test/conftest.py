from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base
from app.main import app
import pytest
from app import models
from app.oauth2 import create_access_token
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

@pytest.fixture()
def test_user(client):
    user_data = {"email":"masha@gmail.com","password":"123"}    
    res = client.post("/users/",json=user_data)
    new_user = res.json()
    new_user['password'] = user_data['password']
    #assert new_user.email == "masha@gmail.com"
    return new_user

@pytest.fixture
def test_user2(client):
    user_data = {"email": "masha123@gmail.com",
                 "password": "password123"}
    res = client.post("/users/", json=user_data)

    assert res.status_code == 201

    new_user = res.json()
    new_user['password'] = user_data['password']
    return new_user

@pytest.fixture
def token(test_user):
    return create_access_token({"user_id": test_user['id']})

@pytest.fixture
def authorized_client(client, token):
    client.headers = {
        **client.headers,
        "Authorization": f"Bearer {token}"
    }

    return client

@pytest.fixture
def test_posts(test_user, session,test_user2):
    posts_data = [{
        "title": "first title",
        "content": "first content",
        "owner_id": test_user['id']
    }, {
        "title": "2nd title",
        "content": "2nd content",
        "owner_id": test_user['id']
    },
        {
        "title": "3rd title",
        "content": "3rd content",
        "owner_id": test_user2['id']
    }]

    def create_post_model(post):
        return models.Post(**post)

    post_map = map(create_post_model,posts_data)
    posts = list(post_map)
    session.add_all(posts)
    """
    session.add_all([models.User(title="first title",content="first content",owner_id=test_user['id'])
                        ])
    """
    session.commit()
    posts = session.query(models.Post).all
    return posts