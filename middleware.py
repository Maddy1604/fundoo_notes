from fastapi import FastAPI, Request
from notes_services.utils import MiddleWare
import json
from notes_services.route import app

@app.middleware("http")
async def log_request(request : Request, call_next):
    method = request.method
    endpoint = str(request.url.path)

    # Created redis key as request method
    redis_key = method

    # Fetching existing logs 
    redis_instance = MiddleWare()
    request_log = redis_instance.get(key=redis_key)

    # If exsting log is not present then creating new log
    if not request_log:
        request_log = {}
    else:
        request_log = json.loads(request_log)
    print(request_log)
    # Updating counting for each endpoint
    if endpoint in request_log:
        request_log[endpoint] += 1
    else:
        request_log[endpoint] = 1

    # Save the changes in redis DB
    redis_instance.save(key=redis_key, value=json.dumps(request_log))

    # Continue wiht next endpoint
    response = await call_next(request_log)
    return response
