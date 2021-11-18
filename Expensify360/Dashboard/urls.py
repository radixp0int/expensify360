from django.urls import path
from . import views
from Dashboard.dash_apps.finished_apps import simpleexample

urlpatterns = [
    path('', views.homepage, name='home'),
    path('create_organization/', views.create_org, name='create_org'),
    path('create_project/', views.create_proj, name='create_proj'),
    path('user_management/', views.manage_users, name='user_management'),
    path('add_user/', views.manage_users, name='add_user'),
    path('add_to_group', views.manage_users, name='add_to_group'),
    ]
