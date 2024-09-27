from pydantic import BaseModel, EmailStr, field_validator
import re

class UserRegistration(BaseModel):
    email : EmailStr
    password : str
    first_name : str
    last_name : str

    @field_validator("first_name", "last_name")
    def check_names(cls, value):
        if len(value) < 3:
            raise ValueError ("Name atleast contain 3 characters.")
        return value

    @field_validator('email')
    def check_email(cls, value):
        if not re.match(r'[^@]+@[^@]+\.[^@]+', value):
            raise ValueError("Invalid email.")
        return value
    
    @field_validator('password')
    def check_password(cls, value):
        if len(value) < 8 or not re.search(r'\W', value):
            raise ValueError("Invalid password, Password should have minimum 8 characters and 1 special character init.")
        return value


class UserLogin(BaseModel):
    email : EmailStr
    password : str

    @field_validator("password")
    def valid_password(cls, value):
        if len(value) == 0:
            raise ValueError("Password cannot be empty")
        return value 


    