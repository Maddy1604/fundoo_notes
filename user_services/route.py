from fastapi import FastAPI, HTTPException
from sqlalchemy.orm import Session
from user_services.models import User, get_db

app = FastAPI()

@app.get('/')
def 

