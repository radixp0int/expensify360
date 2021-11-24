from django.urls import path
from . import views

urlpatterns = [
    path('expense/', views.expense, name='expense'),
    path('expense/MileageEntry', views.mileageEntry, name='mileageEntry'),
    path('expense/ExpenseEntry', views.expenseEntry, name='expenseEntry'),
    path('expense/TimeEntry', views.timeEntry, name='timeEntry'),
]
