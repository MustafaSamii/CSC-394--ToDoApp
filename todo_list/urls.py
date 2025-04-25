from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.landing, name='landing'),
    path('register/', views.register, name='register'),
    path('login/', views.custom_login, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('todos/new/', views.create_todo, name='create_todo'),
    path('todos/delete/<int:todo_id>/', views.delete_todo, name='delete_todo'),
    path('todos/edit/<int:todo_id>/', views.update_todo, name='update_todo'),
    path('about/', views.about, name='about'),
    path('teams/<int:team_id>/delete/', views.delete_team, name='delete_team'),
    path('todos/toggle/<int:todo_id>/<str:action>/', views.update_todo_status, name='update_todo_status'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('todos/', views.todos_list, name='todos'),
    path('teams/', views.teams_list, name='teams_list'),
    path('teams/<int:team_id>/', views.team_details, name='team_details'),
    path('teams/new/', views.create_team, name='create_team'),
    path('password-reset/', auth_views.PasswordResetView.as_view(template_name="password_reset.html"), 
         name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(template_name="password_reset_done.html"), 
         name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name="password_reset_confirm.html"), 
         name='password_reset_confirm'),
    path('password-reset-complete/',auth_views.PasswordResetCompleteView.as_view(template_name="password_reset_complete.html"), 
         name='password_reset_complete'),
    path('get_category_team/', views.get_categ_teams, name='get_category_team'),
]
