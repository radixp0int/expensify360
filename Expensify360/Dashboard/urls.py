from django.urls import path
from . import views

urlpatterns = [
    path('', views.homepage, name='home'),
    path('create_organization/', views.create_org, name='create_org'),
    path('create_project/', views.create_proj, name='create_proj'),
    path('success/', views.org_success, name='org_success'),
    path('project-success/', views.proj_success, name='proj_success')
    ]
