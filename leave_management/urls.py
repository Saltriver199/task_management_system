from django.urls import path
from . import views

urlpatterns = [
    path('apply/', views.apply_leave, name='apply_leave'),
    path('history/', views.leave_history, name='leave_history'),
    path('review/', views.leave_review_list, name='leave_review_list'),
    path('review/<int:pk>/', views.review_leave, name='review_leave'),
]