from app import schema
from jose import jwt
#from .database import client, session # because client depedns on session ->can # becaise use conftest.py
import pytest
from app.config import setting

@pytest.fixture()
def test_user(client):
    user_data = {"email":"masha@gmail.com","password":"123"}    
    res = client.post("/users/",json=user_data)
    new_user = res.json()
    new_user['password'] = user_data['password']
    #assert new_user.email == "masha@gmail.com"
    return new_user



"""
def test_root(client):
    response = client.get("/")
    #print(response.json().get('message'))
    assert response.status_code == 200
    assert response.json().get('message') == "hiii world"
"""

def test_create_user(client):
    res = client.post("/users/",json={"email":"masha@gmail.com","password":"123"})
    #print(res.json())
    new_user = schema.UserOut(**res.json())#use ** to unpack dict
    assert new_user.email == "masha@gmail.com"
    assert res.status_code == 201

def test_login_user(client,test_user):
    res = client.post("/login",data={"username":test_user['email'],"password":test_user['password']})
    #print(res.json())
    login_res = schema.Token(**res.json())
    payload = jwt.decode(login_res.access_token,setting.secret_key,algorithms=setting.algorithm)
    id = payload.get("user_id")
    assert id == test_user["id"]
    assert login_res.token_type == "bearer"
    assert res.status_code == 200
@pytest.mark.parametrize("email, password, status_code",[
    ('wrongemail@gmail.com', '123', 403),
    ('masha@gmail.com', 'wrongpassword', 403),
    ('wrongemail@gmail.com', 'wrongpassword', 403),
    (None, '123', 422),
    ('masha@gmail.com', None, 422)
])
def test_incorrect_login(client,test_user,status_code,password,email):
    res = client.post("/login",data={"username":email,"password":password})
    assert res.status_code == status_code
    #assert res.json().get('detail') == "Invalid credetials"
