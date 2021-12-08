from django.urls import path
from . import views

urlpatterns = [
    path('', views.homepage, name='home'),
    path('create_organization/', views.create_org, name='create_org'),
    path('create_project/', views.create_proj, name='create_proj'),
    path('add_user/', views.manage_users, name='add_user'),
    path('add_to_group/', views.manage_users, name='add_to_group'),
    path('add_to_project/', views.manage_users, name='add_to_project'),
    path('user_management/', views.manage_users, name='user_management'),
    path('user_management/change_user_permissions/', views.manage_permissions, name='change_user_permissions'),
    path('expense_manager/', views.expense_manager, name='expense_manager'),
    path('expense_history/', views.expense_history, name='expense_history'),
    path('user_management/remove-user', views.remove_user, name='remove-user')
]
