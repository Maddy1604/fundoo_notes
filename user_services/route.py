from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks, Request
from sqlalchemy.orm import Session
from .models import User, get_db
from .schemas import UserRegistration, UserLogin 
from .utils import hash_password, verify_password, create_token, create_tokens
from .email import send_verification_email
from settings import settings
import jwt


# Initialize FastAPI app
app = FastAPI()

@app.get("/")
def read_root():
    '''
    Discription: This is the handler function that gets called when a request is made to the root endpoint
    Parameters: None
    Return: A dictionary with a welcome message.
    '''
    return {"message": "Welcome to the Fundoo Notes API!"}

# Register a new user
@app.post("/register")
def register_user(request: Request, user: UserRegistration, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    '''
    Discription: Registers a new user after validating the input, checking if the user exists, 
    hashing the password, and storing the user in the database.
    Parameters: 
    request: Request: Provides information about the HTTP request, which is used to generate the email verification link.
    user: UserRegistration: The request body is validated using the UserRegistration, 
    which ensures that all required fields are correctly formatted.
    db: Session = Depends(get_db): Uses dependency injection to pass the current database session to the function.
    Return: Returns a JSON response with a success message and the registered user's data 
    (using the to_dict() method of the User model).
    '''
    # Check if the user already exists by email
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Hash the user's password
    hashed_password = hash_password(user.password)

    # Create a new User object
    db_user = User(
        email=user.email, 
        password=hashed_password,
        first_name=user.first_name,
        last_name=user.last_name
    )

    # Add the user to the database and commit the transaction
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Generate the access token where subject use as key and user entered email as value 
    access_token = create_token({"sub": db_user.email}, "access")

    # Generate verification link using request url_for function taking token as access_token 
    verify_link = request.url_for('verify_registered_user', token= access_token)
        
    # Send verification email using the utility function
    background_tasks.add_task(send_verification_email, db_user.email, verify_link)
    
    return {
        "message": "User registered successfully",
        "status": "success",
        "data": db_user.to_dict,
        "access_token": access_token
    }

# User login
@app.post("/login")
def login_user(user: UserLogin, db: Session = Depends(get_db)):
    '''
    Discription:  Logs in a user by verifying their email and password against the database, 
    returning a success message if they match.
    Parameters: 
    user: UserLogin : The request body is validated using the UserLogin (email and password).
    db: Session = Depends(get_db): Dependency injection is used to get a database session via the get_db function.
    Return: If the email and password match, a success message is returned, along with the logged-in user's data.
    '''
    # Check if the user exists in the database by email
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user or not verify_password(user.password, db_user.password):
        raise HTTPException(status_code=400, detail="Invalid email or password")

    # Generate both JWT tokens
    access_token, refresh_token = create_tokens({"sub": db_user.email, "user_id": db_user.id})

    return {
        "message": "Login successful",
        "status": "success",
        "access_token": access_token,
        "refresh_token": refresh_token,
        "data": db_user.to_dict
    }

@app.get("/verify/{token}")
def verify_registered_user(token: str, db: Session = Depends(get_db)):
    try:
        # Decode the token
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        email = payload.get("sub")

        if email is None:
            raise HTTPException(status_code=400, detail="Invalid token")

        # Fetch the user from the database
        user = db.query(User).filter(User.email == email).first()

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Mark user as verified
        if user.is_verified:
            return {"message": "User is already verified"}
    
        # Verify the user
        user.is_verified = True
        db.commit()

        return {"message": "Email verified successfully!"}

    except Exception:
        raise HTTPException(status_code=400, detail="Token has expired or is invalid")

@app.get("/user/{token}",status_code= 200, include_in_schema= False)
def auth_user(token: str, db: Session = Depends(get_db)):
    try:
        # Decode the JWT token to get payload
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        # print(payload)
        user_id: int = payload.get("user_id")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid User ID")
        
        # Fetch user details from the database based on user_id from token
        db_user = db.query(User).filter(User.id == user_id).first()
        if not db_user:
            raise HTTPException(status_code=404, detail= "User not found")
        
        # Return user details in JSON format
        return {
            "message": "Authorizaton successful",
            "status": "success",
            "data": db_user
        }
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")