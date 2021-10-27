from django.urls import path
from . import views

urlpatterns = [
    path('expense/', views.expense, name='expense')
]
