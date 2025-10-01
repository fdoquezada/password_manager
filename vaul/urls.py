from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('add/', views.add_password, name='add_password'),
    path('reveal/<int:entry_id>/', views.reveal_password, name='reveal_password'),
    path('edit/<int:entry_id>/', views.edit_password, name='edit_password'),
    path('delete/<int:entry_id>/', views.delete_password, name='delete_password'),
    path('help/', views.help_view, name='help'),
    path('logs/', views.reveal_logs, name='reveal_logs'),
]
