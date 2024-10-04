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
        cls.r.hset(name, key, json.dumps(value, default=str))
        return True
    
    @classmethod
    def get(cls, name):
        """
        Description : Thus function is called for getting values in note caches
        Parameter:
        cls: By default it tkes
        name : take user id and gives all notes from particular id
        """
        note = cls.r.hgetall(name)
        return note
    
    @classmethod
    def put(cls, name, key, value):
        """
        Description : Thus function is called for updating values in note caches
        Parameter:
        cls: By default it tkes
        name: for user id
        key : for note id
        value : note data
        """
        put_note = cls.r.hset(name, key, json.dumps(value, default=str))
        return put_note

    @classmethod
    def delete(cls, name, key):
        """
        Description : Thus function is called for saving values in note caches
        Parameter:
        cls: By default it tkes
        name: for user id
        ket : for note id
        """
        del_note = cls.r.hdel(name, key)
        return del_note
    
# class for creating and storing caches of lables data in database = 1
class JwtUtilsLables():
    # staring rediis chaching with configuration and database set at 1
    r = redis.Redis(host='localhost', port=6379, decode_responses=True, db = 1) 

    @classmethod
    def save(cls, name, key, value):
        """
        Description : Thus function is called for saving values in lable caches
        Parameter:
        cls: By default it tkes
        key: for user id
        field : for lable id
        value : lable data
        """
        cls.r.hset(name, key, json.dumps(value, default=str))
        return True
    
    @classmethod
    def get(cls, name):
        """
        Description : Thus function is called for getting values in lable caches
        Parameter:
        cls: By default it tkes
        name : take user id and gives all lables from particular id
        """
        note = cls.r.hgetall(name)
        return note
    
    @classmethod
    def put(cls, name, key, value):
        """
        Description : Thus function is called for updating values in lable caches
        Parameter:
        cls: By default it tkes
        name: for user id
        key : for lable id
        value : lable data
        """
        put_note = cls.r.hset(name, key, json.dumps(value, default=str))
        return put_note

    @classmethod
    def delete(cls, name, key):
        """
        Description : Thus function is called for saving values in lable caches
        Parameter:
        cls: By default it tkes
        name: for user id
        ket : for lable id
        """
        del_note = cls.r.hdel(name, key)
        return del_note