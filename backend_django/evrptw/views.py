from django.shortcuts import render
import json
from django.http import HttpRequest, HttpResponse, JsonResponse, HttpResponseBadRequest
from evrptw.models import User, Client
from utils.utils_request import BAD_METHOD, request_failed, request_success, return_field
from utils.utils_require import MAX_CHAR_LENGTH, CheckRequire, require
from utils.utils_time import get_timestamp
from utils.utils_jwt import generate_jwt_token, check_jwt_token
from utils.utils_cluster import cluster_kmeans
from django.contrib.auth.hashers import make_password, check_password
import matplotlib
matplotlib.use('Agg') 
import matplotlib.pyplot as plt
from django.http import HttpResponse
from io import BytesIO
from utils.load_clients import load_initial_clients
import numpy as np
from saved import global_vars

@CheckRequire
def startup(req: HttpRequest):
    return HttpResponse("Congratulations! You have successfully installed the requirements. Go ahead!")

@CheckRequire
def login(req: HttpRequest):
    if req.method != "POST":
        return BAD_METHOD
    
    # Request body example: {"userName": "Ashitemaru", "password": "123456"}
    body = json.loads(req.body.decode("utf-8"))
    
    username = require(body, "userName", "string", err_msg="用户名格式错误")
    password = require(body, "password", "string", err_msg="密码格式错误")

    try:
        user = User.objects.filter(name=username).first()
        if user:
            if check_password(password, user.password):
                token = generate_jwt_token(username)
                return JsonResponse({"code": 0, "info": "Succeed", "token": token})
            else:
                return request_failed(2, "密码错误", 401)
        else:
            return request_failed(1, "用户不存在", 401)

    except Exception as e:
        return request_failed(4, f"发生错误：{str(e)}", 500)

@CheckRequire
def registry(req: HttpRequest):
    if req.method != "POST":
        return BAD_METHOD

    # Request body example: {"userName": "Ashitemaru", "password": "123456"}
    body = json.loads(req.body.decode("utf-8"))
    
    username = require(body, "userName", "string", err_msg="用户名格式错误")
    password = require(body, "password", "string", err_msg="密码格式错误")

    try:
        user = User.objects.filter(name=username).first()
        if user:
            return request_failed(3, "该用户名已被使用", 401)
        else:
            hashed_password = make_password(password)
            User.objects.create(name=username, password=hashed_password)
            token = generate_jwt_token(username)
            return JsonResponse({"code": 0, "info": "Succeed", "token": token})

    except Exception as e:
        return request_failed(4, f"发生错误：{str(e)}", 500)

@CheckRequire
def update_k(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            k = data.get("k")  # Extract k from the request body
            if k is None:
                return HttpResponseBadRequest("k is required")
            print(f"Received k: {k}")
            global_vars.k = k
            # Perform any additional logic with k here
            return JsonResponse({"code": 0, "info": "Succeed", "k": k})
        except json.JSONDecodeError:
            return HttpResponseBadRequest("Invalid JSON")
    return HttpResponseBadRequest("Invalid HTTP method")

@CheckRequire
def location_img(req: HttpRequest):
    try:
        load_initial_clients()
    except Exception as e:
        print(f"Error loading clients: {e}")
        return HttpResponseBadRequest("Failed to load initial clients")

    if req.method == "GET":
        cluster_kmeans(global_vars.k)
        
        clients = Client.objects.all()
        if not clients.exists():
            print("No clients found in database.")
            return HttpResponseBadRequest("No clients found")
        latitudes = [client.location_lat for client in clients]
        longitudes = [client.location_lng for client in clients]
        cluster_ids = [client.cluster_id for client in clients]

        unique_cluster_ids = np.unique(cluster_ids)
        colors = plt.cm.get_cmap('tab10', len(unique_cluster_ids))

        # Create the scatter plot
        plt.figure(figsize=(8, 6))
        for cluster_id in unique_cluster_ids:
            # Plot clients that belong to the current cluster
            cluster_latitudes = [latitudes[i] for i in range(len(latitudes)) if cluster_ids[i] == cluster_id]
            cluster_longitudes = [longitudes[i] for i in range(len(longitudes)) if cluster_ids[i] == cluster_id]
            plt.scatter(cluster_longitudes, cluster_latitudes, label=f'Cluster {cluster_id}', 
                        alpha=0.7, s=20, color=colors(cluster_id))
        plt.title('Client Locations')
        plt.xlabel('Longitude')
        plt.ylabel('Latitude')

        # Save the plot to a BytesIO buffer
        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        plt.close()
        buffer.seek(0)

        # Serve the image as an HTTP response
        return HttpResponse(buffer, content_type='image/png') 
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