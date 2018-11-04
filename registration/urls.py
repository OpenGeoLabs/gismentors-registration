from django.urls import path, include

from . import views

urlpatterns = [
    path('', views.courses, name='courses'),
    path('json/', views.courses_json, name='courses_json'),
    path('atom/', views.courses_atom, name='courses_atom'),
    path('<int:course_id>/', views.course, name='course'),
    path('views/<int:course_id>/certificates', views.certificates, name='course'),
]
