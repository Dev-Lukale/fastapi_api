from fastapi import FastAPI,Request,HTTPException,status
from tortoise.contrib.fastapi import register_tortoise
from tortoise import models
from models import (User, Business, Product, user_pydantic, user_pydanticIn, 
                    product_pydantic,product_pydanticIn, business_pydantic, 
                    business_pydanticIn, user_pydanticOut)
from authUtil import *
from mail import *

#signals
from tortoise.signals import post_save
from typing import List,Optional,Type
from tortoise import BaseDBAsyncClient

from fastapi.responses import HTMLResponse

from fastapi.templating import Jinja2Templates

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
        await send_email([instance.email],instance)
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


templates=Jinja2Templates(directory="templates")
@app.get("/verification",response_class=HTMLResponse)
async def verify_email(request: Request,token:str):
    user=await verify_token(token)
    if user and not user.is_verified:
        user.is_verified=True
        await user.save()
        return templates.TemplateResponse("Verification.html",{"request": request,"username":user.username})
    raise HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Invalid token",
    headers={"WWW.Authenticate":"Bearer"}
    )

register_tortoise(
    app,
    db_url="sqlite://database.sqlite3",
    modules={"models":["models"]},
    generate_schemas=True,
    add_exception_handlers=True
)