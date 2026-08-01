"""
URL configuration for student_prediction project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
"""
from django.contrib import admin
from django.urls import path, include
from predictor.health import liveness, readiness

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('health/', liveness, name='health_liveness'),
    path('health/ready/', readiness, name='health_readiness'),
    path('', include('predictor.urls')),
]
