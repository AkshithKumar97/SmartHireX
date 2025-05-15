from django.shortcuts import redirect
from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login,logout,get_user_model
from django.contrib import messages
from django.template.loader import get_template
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from recruiter.models import Job
from .models import AppliedJob,RejectedJob
from . import views
from django.views.decorators.cache import never_cache, cache_control
from django.contrib.auth.decorators import login_required
from django.contrib.messages import get_messages
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import FileSystemStorage
import os
from django.conf import settings
# Create your views here.
def home(request):
    return render(request,'myApp/home.html')

User = get_user_model() 

@never_cache
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def student_login(request):

    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')
        fullname = request.POST.get('fullname')

        try:
            user = User.objects.get(email=email)
            user = authenticate(request, username=user.username,password=password)
            if user is not None:
                
                login(request,user)
                messages.success(request,"Login successful!")
                return redirect('student_dashboard')
            else:
                messages.error(request,"Invalid credentials!")
        except User.DoesNotExist:
            messages.error(request, "user with this email does not exist!")

    return render(request,'myApp/student_login.html')

def student_registration(request):

    if request.method == "POST":
        fullname = request.POST.get('fullname')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirmPassword = request.POST.get('confirm-password')

        if password == confirmPassword:
            if User.objects.filter(username=email).exists():
                messages.error(request,"User with this email alredy exists!")
            else:###########
                user = User.objects.create_user(username=email,email=email,password=password)
                user.first_name = fullname
                user.save()
                messages.success(request,"Account created successfully! Please login.")
                return redirect('student_login')
        else:
            messages.error(request,"Password do not match!")

    return render(request,'myApp/student_registration.html')


@login_required(login_url='student_login')
def login_sucess(request):
    if request.user.is_authenticated:
        return render(request,'myApp/student_dashboard.html')
    return redirect('student_login')

@login_required(login_url='student_login')
def logout_view(request):

    list(get_messages(request))


    logout(request)
    messages.success(request, "You have been logged out successfully!")
    return redirect('student_login')

@never_cache
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='student_login')
def student_dashboard(request):
    user = request.user
    # Applied Jobs Count
    applied_jobs_count = AppliedJob.objects.filter(student=user).count()

    # Saved Jobs Count (Only if you have a model like SavedJob)
    # If you don't have a SavedJob model, either comment this or create it
    # saved_jobs_count = SavedJob.objects.filter(student=user).count()
    saved_jobs_count = 0  # Placeholder until you implement saved job logic

    # Upcoming Interviews Count (optional - logic depends on your model)
    upcoming_interviews_count = AppliedJob.objects.filter(student=user, status='accepted').count()

    context = {
        'applied_jobs_count': applied_jobs_count,
        'saved_jobs_count': saved_jobs_count,
        'upcoming_interviews_count': upcoming_interviews_count,
    }
    return render(request,'myApp/student_dashboard.html',context)

@never_cache
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='job_listings')
def job_listings(request):
    
    jobs = Job.objects.all().order_by('-posted_at')  # Fetch all jobs
    
    rejected_jobs = RejectedJob.objects.filter(student=request.user).values_list('job_id', flat=True)
    jobs = jobs.exclude(id__in=rejected_jobs)
    # Filters
    search_query = request.GET.get('search', '')
    if search_query:
        jobs = jobs.filter(title__icontains=search_query)

    #getting applied jobs id 
    applied_job_ids = AppliedJob.objects.filter(student=request.user).values_list('job_id', flat=True)

    context = {
        'jobs': jobs,
        'applied_job_ids': applied_job_ids   
    }
    return render(request, 'myApp/job_listings.html', context)


def apply_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    print("Job found:", job.title)

    existing_application = AppliedJob.objects.filter(student=request.user, job=job).first()

    if existing_application:
        if existing_application.status == 'declined':
            messages.warning(request, "You have already applied for this job and your application was declined.")
        elif existing_application.status == 'pending':
            messages.error(request, "You have already applied for this job. Please wait for a response.")
        elif existing_application.status == 'accepted':
            messages.success(request, "You have already applied and your application was accepted.")

        return redirect('job_listings')

    # First-time application
    AppliedJob.objects.create(student=request.user, job=job)
    messages.success(request, "You have successfully applied for this job!")
    return redirect('job_listings')


@never_cache
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='job_listings')
def job_details(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    applied = False
    status = None

    if request.user.is_authenticated:
        application = AppliedJob.objects.filter(student=request.user, job=job).first()
        if application:
            applied = True
            status = application.status

    return render(request, 'myApp/job_details.html', {
        'job': job,
        'applied': applied,
        'status': status
    })


@require_POST
@login_required
def reject_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    
    # Save rejected job
    RejectedJob.objects.get_or_create(student=request.user, job=job)
    
    AppliedJob.objects.filter(student=request.user, job=job).delete()

    return JsonResponse({"success": True})

    # if request.method == "POST":
    #     job_id = request.POST.get("job_id")
    #     job = get_object_or_404(Job, id=job_id)

    #     # Save rejected job
    #     RejectedJob.objects.get_or_create(student=request.user, job=job)

    #     return JsonResponse({"status": "success"})

    # return JsonResponse({"status": "error"}, status=400)


@require_POST
@login_required
@csrf_exempt
def upload_resume_and_apply(request, job_id):
    print("Resume upload view triggered")
    if request.method == 'POST' and request.FILES.get('resume'):
        resume = request.FILES['resume']
        fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'resumes'))
        filename = fs.save(resume.name, resume)
        resume_url = fs.url(filename)

        # Apply for job + attach resume
        job = get_object_or_404(Job, id=job_id)
        AppliedJob.objects.get_or_create(
            student=request.user,
            job=job,
            defaults={'resume': f'resumes/{filename}'}
        )
        messages.success(request, "You have successfully applied for this job with your resume!")
        return JsonResponse({'success': 'Resume uploaded and job application submitted successfully!'})
    
    # If we get here, no resume was uploaded
    messages.error(request, "No resume uploaded")
    return JsonResponse({'error': 'No resume uploaded'}, status=400)



@login_required
def message_recruiter(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    recruiter = job.recruiter  # Assuming there's a recruiter field in the Job model
    return render(request, 'myApp/message_recruiter.html', {'recruiter': recruiter})



@login_required(login_url='student_login')
def student_applied_jobs(request):
    user = request.user
    applications = AppliedJob.objects.filter(student=user).select_related('job').order_by('-applied_at')

    return render(request, 'myApp/student_applied_jobs.html', {
        'applications': applications
    })