
from typing import Optional, List
from fastapi import Body, FastAPI, Response, status, HTTPException,Depends, APIRouter
from .. import models, schema, utils
from ..database import engine, get_db
from sqlalchemy.orm import Session

router = APIRouter(
    prefix= "/users",
    tags = ['Users']
)

@router.post("/",status_code=status.HTTP_201_CREATED,response_model=schema.UserOut)
def create_user(user:schema.UserCreate,db: Session = Depends(get_db)):
    #hash the password - user.password
    # Check if the new_user with the given email already exists
    existing_user = db.query(models.User).filter(models.User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    hashed_password = utils.hash(user.password)
    user.password = hashed_password
    new_user = models.User(**user.dict()) # same as above
    db.add(new_user)
    db.commit()
    db.refresh(new_user) # same as RETURNING *
    return new_user

@router.get('/{id}',response_model=schema.UserOut)
def get_user(id:int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id==id).first()
    if not user:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND,detail=f"The user with id {id} was not found")
    return user 


