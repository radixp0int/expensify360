from django.urls import path
from . import views

urlpatterns = [
    path('accounts/sign_up', views.sign_up, name='signup'),
    path('magic/', views.demo_creation_hack) # not for production use!
    ]
