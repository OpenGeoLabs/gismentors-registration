from django.urls import path, include

from . import views

urlpatterns = [
    path('', views.courses, name='courses'),
    path('<int:course_id>/', views.course, name='course'),
]
