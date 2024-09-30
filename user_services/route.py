from fastapi import FastAPI, HTTPException, Depends, status, Request
from sqlalchemy.orm import Session
from user_services.models import User, get_db
from user_services.schemas import UserRegistration, UserLogin
from user_services.utils import get_hash_password, verify_password, create_token, create_tokens
from datetime import timedelta
from jose import jwt, JWTError
from settings import settings
from user_services.email import *


app = FastAPI()

@app.get('/')
def fundoo_notes():
    return {"message" : "Fundoo Notes Tasks"}

@app.post("/register", response_model=UserRegistration)
async def register_user(request: Request, user: UserRegistration, db: Session = Depends(get_db)):
    new_user = db.query(User).filter(User.email == user.email).first()
    if new_user:
        raise HTTPException(status_code=400, detail="User already registered")
    
    hashed_password = get_hash_password(user.password)
    new_user = User(email=user.email, 
                    password=hashed_password, 
                    first_name=user.first_name, 
                    last_name=user.last_name)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    token = create_token({"sub": new_user.email}, "access")
    verification_url = request.url_for("verify_registered_user", **{"token":token})
    await send_verification_email(new_user.email, token, verification_url)
    
    return {
        "message" : "New user registered successfully.",
        "status" : "Success",
        "data" : new_user.to_dict
    }

@app.post('/login')
def user_login(user:UserLogin, db:Session = Depends(get_db)):
    log_user = db.query(User).filter(User.email == user.email).first()
    if not log_user or not verify_password(user.password, log_user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credential not matched")
    
    access_token = create_token({"sub" : log_user.email}, "access")
    refresh_token = create_token({"sub" : log_user.email}, "refresh")

    return {
        "message" : "Login Successfully",
        "status" : "Success",
        "access token" : access_token,
        "refesh token" : refresh_token,
        "data" : log_user.to_dict
    }

@app.get("/verify/{token}")
async def verify_registered_user(token: str, db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=400, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=400, detail="Invalid token")
    
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.is_verified = True
    db.commit()
    return {"message": "User verified successfully"}


