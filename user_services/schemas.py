from pydantic import BaseModel, EmailStr, field_validator
import re

# Schema for creating a new user
class UserRegistration(BaseModel):
    '''
    Defines a model for user registration. 
    This model inherits from BaseModel and fields are type-annotated.
    '''
    email: EmailStr
    password: str
    first_name: str
    last_name: str

    @field_validator("first_name", "last_name")
    def validate_name(cls, value):
        '''
        Discription: This method validates both the first_name and last_name fields.
        Parameters: 
        cls: The class the method is attached to.
        value: The value of the field (either first name or last name) that will be validated.
        Return: Returns the validated value if it passes the check.
        '''
        # Validate first and last names
        if len (value) < 3:
            raise ValueError("Name must contain at least 3 characters")
        return value
        
    @field_validator("email")
    def validate_email(cls, value):
        # Validate email
        if not re.match(r"[^@]+@[^@]+\.[^@]+", value):
            raise ValueError("Invalid email format")
        return value
    
    @field_validator("password")
    def validate_password(cls, value):
        # Validate password strength
        if len(value) < 8 or not re.search(r'\W', value):
            raise ValueError("Password must contain at least 8 characters and 1 special character")
        return value


# Schema for user login
class UserLogin(BaseModel):
    '''
    This class is used for validating the login request, 
    ensuring that an email and password are provided and in the given format.
    '''
    email: EmailStr
    password: str

    @field_validator("password")
    def validate_password(cls, value):
        # Check if the password is provided (not empty)
        if len(value) == 0:
            raise ValueError("Password cannot be empty")
        return value

