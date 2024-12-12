from django.urls import path
from . import views

urlpatterns = [
    path('', views.startup, name='startup'),
    path('login', views.login, name='login'),
    path('update_k', views.update_k, name='update_k'),
    path('location_img', views.location_img, name='location_img'),
    path('registry', views.registry, name='registry'),
]
