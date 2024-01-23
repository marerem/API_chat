from typing import Optional, List
from fastapi import Body, FastAPI, Response, status, HTTPException,Depends, APIRouter
from .. import models, schema, utils,oauth2
from ..database import engine, get_db
from sqlalchemy.orm import Session
from sqlalchemy import func
router = APIRouter(
    prefix = "/posts",
    tags = ['Posts']
)

@router.get("/",response_model=List[schema.PostOut]) # get use for retrived operation using ORM SQLAlchamy
def get_posts(db: Session = Depends(get_db), 
              current_user: int = Depends(oauth2.get_current_user),
              limit:int =10,skip:int = 0,search:Optional[str]=""):#deafult 10 limit of number of posts
    #posts = db.query(models.Post).all()
    #posts = db.query(models.Post).limit(limit).all()# {{URL}}posts?limit=1
    ###posts = db.query(models.Post).filter(models.Post.title.contains(search)).limit(limit).offset(skip).all()#{{URL}}posts?limit=1&skip=1
    #{{URL}}posts?search=3 - title ocncist of 3
    #{{URL}}posts?search=something%20beaches - %20 is space
    #if you want only posts belong to desire user:
    #posts = db.query(models.Post).filter(models.Post.owner_id == current_user.id).all()
    posts = db.query(models.Post,func.count(models.Vote.post_id).label("votes")).join(models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(models.Post.id).filter(models.Post.title.contains(search)).limit(limit).offset(skip).all()

    return posts

@router.post("/",status_code=status.HTTP_201_CREATED,response_model=schema.Post)
def create_posts(post: schema.PostCreate,db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)): #access to db
    #new_post = models.Post(title=post.title,content=post.content,published=post.published)

    new_post = models.Post(owner_id=current_user.id,**post.dict()) # same as above
    db.add(new_post)
    db.commit()
    db.refresh(new_post) # same as RETURNING *

    return new_post

@router.get("/{id}",response_model=schema.PostOut) 
def get_post_one(id: int,db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    #post = db.query(models.Post).filter(models.Post.id == id).first() #only unique id
    post = db.query(models.Post,func.count(models.Vote.post_id).label("votes")).join(models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(models.Post.id).filter(models.Post.id == id).first()
    if not post:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND,detail=f"post with id {id} was not found")
        #response.status_code = status.HTTP_404_NOT_FOUND
        #return {"mesaage":f"post with id {id} was not found"}
    return post

@router.delete('/{id}',status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int,db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
   post = db.query(models.Post).filter(models.Post.id == id).first()

   if post==None:
       raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail =f"post with {id} doesnt exist")

   if post.owner_id != current_user.id:
       raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                           detail= "Not authorized to perform requested action")
   db.delete(post)
   db.commit()
   return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.put("/{id}",response_model=schema.Post)
def update_post(id:int,postm:schema.PostCreate,db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):#right schemo Post
    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()
    if post==None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail =f"post with {id} doesnt exist")
    if post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                        detail= "Not authorized to perform requested action")

    #post_query.update({'title':'heyey','content':"wow"})
    post_query.update(postm.dict())
    db.commit()
    return post_query.first()