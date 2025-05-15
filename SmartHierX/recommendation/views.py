# recommendation/views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import ResumeUploadForm
from recruiter.models import Job as PostedJob
from myApp.models import StudentResume  # ✅ Use this instead of AppliedJob
import joblib
import os
from django.conf import settings
from .utils import clean_text
from django.core.files.storage import FileSystemStorage
from .utils import extract_text_from_file
from django.contrib.auth.decorators import login_required
import traceback
from sklearn.metrics.pairwise import cosine_similarity


@login_required
def recommend_jobs(request):
    if request.method == 'POST':
        form = ResumeUploadForm(request.POST, request.FILES)
        if form.is_valid():
            resume_file = request.FILES['resume']
            StudentResume.objects.filter(student=request.user).delete()
            StudentResume.objects.create(student=request.user, resume=resume_file)
            messages.success(request, "Resume uploaded successfully!")
            return redirect('recommend_jobs')
    else:
        form = ResumeUploadForm()

    try:
        student_resume = StudentResume.objects.get(student=request.user)
        resume_path = student_resume.resume.path
        print("✅ Resume path:", resume_path)

        resume_text = extract_text_from_file(resume_path)
        cleaned_resume = clean_text(resume_text)
        print("✅ Resume (cleaned):", cleaned_resume[:300])

        tfidf = joblib.load(os.path.join(settings.BASE_DIR, 'recommendation/recommender/tfidf_vectorizer.pkl'))

        # Load jobs
        jobs = PostedJob.objects.all()
        job_texts = []
        job_map = {}

        for idx, job in enumerate(jobs):
            job_text = clean_text(f"{job.title} {job.description} {job.skills} {job.qualification} {job.category} {job.job_type}")
            job_texts.append(job_text)
            job_map[idx] = job

        # Transform both job descriptions and resume
        job_vectors = tfidf.transform(job_texts)
        resume_vector = tfidf.transform([cleaned_resume])

        print(f"✅ Resume vector sum: {resume_vector.sum()}")  # Debug
        similarities = cosine_similarity(resume_vector, job_vectors).flatten()

        print(f"✅ Similarities: {similarities}")  # Debug

        recommended_jobs = []
        for idx, score in enumerate(similarities):
            match_score = round(similarities[idx] * 100, 2)
            if match_score >= 25:
                recommended_jobs.append({
                    'job': job_map[idx],
                    'score': match_score
                })

        recommended_jobs = sorted(recommended_jobs, key=lambda x: x['score'], reverse=True)[:10]

        return render(request, 'recommendation/recommended_jobs.html', {
            'recommended_jobs': recommended_jobs,
            'resume_file': student_resume.resume.name
        })

    except StudentResume.DoesNotExist:
        return render(request, 'recommendation/upload_resume.html', {'form': form})
    except Exception as e:
        print("❌ Exception occurred in recommend_jobs view:")
        traceback.print_exc()
        messages.error(request, f"Something went wrong: {str(e)}")
        return render(request, 'recommendation/upload_resume.html', {'form': form})











# def recommend_jobs(request):
#     if not request.user.is_authenticated:
#         messages.error(request, "Please log in to access recommendations.")
#         return redirect('student_login')

#     # Upload Resume Logic
#     if request.method == 'POST':
#         form = ResumeUploadForm(request.POST, request.FILES)
#         if form.is_valid():
#             resume_file = request.FILES['resume']
#             StudentResume.objects.filter(student=request.user).delete()
#             StudentResume.objects.create(student=request.user, resume=resume_file)

#             messages.success(request, "Resume uploaded successfully!")
#             return redirect('recommend_jobs')
#     else:
#         form = ResumeUploadForm()

#     try:
#         student_resume = StudentResume.objects.get(student=request.user)
#         resume_path = student_resume.resume.path
#         print("✅ Resume path:", resume_path)

#         resume_text = extract_text_from_file(resume_path)
#         print("✅ Extracted resume text (first 300):", resume_text[:300])

#         cleaned_resume = clean_text(resume_text)
#         print("✅ Cleaned resume text (first 300):", cleaned_resume[:300])

#         tfidf = joblib.load(os.path.join(settings.BASE_DIR, 'recommendation/recommender/tfidf_vectorizer.pkl'))

#         resume_vector = tfidf.transform([cleaned_resume])
#         print(f"✅ Resume vector shape: {resume_vector}")
#         model = joblib.load(os.path.join(settings.BASE_DIR, 'recommendation/recommender/job_recommendation_model.pkl'))
#         print(model.predict_proba(resume_vector)[0][1])
#         jobs = PostedJob.objects.all()
#         job_texts = []
#         job_map = {}
#         print(f"resume_vector sum : {resume_vector.sum()}")
#         for idx, job in enumerate(jobs):
#             job_text = clean_text(f"{job.title} {job.description} {job.skills} {job.qualification}")
#             job_texts.append(job_text)
#             job_map[idx] = job

#         job_vectors = tfidf.transform(job_texts)
#         similarities = cosine_similarity(resume_vector, job_vectors).flatten()  # put [0] here cahange recently shape: (num_jobs,)

#         recommended_jobs = []
#         for idx, score in enumerate(similarities):
#             match_score = round(score * 100)
#             if match_score >= 25:  # You can tweak this threshold
#                 recommended_jobs.append({
#                     'job': job_map[idx],
#                     'score': match_score
#                 })

#         recommended_jobs = sorted(recommended_jobs, key=lambda x: x['score'], reverse=True)[:10]

#         return render(request, 'recommendation/recommended_jobs.html', {
#             'recommended_jobs': recommended_jobs,
#             'resume_file': student_resume.resume.name
#         })

#     except StudentResume.DoesNotExist:
#         return render(request, 'recommendation/upload_resume.html', {'form': ResumeUploadForm()})
#     except Exception as e:
#         print("Exception occurred in recommend_jobs view:")
#         traceback.print_exc()
#         messages.error(request, f"Something went wrong: {str(e)}")
#         return render(request, 'recommendation/upload_resume.html', {'form': ResumeUploadForm()})















# def recommend_jobs(request):
#     if not request.user.is_authenticated:
#         messages.error(request, "Please log in to access recommendations.")
#         return redirect('student_login')

#     # Upload Resume Logic
#     if request.method == 'POST':
#         form = ResumeUploadForm(request.POST, request.FILES)
#         if form.is_valid():
#             resume_file = request.FILES['resume']
#             # StudentResume.objects.update_or_create(
#             #     student=request.user,
#             #     defaults={'resume': resume_file}
#             # )
#             # Delete existing resume to ensure clean upload
#             StudentResume.objects.filter(student=request.user).delete()
#             StudentResume.objects.create(student=request.user, resume=resume_file)

#             messages.success(request, "Resume uploaded successfully!")
#             return redirect('recommend_jobs')
#     else:
#         form = ResumeUploadForm()

#     # Recommendation Logic
#     i = 0
#     try:
#         student_resume = StudentResume.objects.get(student=request.user)
#         resume_path = student_resume.resume.path
#         print("✅ Resume path:", resume_path)
#         resume_text = extract_text_from_file(resume_path)
#         print("✅ Extracted resume text (first 300):", resume_text[:300])
#         cleaned_resume = clean_text(resume_text)
#         print("✅ Cleaned resume text (first 300):", cleaned_resume[:300])
#         model = joblib.load(os.path.join(settings.BASE_DIR, 'recommendation/recommender/job_recommendation_model.pkl'))
#         tfidf = joblib.load(os.path.join(settings.BASE_DIR, 'recommendation/recommender/tfidf_vectorizer.pkl'))

#         jobs = PostedJob.objects.all()
#         recommended_jobs = []
#         for job in jobs:
#             job_text = clean_text(f"{job.skills} {job.qualification} {job.description}")
#             # print(f"\n Job {job.id} -> {job.title} | {job.skills} | {job.qualification} {i}")
#             i += 1
#             combined = [cleaned_resume + " " + job_text]
#             vector = tfidf.transform(combined)
#             score = model.predict_proba(vector)[0][1] * 100
#             # print(f"Score: {score}")  # Debugging line
#             if score >= 25:
#                 recommended_jobs.append({
#                     'job': job,
#                     'score': round(score, 2)
#                 })

#         recommended_jobs = sorted(recommended_jobs, key=lambda x: x['score'], reverse=True)[:10]

#         return render(request, 'recommendation/recommended_jobs.html', {
#             'recommended_jobs': recommended_jobs,
#             'resume_file': student_resume.resume.name
#         })

#     except StudentResume.DoesNotExist:
#         return render(request, 'recommendation/upload_resume.html', {'form': ResumeUploadForm()})
#     except Exception as e:
#         print("Exception occurred in recommend_jobs view:")
#         traceback.print_exc()
#         messages.error(request, f"Something went wrong: {str(e)}")
#         return render(request, 'recommendation/upload_resume.html', {'form': ResumeUploadForm()})






@login_required
def clear_resume_and_redirect(request):
    StudentResume.objects.filter(student=request.user).delete()
    return redirect('student_dashboard')  # change this to your actual dashboard URL name

def test(request):
    return render(request, 'recommendation/test.html')
