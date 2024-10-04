import requests as http
from fastapi import Request, HTTPException
import redis
import json

# Creating function with request parameter assign as Request type
def auth_user(request: Request):
    token = request.headers.get("Authorization")
    response = http.get(url= f"http://127.0.0.1:8000/user/{token}")
    if response.status_code >= 400:
        raise HTTPException(status_code=response.status_code, detail= "Invalid  it User")
    
    # the user data is extracted from the "data" field of the JSON response and stored in the user_data variable.
    # The user_data is stored in the request.state object. 
    # The state attribute is a way to store information that is available throughout the entire request lifecycle.

    user_data = response.json()["data"]
    request.state.user = user_data
    
class JwtUtils():
    r = redis.Redis(host='localhost', port=6379, decode_responses=True, db = 0)

    @classmethod
    def save(cls, key, field, value):
        cls.r.hset(key, field, json.dumps(value, default=str))
        return True
    
    @classmethod
    def get(cls, key):
        cls.r.get(key)
        return {
            "data" : json.dumps()
        }
    
    @classmethod
    def delete(cls, key):
        cls.r.delete(key)
        return True
