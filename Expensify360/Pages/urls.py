from django.urls import path
from . import views

urlpatterns = [
    path('', views.homepage, name='home'),
    path('accounts/sign_up', views.sign_up, name='signup')
    ]
