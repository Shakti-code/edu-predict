from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Face-based Password Reset
    path('password-reset/', views.face_reset_request, name='password_reset'),
    path('password-reset/verify/<str:username>/', views.face_verify, name='face_verify'),
    path('password-reset/confirm/<str:username>/', views.face_reset_confirm, name='password_reset_confirm'),
]
