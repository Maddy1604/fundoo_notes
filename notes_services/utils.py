import requests as http
from fastapi import Request, HTTPException


def auth_user(request: Request):
    token = request.headers.get("Authorization")
    response = http.get(url= f"http://127.0.0.1:8000/user/{token}")
    if response.status_code >= 400:
        raise HTTPException(status_code=response.status_code, detail= "Invalid  it User")
    
    user_data = response.json()["data"]
    request.state.user = user_data
    