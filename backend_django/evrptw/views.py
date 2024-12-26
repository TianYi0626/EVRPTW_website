from django.shortcuts import render
import json
from django.http import HttpRequest, HttpResponse, JsonResponse, HttpResponseBadRequest
from evrptw.models import User, Client, Task, Cluster, Route
from utils.utils_request import BAD_METHOD, request_failed, request_success, return_field
from utils.utils_require import MAX_CHAR_LENGTH, CheckRequire, require
from utils.utils_time import get_timestamp
from utils.utils_jwt import generate_jwt_token, check_jwt_token
from django.contrib.auth.hashers import make_password, check_password
import matplotlib
matplotlib.use('Agg') 
import matplotlib.pyplot as plt
from django.http import HttpResponse
from io import BytesIO
from utils.load_clients import load_initial_clients
from utils.utils_loaddata import *
import numpy as np
from saved import global_vars
from sklearn.cluster import KMeans
from utils.acovrp import acovrp
import time
import pandas as pd

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
        user = User.objects.filter(name=username)
        if user:
            if check_password(password, user.password):
                token = generate_jwt_token(username)
                return JsonResponse({"code": 0, "info": "Succeed", "token": token, "name": username})
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
        if User.objects.exists():
            user = User.objects.filter(name=username)
            if user.exists():
                return request_failed(3, "该用户名已被使用", 401)
            else:
                hashed_password = make_password(password)
                User.objects.create(name=username, password=hashed_password)
                token = generate_jwt_token(username)
                return JsonResponse({"code": 0, "info": "Succeed", "token": token})
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
        return HttpResponseBadRequest("Error loading clients")

    if req.method == "POST":
        try:
            data = json.loads(req.body.decode("utf-8"))
        except json.JSONDecodeError as e:
            print(f"Invalid JSON in request: {e}")
            return HttpResponseBadRequest("Invalid JSON in request")

        k = data.get("k")
        user_name = data.get("userName")
        clusters = data.get("clusters")
        clusterList = [char == '1' for char in clusters]
        if len(clusterList) > k:
            clusterList = clusterList[:k]
        elif len(clusterList) < k:
            return HttpResponseBadRequest("Mismatch between 'k' and clusterList length")
            
        try:
            user = User.objects.get(name=user_name)
        except User.DoesNotExist:
            user = User.objects.first()

        tasks = Task.objects.filter(user=user, clusterK=k, clusters=clusters)
        cluster_group = Cluster.objects.filter(clusterK=k)
        if tasks.exists():
            task = tasks.first()
        elif cluster_group.exists():
            task = Task.objects.create(user=user, clusterK=k, status=1, clusters=clusters)
            cluster = cluster_group.first()
            task.cluster_label = cluster.cluster_label
            task.save()
        else:
            task = Task.objects.create(user=user, clusterK=k, status=1, clusters=clusters)
            cluster = Cluster.objects.create(clusterK=k)
            data = np.array([[client.location_lat, client.location_lng]
                            for client in Client.objects.all()])
            kmeans = KMeans(n_clusters=k, random_state=42)
            cluster_labels = kmeans.fit_predict(data)
            cluster.cluster_label = list(map(int, cluster_labels))
            cluster.save()
            task.cluster_label = list(map(int, cluster_labels))
            task.save()

        try:
            cluster_map = {
                    cluster_id: [i for i, label in enumerate(task.cluster_label) if label == cluster_id]
                    for cluster_id in range(len(clusterList))
                    if clusterList[cluster_id]
            }
            client_ids = [client_id for cluster_ids in cluster_map.values() for client_id in cluster_ids]
            clients = Client.objects.filter(id__in=client_ids)
            task.clients.set(clients)
            task.save()
        except Exception as e:
            return HttpResponseBadRequest("Failed to load clients")

        if not clients.exists():
            return HttpResponseBadRequest("No clients found in database")

        try:
            latitudes = [client.location_lat for client in Client.objects.all()]
            longitudes = [client.location_lng for client in Client.objects.all()]
            cluster_ids = task.cluster_label

            # unique_cluster_ids = np.unique(cluster_ids)
            unique_cluster_ids = [cluster_id for cluster_id in np.unique(cluster_ids) if clusterList[cluster_id]]

            colors = plt.cm.get_cmap('tab10', len(unique_cluster_ids))

            plt.figure(figsize=(8, 6))
            for cluster_id in unique_cluster_ids:
                if clusterList[cluster_id]:
                    cluster_latitudes = [latitudes[i] for i in range(len(latitudes)) if cluster_ids[i] == cluster_id]
                    cluster_longitudes = [longitudes[i] for i in range(len(longitudes)) if cluster_ids[i] == cluster_id]
                    plt.scatter(cluster_longitudes, cluster_latitudes, label=f'Cluster {cluster_id}', 
                                alpha=0.7, s=20, color=colors(cluster_id))
            plt.title('Client Locations')
            plt.xlabel('Longitude')
            plt.ylabel('Latitude')
        except Exception as e:
            return HttpResponseBadRequest("Plot generation failed")

        buffer = BytesIO()
        try:
            plt.savefig(buffer, format='png')
        except Exception as e:
            return HttpResponseBadRequest("Plot save failed")
        finally:
            plt.close()
        buffer.seek(0)

        return HttpResponse(buffer, content_type='image/png')
    else:
        return HttpResponseBadRequest("Unsupported method")

@CheckRequire
def route_img(req: HttpRequest):
   
    if req.method == "POST":
        try:
            data = json.loads(req.body.decode("utf-8"))
        except json.JSONDecodeError as e:
            print(f"Invalid JSON in request: {e}")
            return HttpResponseBadRequest("Invalid JSON in request")

        k = data.get("k")
        cluster_id = data.get("cluster_id")
        time = data.get("time")
        if cluster_id > k-1:
            return HttpResponseBadRequest("Mismatch between 'k' and cluster_id")

        routes = Route.objects.filter(clusterK=k, clusterId=cluster_id)
        cluster_group = Cluster.objects.filter(clusterK=k)
        if routes.exists():
            route = routes.first()
        else:
            if cluster_group.exists():
                route = Route.objects.create(clusterK=k, clusterId=cluster_id)
                cluster = cluster_group.first()
            else:
                route = Route.objects.create(clusterK=k, clusterId=cluster_id)
                cluster = Cluster.objects.create(clusterK=k)
                data = np.array([[client.location_lat, client.location_lng]
                                for client in Client.objects.all()])
                kmeans = KMeans(n_clusters=k, random_state=42)
                cluster_labels = kmeans.fit_predict(data)
                cluster.cluster_label = list(map(int, cluster_labels))
                cluster.save()

            try:
                cluster_map = {
                        cluster_id: [i for i, label in enumerate(cluster.cluster_label) if label == cluster_id]
                }
                client_ids = [client_id for cluster_ids in cluster_map.values() for client_id in cluster_ids]
                clients = Client.objects.filter(id__in=client_ids)
                route.clients.set(clients)
                route.save()
            except Exception as e:
                return HttpResponseBadRequest("Failed to load clients")

            if not clients.exists():
                return HttpResponseBadRequest("No clients found in database")

            num_ants = 10
            alpha = 1.0
            beta = 20.0
            rho = 0.15
            num_iterations = 500
            vehicle_capacity = [2.5, 16]
            service_time = 30

            distance_matrix_all, spendtm_matrix_all = load_distance('../data/input_distance_time.txt')
            distance_df_all = pd.DataFrame(distance_matrix_all)
            spendtm_df_all = pd.DataFrame(spendtm_matrix_all)

            client_nodes = [client.id for client in clients]
            nodes_with_depot = np.concatenate(([0], client_nodes))
            distance_df = distance_df_all.loc[nodes_with_depot, nodes_with_depot]
            spendtm_df = spendtm_df_all.loc[nodes_with_depot, nodes_with_depot]

            customer_demands = [[client.package_weight, client.package_volume] for client in clients]
            time_windows = [[client.timewindow_start, client.timewindow_end] for client in clients]

            best_cost, best_solution, cost_iteration, iteration_time = acovrp(num_ants, alpha, beta, rho, num_iterations, 
                distance_df, spendtm_df, vehicle_capacity, customer_demands, time_windows, service_time, time, False)

            route.path = best_solution
            route.save()

        try:
            locations = [[client.location_lat, client.location_lng] for client in Client.objects.all()]
            id_to_location = {row['ID']: (row['lat'], row['lng']) for _, row in locations.iterrows()}

            plt.figure(figsize=(12, 10))
            colors = plt.cm.tab20(np.linspace(0, 1, len(route.path)))
            for i, path in enumerate(route.path):
                color = colors[i]
                for j in range(len(path) - 1):
                    start = path[j]
                    end = path[j + 1]
                    start_coords = id_to_location[start]
                    end_coords = id_to_location[end]
                    latitudes = [start_coords[0], end_coords[0]]
                    longitudes = [start_coords[1], end_coords[1]]
                    plt.plot(longitudes, latitudes, color=color, marker='o', zorder=1, label=f'Vehicle {i + 1}' if j == 0 else "")
            
            for i, path in enumerate(route.path):
                for j in range(len(path)):
                    if path[j] == 0:
                        start = path[j]
                        start_coords = id_to_location[start]
                        lng = start_coords[1]
                        lat = start_coords[0]
                        plt.scatter(lng, lat, color='red', marker='*')
                    elif path[j] > 1000:
                        start = path[j]
                        start_coords = id_to_location[start]
                        lng = start_coords[1]
                        lat = start_coords[0]
                        plt.scatter(lng, lat, color='black', marker='o', zorder=2)
                    
            plt.xlabel("Longitude")
            plt.ylabel("Latitude")
            plt.title(f"Routes")

        except Exception as e:
            return HttpResponseBadRequest("Plot generation failed")

        buffer = BytesIO()
        try:
            plt.savefig(buffer, format='png')
        except Exception as e:
            return HttpResponseBadRequest("Plot save failed")
        finally:
            plt.close()
        buffer.seek(0)

        return HttpResponse(buffer, content_type='image/png')
    else:
        return HttpResponseBadRequest("Unsupported method")

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