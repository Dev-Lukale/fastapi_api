from fastapi import (BackgroundTasks,UploadFile,File,Form,Depends,HTTPException,status)
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from dotenv import dotenv_values
from pydantic import BaseModel,EmailStr
from typing import List
from models import (User)
import jwt


config_credentials=dotenv_values(".env")

conf = ConnectionConfig(
    MAIL_USERNAME =config_credentials["EMAIL"],
    MAIL_PASSWORD = config_credentials["PASSWORD"],
    MAIL_FROM =config_credentials["EMAIL"],
    MAIL_PORT = 465,
    MAIL_SERVER = "smtp.gmail.com",
    MAIL_STARTTLS = False,
    MAIL_SSL_TLS = True,
    USE_CREDENTIALS = True,
    VALIDATE_CERTS = True
)
# class EmailSchema(BaseModel):
#     email:List[EmailStr]
async def send_email(email:List,instance:User):
    token_data={
        "id":instance.id,
        "username":instance.email
    }
    token=jwt.encode(token_data,config_credentials["SECRET"],algorithm='HS256')

    template=f"""
        <!DOCTYPE html>
        <html>
            <head></head>
            <body>
                <div style="display:flex;align-items:center;justify-content:center;flex-direction:column">
                    <h3>Account Verification</h3><br>
                    <p>
                        Thanks for choosing EasyShoppa,please click on the button
                        below to verify your account
                    </p>
                    <a style="margin-top:1rem;padding:1rem;border-radius:0.5rem;
                    font-size:1rem;text-decoration:none;background:blue;color:white"
                    href="http://localhost:8000/verification/?token={token}"
                    >
                    Verify Email
                    </a>
                    <p>Kindly ignore this email if you did not register with EasyShoppa</p>
                </div>
            </body>
        </html>
    """
    message=MessageSchema(
        subject="EasyShoppa Account Verification Email",
        recipients=email,#list of recipients
        body=template,
        subtype="html"
    )
    fm=FastMail(conf)
    await fm.send_message(message=message)
