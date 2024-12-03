from django.shortcuts import render
import json
from django.http import HttpRequest, HttpResponse, JsonResponse
from evrptw.models import User
from utils.utils_request import BAD_METHOD, request_failed, request_success, return_field
from utils.utils_require import MAX_CHAR_LENGTH, CheckRequire, require
from utils.utils_time import get_timestamp
from utils.utils_jwt import generate_jwt_token, check_jwt_token
from django.contrib.auth.hashers import make_password, check_password

@CheckRequire
def startup(req: HttpRequest):
    return HttpResponse("Congratulations! You have successfully installed the requirements. Go ahead!")

@CheckRequire
def login(req: HttpRequest):
    if req.method != "POST":
        return BAD_METHOD
    
    # Request body example: {"userName": "Ashitemaru", "password": "123456"}
    body = json.loads(req.body.decode("utf-8"))
    
    username = require(body, "userName", "string", err_msg="Missing or error type of [userName]")
    password = require(body, "password", "string", err_msg="Missing or error type of [password]")

    try:
        user = User.objects.filter(username=username).first()
        if user:
            if check_password(password, user.password):
                token = generate_jwt_token(username)
                return JsonResponse({"code": 0, "info": "Succeed", "token": token})
            else:
                return request_failed(2, "Wrong password", 401)
        else:
            hashed_password = make_password(password)
            User.objects.create(username=username, password=hashed_password)
            token = generate_jwt_token(username)
            return JsonResponse({"code": 0, "info": "Succeed", "token": token})

    except Exception as e:
        return request_failed(3, f"An error occurred: {str(e)}", 500)

@CheckRequire
def boards(req: HttpRequest):
    if req.method == "GET":
        params = req.GET
    elif req.method == "POST":
        jwt_token = req.headers.get("Authorization")
        body = json.loads(req.body.decode("utf-8"))
        
        # TODO Start: [Student] Finish the board view function according to the comments below
        
        # First check jwt_token. If not exists, return code 2, "Invalid or expired JWT", http status code 401
        
        # Then invoke `check_for_board_data` to check the body data and get the board_state, board_name and user_name. Check the user_name with the username in jwt_token_payload. If not match, return code 3, "Permission denied", http status code 403
        
        # Find the corresponding user instance by user_name. We can assure that the user exists.
        
        # We lookup if the board with the same name and the same user exists.
        ## If not exists, new an instance of Board type, then save it to the database.
        ## If exists, change corresponding value of current `board`, then save it to the database.
        
        return request_failed(1, "Not implemented", 501)
        
        # TODO End: [Student] Finish the board view function according to the comments above
        
    else:
        return BAD_METHOD


@CheckRequire
def tasks_index(req: HttpRequest, index: any):
    
    idx = require({"index": index}, "index", "int", err_msg="Bad param [id]", err_code=-1)
    assert idx >= 0, "Bad param [id]"
    
    if req.method == "GET":
        params = req.GET
    
    elif req.method == "DELETE":
        # TODO Start: [Student] Finish the board_index view function
        return request_failed(1, "Not implemented", 501)
        # TODO End: [Student] Finish the board_index view function
    
    else:
        return BAD_METHOD


@CheckRequire
def user(req: HttpRequest, userName: any):
    user_name = require({"user name": userName}, "user name", "string", 
                        err_msg="Bad param [name]", err_code=-1)
    assert user_name == "", "Bad param [name]"
    
    if req.method == "GET":
        params = req.GET
    elif req.method == "POST":
        params = req.POST
    elif req.method == "DELETE":
        return request_failed(1, "Not implemented", 501)
    else:
        return BAD_METHOD