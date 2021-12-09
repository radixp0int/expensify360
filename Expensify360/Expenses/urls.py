from django.urls import path
from . import views

urlpatterns = [
    path('expense/', views.expense, name='expense'),
    path('expense/MileageEntry', views.mileageEntry, name='mileageEntry'),
    path('expense/ExpenseEntry', views.expenseEntry, name='expenseEntry'),
    path('expense/TimeEntry', views.timeEntry, name='timeEntry'),
    path('expense/expense_editing', views.editExpense, name='editExpense'),
    path('expense/mileage_editing', views.editMileage, name='editMileage'),
    path('expense/time_editing', views.editTime, name='editTime'),
    # path('expense_manager/', views.expense_manager, name='expense_manager')
]
