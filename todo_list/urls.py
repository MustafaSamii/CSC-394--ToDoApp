from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing, name='landing'),
    path('register/', views.register, name='register'),
    path('login/', views.custom_login, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('todos/new/', views.create_todo, name='create_todo'),
    path('todos/delete/<int:todo_id>/', views.delete_todo, name='delete_todo'),
    path('todos/edit/<int:todo_id>/', views.update_todo, name='update_todo'),
    path('todos/toggle/<int:todo_id>/', views.toggle_status, name='toggle_status'), 
     path('about/', views.about, name='about'),
]
