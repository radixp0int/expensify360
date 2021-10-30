from django.urls import path
from . import views

urlpatterns = [
    path('', views.homepage, name='home'),
    path('create_organization/', views.create_org, name='create_org')
    ]
