from django.urls import path
from . import views
from . import files

urlpatterns = [
    path('', views.startup, name='startup'),
    path('login', views.login, name='login'),
    path('update_k', views.update_k, name='update_k'),
    path('location_img', views.location_img, name='location_img'),
    path('registry', views.registry, name='registry'),
    path('route_img', views.route_img, name='route_img'),
    path('node_file', files.node_file, name='node_file'),
    path('dw_file', files.dw_file, name='dw_file')
]
