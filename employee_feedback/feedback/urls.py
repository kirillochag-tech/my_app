from django.urls import path
from . import views

app_name = 'feedback'

urlpatterns = [
    path('', views.feedback_list, name='feedback_list'),
    path('results/', views.results_view, name='results'),
    path('results/<int:task_id>/', views.results_detail, name='results_detail'),
    path('statistics/', views.statistics_view, name='statistics'),
]