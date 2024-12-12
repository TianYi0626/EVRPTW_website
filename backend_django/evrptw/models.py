from utils import utils_time
from django.db import models
from utils.utils_request import return_field

from utils.utils_require import MAX_CHAR_LENGTH

class User(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=MAX_CHAR_LENGTH, unique=True)
    password = models.CharField(max_length=MAX_CHAR_LENGTH)
    created_time = models.FloatField(default=utils_time.get_timestamp)
    
    class Meta:
        indexes = [models.Index(fields=["name"])]
        
    def serialize(self):
        return {
            "id": self.id, 
            "name": self.name, 
            "createdAt": self.created_time
        }
    
    def __str__(self) -> str:
        return self.name

class Client(models.Model):
    id = models.BigAutoField(primary_key=True)
    node_id = models.IntegerField(default=0)
    is_depot = models.BooleanField(default=False)
    is_charger = models.BooleanField(default=True)
    package_weight = models.FloatField(default=0)
    package_volume = models.FloatField(default=0)
    location_lat = models.FloatField(default=39.792844)
    location_lng = models.FloatField(default=116.571614)
    timewindow_start = models.IntegerField(default=0)
    timewindow_end = models.IntegerField(default=960)
    serve_time = models.IntegerField(default=30)
    cluster_id = models.IntegerField(default=0)

    def __str__(self) -> str:
        return str(id)
    
class Route(models.Model):
    id = models.BigAutoField(primary_key=True)
    path = models.JSONField()
    vehicle = models.IntegerField(default=1)
    
    def __str__(self) -> str:
        return str(id)

class Task(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    clients = models.ManyToManyField(to=Client, related_name="tasks")
    solution = models.ManyToManyField(to=Route)
    
    def __str__(self) -> str:
        return str(id)
    
