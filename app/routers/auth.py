from fastapi import Body, FastAPI, Response, status, HTTPException,Depends, APIRouter
from sqlalchemy.orm import Session
from .. import database, schema, models, utils, oauth2
from fastapi.security.oauth2 import OAuth2PasswordRequestForm

router = APIRouter(tags=['Authentication'])
@router.post('/login',response_model=schema.Token)
#def login(user_credentials:schema.UserLogin,db: Session = Depends(database.get_db)):
def login(user_credentials:OAuth2PasswordRequestForm = Depends(),db: Session = Depends(database.get_db)):
    #retun : {'username' ='bala','password' = 'bla'}
    user = db.query(models.User).filter(
        models.User.email == user_credentials.username).first()
    if not user:
        raise HTTPException(status_code = status.HTTP_403_FORBIDDEN,detail=f"Invalid credetials")
    if not utils.verify(user_credentials.password, user.password):
        raise HTTPException(status_code = status.HTTP_403_FORBIDDEN,detail=f"Invalid credetials")
    # create token
    # #return token   
    #return {'token':"excmaple"}      
          
    access_token = oauth2.create_access_token(data = {'user_id':user.id})#its  pillow

    return {"access_token" : access_token, "token_type":"bearer"}
