from typing import Optional
from fastapi import Body, FastAPI, Response, status, HTTPException,Depends
from websockets import PayloadTooBig
from pydantic import BaseModel 
from random import randrange
import psycopg2
from psycopg2.extras import RealDictCursor
import time
from . import models
from .database import engine, get_db
from sqlalchemy.orm import Session

models.Base.metadata.create_all(bind=engine)
app = FastAPI() #object of FastAPI class


class Post(BaseModel):
    title: str # check in pydantic
    content: str
    published: bool = True #default true if user doesnt provide 
   # rating: Optional[int] = None
while True:

    try: 
        #Connect to an existing database
        conn = psycopg2.connect(host='localhost', database='postgres', 
                                user='postgres', password='Masha2938481998',cursor_factory=RealDictCursor)
        #Open a cursor to perform database operations
        cursor = conn.cursor()
        print('Data base contection was sucsessful')
        break
    except Exception as error:
        print('Connected to DB failed')
        print('Error:',error)
        time.sleep(2)# 2 seconds 

  
my_posts = [{"title":"title of post 1","content":"contentof post 1","id":1},
            {"title":"title of post 2","content":"contentof post 2","id":2}]

def find_post(id):
    for p in my_posts:
        if p['id'] == id:
            return p
        
def find_index_post(id:int):
    for i, p in enumerate(my_posts):
        if p['id'] == id:
           return i


#request Get method url :'/'-order matter
#path operation decorator: get, post, put, delete, options, head
@app.get("/") # get is HTTP method, ("/lol")-root path ->http://127.0.0.1:8000/lol
async def hello_user():
    return {"message": "Hello Mariichka"} #json convert

####SQL get_post
#@app.get("/posts") # get use for retrived operation
#def get_posts():
   # cursor.execute("""SELECT * FROM posts """)
   # posts = cursor.fetchall()
   # print(posts)
   #return {"data":posts}
####
@app.get("/posts") # get use for retrived operation using ORM SQLAlchamy
def get_posts(db: Session = Depends(get_db)):
    posts = db.query(models.Post).all()
    print(posts)
    return {"data":posts}
"""
@app.post("/createposts")
def create_posts(payload: dict=Body(...)):
    print(payload)
    return {"new_post":f"title {payload['title']} content: {payload['content']}"}
"""
"""ORM example
@app.get("/sqlachemy")
def test_posts(db: Session = Depends(get_db)):
    posts = db.query(models.Post).all()
    return {"data":posts}
"""

@app.post("/posts",status_code=status.HTTP_201_CREATED)
def create_posts(post: Post):
    """
    post_dict = post.dict()
    post_dict['id'] = randrange(0,1000000)
    print(post.dict())#convert to dict
    my_posts.append(post_dict)
    """
    cursor.execute("""INSERT INTO posts (title,content,published) VALUES (%s,%s,%s) RETURNING *""",
                   (post.title,post.content,post.published))
    new_post =cursor.fetchone()
    conn.commit() # save in data base
    return {"data":new_post}

@app.get("/posts/latest") #order matter > latest can be {id}
def get_latestpost():
    post = my_posts[-1]
    return {"deteil":post}

#title str, content str
@app.get("/posts/{id}") #id is path parameter- alwasy parameters are str
#def get_post_one(id: int,response: Response):#validation -auto switch to int(id)
def get_post_one(id: int):
    #[p for p in my_posts if p['id'] == id]
    cursor.execute("""SELECT * FROM posts WHERE id = %s""", (str(id)))
    post = cursor.fetchone()

   # post = find_post(id)
    if not post:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND,detail=f"post with id {id} was not found")
        #response.status_code = status.HTTP_404_NOT_FOUND
        #return {"mesaage":f"post with id {id} was not found"}
    return {"Your id post is": post}
    """
    if post:
        # The post with the specified id exists
        # You can do something with the filtered_posts here
        return post
    else:
        # The post with the specified id doesn't exist
        return f"The id {id} doesn't exist."
    #return {"post_deatil": [p for p in my_posts if p['id'] == int(id)]}
    #return {"post_deatil": post}
    """

@app.delete('/posts/{id}',status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int):
    # delete post
   """
   post = find_post(id)
   new_posts = [p for p in my_posts if p['id'] != id]
   if post:
       return {"detail":f"all postes before {my_posts},post with {id} {post}was deleted, now is {new_posts}"}
   if not post:
       raise HTTPException(status_code = status.HTTP_404_NOT_FOUND,detail=f"post with id {id} was not found")
   """
   cursor.execute("""DELETE FROM posts WHERE id = %s RETURNING *""",(str(id)))
   delete_post = cursor.fetchone()
   conn.commit()
   #index = find_index_post(id)
   if delete_post==None:
       raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail =f"post with {id} doesnt exist")
   else:
      #my_posts.pop(index)
      return Response(status_code=status.HTTP_204_NO_CONTENT)

@app.put("/posts/{id}")
def update_post(id:int,post:Post):#right schemo Post
    #index = find_index_post(id)
    cursor.execute("""UPDATE posts SET title = %s,content = %s,published= %s  WHERE id = %s RETURNING *""",
                   (post.title,post.content,post.published,str(id)))
    updated_post = cursor.fetchone()
    conn.commit()
    if updated_post==None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail =f"post with {id} doesnt exist")

    #post_dict = post.dict()
    #post_dict['id'] = id
    #my_posts[index] = post_dict
    return {"updated_post":updated_post}

