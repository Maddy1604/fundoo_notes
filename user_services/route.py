from fastapi import FastAPI, HTTPException, Depends, status, Request
from sqlalchemy.orm import Session
from user_services.models import User, get_db
from user_services.schemas import UserRegistration, UserLogin, EmailModel
from passlib.context import CryptContext
from user_services.utils import get_hash_password, verify_password, create_access_token, decode_token
from datetime import timedelta
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from user_services.email import mail, create_message
    
REFRESH_TOKEN_EXPIRY = 2

bcrypt_contest = CryptContext(schemes=["bcrypt"], deprecated="auto")


app = FastAPI()


@app.get('/')
def fundoo_notes():
    return {"message" : "Fundoo Notes Tasks"}

@app.post('/register')
def user_register(user:UserRegistration, db:Session = Depends(get_db)):

    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="User email already registered.")
    
    hashed_password = get_hash_password(user.password)

    new_user= User(
        email = user.email,
        password = hashed_password,
        first_name = user.first_name,
        last_name = user.last_name

    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message" : "User registered successfully.",
            "status" : "Success",
            "data" : new_user.to_dict}


@app.post('/login')
def user_login(user:UserLogin, db:Session = Depends(get_db)):
    log_user = db.query(User).filter(User.email == user.email).first()
    if not log_user or not verify_password(user.password, log_user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credential not matched")
    if log_user:
        access_token = create_access_token(
            user_data={
                'email' : user.email

            }
        )

        refresh_token = create_access_token(
            user_data={
                'email' : user.email
            },
            refresh=True, 
            expiry=timedelta(days=REFRESH_TOKEN_EXPIRY)
        )
    
    return {
        "message" : "Login Successfully",
        "status" : "Success",
        "access token" : access_token,
        "refresh token" : refresh_token,
        "data" : log_user.to_dict
    }

@app.post('/verify_registerd_email')
async def send_mail(email: EmailModel):
    email= email.address

    html = "<h1> Welcome to FundooNotes </h1>"

    message = create_message(
        recipients=email,
        subject="Welcome",
        body=html
    )

    await mail.send_message(message)

    return {"message" : "Email sent successfully"}
 

# templates = Jinja2Templates(directory ="templates")

# @app.get('/verification', response_class=HTMLResponse)
# async def email_verification(request: Request, token:str):
#     user = await verify_token(token)

#     if user and not User.is_verified:
#         User.is_verified = True
#         await user.save()
#         return templates.TemplateResponse("verification.heml",
#                                           {"request":request, "username": User.first_name})
    
#     raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token", 
#                             headers={"WWW-Authenticate": "Bearerj"})
