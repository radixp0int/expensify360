from django.urls import path
from . import views

urlpatterns = [
    path('expense/', views.expense, name='expense'),
    path('expense/MileageEntry', views.mileageEntry, name='mileageEntry'),
    path('expense/ExpenseEntry', views.expenseEntry, name='expenseEntry'),
    path('expense/TimeEntry', views.timeEntry, name='timeEntry'),
    path('expense_approval/', views.expense_approval, name='expense_approval')
]
