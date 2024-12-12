from sklearn.cluster import KMeans
import openpyxl
from evrptw.models import Client
from django.db import transaction
import numpy as np

shape_map = {
    0: 'o',  # 圆形
    1: 's',  # 正方形
    2: 'D',  # 菱形
    3: '^',  # 三角形（向上）
    4: 'v',  # 反三角形（向下）
    5: '<',  # 左三角形
    6: '>',  # 右三角形
    7: 'p',  # 五边形
    8: '*',  # 星形
    9: 'X',  # 交叉
}

def cluster_kmeans(k=10):
    clients = Client.objects.all()

    data = np.array([[client.location_lat, client.location_lng]
                     for client in clients])

    kmeans = KMeans(n_clusters=k, random_state=42)

    cluster_labels = kmeans.fit_predict(data)

    with transaction.atomic():
        for i, client in enumerate(clients):
            client.cluster_id = cluster_labels[i]
        
        # Bulk update the clients in the database
        Client.objects.bulk_update(clients, ['cluster_id'])
