"""
URL configuration for task_management_system project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from . import views

urlpatterns = [
    path('dashboard', views.dashboard, name='dashboard'),
    path('create/', views.create_employee, name='create_employee'),
    path('list/', views.employee_list, name='employee_list'),
    path('update/<int:employee_id>/', views.update_employee, name='update_employee'),
    path('delete/<int:employee_id>/', views.delete_employee, name='delete_employee'),
    path('complains/', views.complain_list, name='complain_list'),
    path('complains/new/', views.complain_create, name='complain_create'),
    path('complains/<int:complain_id>/update/', views.update_complain, name='update_complain'),
    path('complains/<int:complain_id>/delete/', views.delete_complain, name='delete_complain'),
    path('repairs/<int:complain_id>/', views.repair_detail, name='repair_detail'),
    path('repairs/add/<int:complain_id>/', views.repair_create, name='repair_create'),
    path('repairs/edit/<int:repair_id>/', views.repair_update, name='repair_update'),
    path('repairs/delete/<int:repair_id>/', views.repair_delete, name='repair_delete'),
]





