from django.urls import path
from . import views

urlpatterns = [
    path('mileage/', views.mileage, name='mileage')
]
