from pydantic import BaseModel, EmailStr

class UserRegistration(BaseModel):
    email : EmailStr
    password : str
    first_name : str
    last_name : str

class UserLogin(BaseModel):
    email : EmailStr
    password : str

    