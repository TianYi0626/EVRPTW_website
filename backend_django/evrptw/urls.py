from django.urls import path
from . import views

urlpatterns = [
    path('', views.startup, name='login'),  # Example route
    path('startup', views.startup, name='startup')
]
