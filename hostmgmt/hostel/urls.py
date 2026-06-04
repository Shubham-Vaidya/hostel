from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard),
    path('rooms/', views.rooms),
    path('students/', views.students),
    path('allocation/', views.allocation),
]