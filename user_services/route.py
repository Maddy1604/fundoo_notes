from fastapi import FastAPI, HTTPException, Depends, status
from sqlalchemy.orm import Session
from user_services.models import User, get_db
from user_services.schemas import UserRegistration, UserLogin
from passlib.context import CryptContext
from user_services.utils import get_hash_password, verify_password

bcrypt_contest = CryptContext(schemes=["bcrypt"], deprecated="auto")


app = FastAPI()
# def get_password_hash(password):
#     return bcrypt_contest.hash(password)

@app.get('/')
def fundoo_notes():
    return {"message" : "Fundoo Notes Tasks"}

@app.post('/register')
def user_register(user:UserRegistration, db:Session = Depends(get_db)):

    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="User email already registered.")
    
    hashed_password = get_hash_password(user.password)

    newUser= User(
        email = user.email,
        password = hashed_password,
        first_name = user.first_name,
        last_name = user.last_name

    )

    db.add(newUser)
    db.commit()
    db.refresh(newUser)

    return {"message" : "User registered successfully.",
            "status" : "Success",
            "data" : newUser.to_dict}


@app.post('/login')
def user_login(user:UserLogin, db:Session = Depends(get_db)):
    log_user = db.query(User).filter(User.email == user.email, User.password == user.password).first()
    if not log_user or not verify_password(user.password, log_user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credential not matched")
    
    return {
        "message" : "Login Successfully",
        "status" : "Success",
        "data" : log_user.to_dict
    }

    
    
