from django.db import models
from django.contrib.auth.models import User
from recruiter.models import Job
from django.dispatch import receiver
# Create your models here.

class AppliedJob(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
        ('rejected','Rejected'),
    ]
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    job = models.ForeignKey(Job, on_delete=models.CASCADE,related_name='applications')
    resume = models.FileField(upload_to='resumes/', blank=True, null=True)
    applied_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[('Accepted', 'Accepted'), ('Declined', 'Declined')], blank=True, null=True,default='pending')

    class Meta:
        unique_together = ('student', 'job')


class RejectedJob(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    rejected_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'job')


class StudentResume(models.Model):
    student = models.OneToOneField(User, on_delete=models.CASCADE)
    resume = models.FileField(upload_to='resumes/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.student.username