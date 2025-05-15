from django.urls import path, include
from django.contrib.auth.views import LogoutView
from . import views
from .models import Job

urlpatterns = [
    path('',views.home,name = 'home'),
    path('student-login/',views.student_login,name='student_login'),
    path('student-registration/',views.student_registration,name='student_registration'),
    path('login-sucessfull/',views.login_sucess,name='login_sucess'),
    path('student_logout/', views.logout_view, name='student_logout'),

    path('logout/', LogoutView.as_view(next_page = "student_login"), name='logout'),
    path("accounts/", include("django.contrib.auth.urls")),
    path('student-dashboard/',views.student_dashboard,name='student_dashboard'),
    path('job-listings/', views.job_listings, name='job_listings'),
    path('job-details/<int:job_id>/', views.job_details, name='job_details'),
    path('apply-job/<int:job_id>/', views.apply_job, name='apply_job'),
    path('reject-job/<int:job_id>/', views.reject_job, name='reject_job'),
    path('upload-resume/<int:job_id>/', views.upload_resume_and_apply, name='upload_resume'),
    path('message-recruiter/<int:job_id>/', views.message_recruiter, name='message_recruiter'),
    path('applied-jobs/', views.student_applied_jobs, name='student_applied_jobs'),
]