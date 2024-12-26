from django.http import HttpRequest
import json
from django.http import HttpRequest, HttpResponse, JsonResponse, HttpResponseBadRequest
from evrptw.models import User
from utils.utils_request import BAD_METHOD, request_failed, request_success, return_field
from utils.utils_require import MAX_CHAR_LENGTH, CheckRequire, require
import matplotlib
matplotlib.use('Agg') 
from io import BytesIO
from utils.utils_loaddata import *
import numpy as np
from saved import global_vars
import pandas as pd
import os

@CheckRequire
def node_file(req: HttpRequest):
    if req.method != "POST":
        return BAD_METHOD

    try:
        data = json.loads(req.body.decode("utf-8"))
    except json.JSONDecodeError as e:
        print(f"Invalid JSON in request: {e}")
        return HttpResponseBadRequest("Invalid JSON in request")

    user_name = data.get("userName")
    uploaded_file = req.FILES.get("file")

    if not uploaded_file.name.endswith('.xlsx'):
        return HttpResponseBadRequest("Uploaded file is not an Excel file")

    try:
        file_data = uploaded_file.read()
        
        excel_file = BytesIO(file_data)
        data = pd.read_excel(excel_file)

        location = data[['ID', 'type', 'lng', 'lat']]
        time_windows = data[['ID', 'first_receive_tm', 'last_receive_tm']]
        packages = data[['ID', 'pack_total_weight', 'pack_total_volume']]

        target_folder = f'data/{user_name}'
        if not os.path.exists(target_folder):
            os.makedirs(target_folder)
        location_path = os.path.join(target_folder, "location.xlsx")
        time_windows_path = os.path.join(target_folder, "time_windows.xlsx")
        packages_path = os.path.join(target_folder, "packages.xlsx")
        
        location.to_excel(location_path, index=False)
        time_windows.to_excel(time_windows_path, index=False)
        packages.to_excel(packages_path, index=False)
        
        return JsonResponse({"message": "File uploaded and read successfully"})
    
    except Exception as e:
        print(f"Error reading file: {e}")
        return HttpResponseBadRequest("Error reading file")

@CheckRequire
def dw_file(req: HttpRequest):
    if req.method != "POST":
        return BAD_METHOD

    try:
        data = json.loads(req.body.decode("utf-8"))
    except json.JSONDecodeError as e:
        print(f"Invalid JSON in request: {e}")
        return HttpResponseBadRequest("Invalid JSON in request")

    user_name = data.get("userName")
    uploaded_file = req.FILES.get("file")

    if not uploaded_file.name.endswith('.txt'):
        return HttpResponseBadRequest("Uploaded file is not an txt file")

    try:
        file_data = uploaded_file.read()
        
        excel_file = BytesIO(file_data)
        data = pd.read_excel(excel_file)

        nodes = sorted(set(data['from_node']).union(set(data['to_node'])))
        node_count = len(nodes)
        node_to_idx = {node: idx for idx, node in enumerate(nodes)}
        distance_matrix = np.zeros((node_count, node_count))
        time_matrix = np.zeros((node_count, node_count))

        np.fill_diagonal(distance_matrix, 0)

        count = 0
        for _, row in data.iterrows():
            from_idx = node_to_idx[row['from_node']]
            to_idx = node_to_idx[row['to_node']]
            distance_matrix[from_idx, to_idx] = row['distance']
            distance_matrix[to_idx, from_idx] = row['distance']
            time_matrix[from_idx, to_idx] = row['spend_tm']
            time_matrix[to_idx, from_idx] = row['spend_tm']
            count += 1
            if count == node_count:
                count = 0

        for i in range(node_count):
            distance_matrix[i, i] = np.finfo(float).eps
            time_matrix[i, i] = np.finfo(float).eps

        target_folder = f'data/{user_name}'
        if not os.path.exists(target_folder):
            os.makedirs(target_folder)
        distance_path = os.path.join(target_folder, "distance.xlsx")
        spend_time_path = os.path.join(target_folder, "spend_time.xlsx")

        distance_matrix = pd.DataFrame(distance_matrix)
        spend_time_matrix = pd.DataFrame(time_matrix)

        distance_matrix.to_excel(distance_path, index=False)
        spend_time_matrix.to_excel(spend_time_path, index=False)
        
        return JsonResponse({"message": "File uploaded and read successfully"})
    
    except Exception as e:
        print(f"Error reading file: {e}")
        return HttpResponseBadRequest("Error reading file")

