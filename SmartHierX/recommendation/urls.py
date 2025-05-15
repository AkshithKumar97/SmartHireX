from django.urls import path
from . import views

urlpatterns = [
    #changed name
    path('recommendations/', views.recommend_jobs, name='recommend_jobs'),
    path('test-1/', views.test, name='test'),
    path('clear-resume/', views.clear_resume_and_redirect, name='clear_resume_and_redirect'),
]
