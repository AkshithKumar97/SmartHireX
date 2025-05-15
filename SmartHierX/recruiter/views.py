from django.shortcuts import render,redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Job
from django.views.decorators.cache import never_cache, cache_control
from django.contrib.auth.decorators import login_required
from django.contrib.messages import get_messages
from myApp.models import AppliedJob
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta
from django.http import FileResponse, Http404
import os
from django.conf import settings
# Create your views here.
def recruiter_login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            if user.is_superuser:  # ✅ Only allow superusers to login
                login(request, user)
                messages.success(request, "Login successful!")
                return redirect('recruiter_dashboard')  # ✅ Redirect to recruiter dashboard
            else:
                messages.error(request, "Access Denied! Only Superusers can login.")
        else:
            messages.error(request, "Invalid Username or Password")

    return render(request, 'recruiter/recruiter_login.html')


def superuser_required(user):
    return user.is_superuser

@never_cache
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='recruiter_login')
@user_passes_test(superuser_required, login_url='recruiter_login')  # Redirect unauthorized users
def recruiter_dashboard(request):
    # Get total jobs posted by the recruiter
    total_jobs = Job.objects.filter(posted_by=request.user).count()
    
    # Get new applicants (applications from the last 7 days)
    new_applicants = AppliedJob.objects.filter(
        job__posted_by=request.user,
        applied_at__gte=timezone.now() - timedelta(days=7)
    ).count()
    
    # Get scheduled interviews (applications with 'Accepted' status)
    scheduled_interviews = AppliedJob.objects.filter(
        job__posted_by=request.user,
        status='Accepted'
    ).count()
    
    context = {
        'total_jobs': total_jobs,
        'new_applicants': new_applicants,
        'scheduled_interviews': scheduled_interviews,
    }
    
    return render(request, 'recruiter/recruiter_dashboard.html', context)

@never_cache
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='recruiter_dashboard')
def post_job(request):
    if request.method == "POST":
        title = request.POST.get('title')
        company_name = request.POST.get('company_name')
        description = request.POST.get('description')
        location = request.POST.get('location')
        salary = request.POST.get('salary')
        job_type = request.POST.get('job_type')
        experience = request.POST.get('experience')
        qualification = request.POST.get('qualification')
        skills = request.POST.get('skills')
        deadline = request.POST.get('deadline')
        category = request.POST.get('category')

        # Save the job in the database
        job = Job.objects.create(
            title=title,
            company_name=company_name,
            description=description,
            location=location,
            salary=salary,
            job_type=job_type,
            experience=experience,
            qualification=qualification,
            skills=skills,
            deadline=deadline,
            category=category,
            posted_by = request.user
        )

        messages.success(request, "Job posted successfully!")
        return redirect('recruiter_dashboard')  # Redirect back to the dashboard

    return render(request, 'recruiter/post_job.html')


@login_required(login_url='recruiter_login')
@user_passes_test(superuser_required, login_url='recruiter_login')
def manage_job(request):
    # Check if user is authenticated
    if not request.user.is_authenticated:
        return redirect('recruiter_login')
        
    recruiter = request.user
    jobs = Job.objects.filter(posted_by=recruiter)\
        .annotate(application_count=Count('applications'))\
        .order_by('-application_count')
    search_query = request.GET.get('search', '')
    if search_query:
        jobs = jobs.filter(title__icontains=search_query)

    return render(request,'recruiter/manage_job.html', {'jobs': jobs})


from django.shortcuts import get_object_or_404


@login_required(login_url='recruiter_login')
@user_passes_test(superuser_required, login_url='recruiter_login')
def remove_job(request, job_id):
    job = get_object_or_404(Job, id=job_id, posted_by=request.user)
    job.delete()
    messages.success(request, "Job removed successfully.")
    return redirect('manage_job')


@login_required(login_url='recruiter_login')
@user_passes_test(superuser_required)
def view_applicants(request, job_id):
    job = get_object_or_404(Job, id=job_id, posted_by=request.user)
    applications = AppliedJob.objects.filter(job=job)
    return render(request, 'recruiter/view_applicants.html', {
        'job': job,
        'applications': applications
    })



@login_required(login_url='recruiter_login')
def accept_application(request, application_id):
    application = get_object_or_404(AppliedJob, id=application_id)
    application.status = 'Accepted'
    application.save()
    messages.success(request,'Application accepted!')
    return redirect('view_applicants', job_id=application.job.id)


@login_required(login_url='recruiter_login')
def decline_application(request, application_id):
    application = get_object_or_404(AppliedJob, id=application_id)
    application.status = 'Declined'
    application.save()
    messages.warning(request,'Application declined.')
    return redirect('view_applicants', job_id=application.job.id)

@login_required(login_url='recruiter_login')
@user_passes_test(superuser_required)
def view_resume(request, application_id):
    application = get_object_or_404(AppliedJob, id=application_id)
    
    # Check if the job belongs to the current recruiter
    if application.job.posted_by != request.user:
        raise Http404("You don't have permission to view this resume")
    
    # Check if resume exists
    if not application.resume:
        messages.error(request, "No resume uploaded for this application")
        return redirect('view_applicants', job_id=application.job.id)
    
    try:
        # Get the file path
        file_path = application.resume.path
        
        # Check if file exists
        if not os.path.exists(file_path):
            messages.error(request, "Resume file not found")
            return redirect('view_applicants', job_id=application.job.id)
        
        # Get the filename
        filename = os.path.basename(file_path)
        
        # Open the file and return it as a response
        response = FileResponse(open(file_path, 'rb'))
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
    
    except Exception as e:
        messages.error(request, f"Error viewing resume: {str(e)}")
        return redirect('view_applicants', job_id=application.job.id)
