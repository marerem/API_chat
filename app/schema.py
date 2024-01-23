from pydantic import BaseModel , EmailStr, conint
from datetime import datetime
from typing import Optional
#classes for requests : 

class PostBase(BaseModel):
    title: str # check in pydantic
    content: str
    published: bool = True #default true if user doesnt provide 
    

class PostCreate(PostBase):
    pass
class UserOut(BaseModel):
    id : int
    email : EmailStr
    created_at : datetime
    class Config:
        from_attributes =True
# what we want in response:
class Post(PostBase):
    id : int
    created_at : datetime
    owner_id : int
    owner: UserOut
    class Config:
        from_attributes =True

class PostOut(BaseModel):
    Post:Post
    votes:int
    class Config:
        from_attributes =True
"""             
class CreatePost(BaseModel):
    title: str # check in pydantic
    content: str
    published: bool = True #default true if user doesnt provide 

class UpdatePost(BaseModel):
    title: str # check in pydantic
    content: str
    published: bool = True #default true if user doesnt provide 
"""
class UserCreate(BaseModel):
    email : EmailStr
    password : str
    class Config:
        from_attributes =True

class UserOut(BaseModel):
    id : int
    email : EmailStr
    created_at : datetime
    class Config:
        from_attributes =True

class UserLogin(BaseModel):
    email : EmailStr
    password : str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    id : Optional[str] = None
    
class Vote(BaseModel):
    post_id : int
    dir: conint(le=1)