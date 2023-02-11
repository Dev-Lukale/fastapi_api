from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise
from tortoise import models
from models import *
from authUtil import *

#signals
from tortoise.signals import post_save
from typing import List,Optional,Type
from tortoise import BaseDBAsyncClient

app = FastAPI()

@post_save(User)
async def create_business(
    sender:"Type[User]",
    instance:User,
    created:bool,
    using_db:"Optional[BaseDBAsyncClient]",
    update_fields:List[str]
)-> None:
    
    if created:
        business_obj= await Business.create(
            businessname=f"{instance.username}'s business",owner=instance
        )
        await business_pydantic.from_tortoise_orm(business_obj)
        #send the email
@app.get("/")
def index():
    return{"Message":"Welcome User"}

@app.post("/register")
async def register(user:user_pydanticIn):
    user_info=user.dict(exclude_unset=True)
    user_info["password"]=hash_password(user_info["password"])
    user_obj=await User.create(**user_info)
    new_user=await user_pydantic.from_tortoise_orm(user_obj)

    return{
        "status":"OK",
        "data":f"Hello {new_user.username},Please check your email inbox to verify your registration"
    }

register_tortoise(
    app,
    db_url="sqlite://database.sqlite3",
    modules={"models":["models"]},
    generate_schemas=True,
    add_exception_handlers=True
)