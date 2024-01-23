from typing import Optional, List
from fastapi import Body, FastAPI, Response, status, HTTPException,Depends, APIRouter
from .. import models, schema, utils,oauth2
from ..database import engine, get_db
from sqlalchemy.orm import Session
router = APIRouter(
    prefix= "/vote",
    tags = ['Vote']
)

@router.post("/",status_code=status.HTTP_201_CREATED)
def vote(vote:schema.Vote,db: Session = Depends(get_db),
        current_user: int = Depends(oauth2.get_current_user)):
    
    post  = db.query(models.Post).filter(models.Post.id == vote.post_id).first()
    if not post:
        raise HTTPException(status.HTTP_404_NOT_FOUND,detail=f'Post with id {vote.post_id} doesnt exist')
    
    vote_query = db.query(models.Vote).filter(models.Vote.post_id == vote.post_id,models.Vote.user_id == current_user.id)#if already exist vote
    found_vot = vote_query.first()

    if (vote.dir==1):
        if found_vot:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail=f'user{current_user.id} has laready voted on post {vote.post_id}')
        new_vote = models.Vote(post_id = vote.post_id, user_id=current_user.id)
        db.add(new_vote)
        db.commit()
        return {'meassage':"you vote succussfully"}
    else:
        if not found_vot:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Vote doesnt exist")
        
        vote_query.delete(synchronize_session=False)
        db.commit()
    return {'message':"succussfully deleted"}
  