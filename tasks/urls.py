from django.urls import path
from . import views

app_name = 'tasks'

urlpatterns = [
    path('', views.task_list, name='task_list'),
    path('<int:task_id>/', views.task_detail, name='task_detail'),
    path('<int:task_id>/execute/', views.execute_task, name='execute_task'),
    path('<int:task_id>/result/', views.task_result, name='task_result'),
    path('create/', views.create_task, name='create_task'),
    path('photo_report/', views.create_photo_report_task, name='create_photo_report_task'),
]