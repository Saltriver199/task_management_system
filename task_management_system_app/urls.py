'''from django.urls import path, include
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.user_login, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.LogoutPage, name='logout'),
    path('categories/', views.category_list, name='category_list'),
    path('categories/create/', views.create_category, name='create_category'),
    path('categories/update/<int:pk>/', views.update_category, name='update_category'),
    path('categories/<int:category_id>/delete/', views.delete_category, name='delete_category'),
    path('categories/<int:category_id>/tasks/', views.category_tasks, name='category_tasks'),
    path('tasks/create/', views.create_task, name='create_task'),
    path('tasks/<int:task_id>/update/', views.update_task, name='update_task'),
    path('tasks/<int:task_id>/employee_update_status/', views.employee_update_task_status, name='employee_update_task_status'),
    path('tasks/<int:task_id>/delete/', views.delete_task, name='delete_task'),
    path('employee_dashboard/', views.employee_dashboard, name='employee_dashboard'),
    path('employee_task/', views.employee_task, name='employee_task'),
    path('assigned_repairs/', views.view_assigned_repairs, name='assigned_repairs'),
    path('clock_out/', views.clock_out, name='clock_out'),
    path('dashboard/', views.employee_dashboard, name='dashboard'),  # Assuming dashboard redirects to admin view
    path('password_change/', auth_views.PasswordChangeView.as_view(template_name='registration/password_change.html'), name='password_change'),
    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(template_name='registration/password_change_done.html'), name='password_change_done'),
]'''
from django.urls import path, include
from . import views
from people_management.views import CustomPasswordChangeView

urlpatterns = [
    path('', views.user_login, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.LogoutPage, name='logout'),
    path('categories/', views.category_list, name='category_list'),
    path('categories/create/', views.create_category, name='create_category'),
    path('categories/update/<int:pk>/', views.update_category, name='update_category'),
    path('categories/<int:category_id>/delete/', views.delete_category, name='delete_category'),
    path('categories/<int:category_id>/tasks/', views.category_tasks, name='category_tasks'),
    path('tasks/create/', views.create_task, name='create_task'),
    path('tasks/<int:task_id>/update/', views.update_task, name='update_task'),
    path('tasks/<int:task_id>/employee_update_status/', views.employee_update_task_status, name='employee_update_task_status'),
    path('tasks/<int:task_id>/delete/', views.delete_task, name='delete_task'),
    path('employee_dashboard/', views.employee_dashboard, name='employee_dashboard'),
    path('employee_task/', views.employee_task, name='employee_task'),
    path('assigned_repairs/', views.view_assigned_repairs, name='assigned_repairs'),
    path('clock_out/', views.clock_out, name='clock_out'),
    path('password_change/', CustomPasswordChangeView.as_view(template_name='registration/change_password.html'), name='password_change'),
    path('password_change/done/', CustomPasswordChangeView.as_view(template_name='registration/password_change_done.html'), name='password_change_done'),
]