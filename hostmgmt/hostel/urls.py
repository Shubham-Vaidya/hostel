from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),

    path('rooms/', views.rooms, name='rooms'),
    path('students/', views.students, name='students'),

    path('allocation/', views.allocation, name='allocation'),

    path('allocation/fswd/', views.fswd_allocation, name='fswd'),
    path('allocation/aiml/', views.aiml_allocation, name='aiml'),
    path('allocation/devops/', views.devops_allocation, name='devops'),
]