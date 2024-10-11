import requests as http
from fastapi import Request, HTTPException
import redis
import json
from settings import settings

# Creating function with request parameter assign as Request type
def auth_user(request: Request):
    token = request.headers.get("Authorization")
    response = http.get(url= f"{settings.AUTHORIZATION}/{token}")
    if response.status_code >= 400:
        raise HTTPException(status_code=response.status_code, detail= "Invalid  it User")
    
    # the user data is extracted from the "data" field of the JSON response and stored in the user_data variable.
    # The user_data is stored in the request.state object. 
    # The state attribute is a way to store information that is available throughout the entire request lifecycle.

    user_data = response.json()["data"]
    request.state.user = user_data

# class for creating and storing cache for notes in redis database = 0
class JwtUtils():
    # staring rediis chaching with configuration and database set at 1
    r = redis.Redis(host='localhost', port=6379, decode_responses=True, db = 0)

    @classmethod
    def save(cls, name, key, value):
        """
        Description : Thus function is called for saving values in note caches
        Parameter:
        cls: By default it tkes
        key: for user id
        field : for note id
        value : note data
        """
        data = cls.r.hset(name, key, json.dumps(value, default=str))
        return data
    
    @classmethod
    def get(cls, name: str):
        """
        Description : Thus function is called for getting values in note caches
        Parameter:
        cls: By default it tkes
        name : take user id and gives all notes from particular id
        """
        data = cls.r.hgetall(name)
        return [json.loads(x) for x in data.values()]


    @classmethod
    def delete(cls, name, key):
        """
        Description : Thus function is called for saving values in note caches
        Parameter:
        cls: By default it tkes
        name: for user id
        key : for note id
        """
        del_note = cls.r.hdel(name, key)
        return del_note
    
# class for creating and storing caches of lables data in database = 1
class JwtUtilsLabels(JwtUtils):
    # staring rediis chaching with configuration and database set at 1
    r = redis.Redis(host='localhost', port=6379, decode_responses=True, db = 1) 

   