from django.urls import path
from recruiter import views
from django.contrib.auth.views import LogoutView
from django.contrib.auth import views as auth_views
urlpatterns = [
    path('login/', views.recruiter_login,name='recruiter_login'),
    path('dashboard/', views.recruiter_dashboard,name='recruiter_dashboard'),
    path('postjob/', views.post_job,name='post_job'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    path('managejob',views.manage_job,name='manage_job'),
    path('removejob/<int:job_id>/', views.remove_job, name='remove_job'),
    path('view-applicants/<int:job_id>/', views.view_applicants, name='view_applicants'),
    path('accept-application/<int:application_id>/', views.accept_application, name='accept_application'),
    path('decline-application/<int:application_id>/', views.decline_application, name='decline_application'),
    path('view-resume/<int:application_id>/', views.view_resume, name='view_resume'),
]
