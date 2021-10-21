from django.urls import path
from . import views

urlpatterns = [
    path('', views.homepage, name='home'),
    path('register/',  views.register_request, name='register')
    ]