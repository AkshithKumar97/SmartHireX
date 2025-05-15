import csv
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from recruiter.models import Job
from datetime import datetime, timedelta

class Command(BaseCommand):
    help = 'Import jobs from jobs_posting.csv into the Job model'

    def handle(self, *args, **kwargs):
        file_path = 'C:\SmartHierX-Master - Copy\SmartHierX\posted_jobs1.csv'  # Place the CSV file at the same level as manage.py

        try:
            with open(file_path, mode='r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                admin_user = User.objects.filter(is_superuser=True).first()

                if not admin_user:
                    self.stdout.write(self.style.ERROR("❌ No superuser found to assign as posted_by."))
                    return

                created_count = 0
                for row in reader:
                    Job.objects.create(
                        title=row['title'],
                        company_name=row['company_name'],
                        description=row['description'],
                        location=row['location'],
                        salary=row.get('salary', 'N/A'),
                        job_type=row.get('job_type', 'Full-Time'),
                        experience=int(row.get('experience', 0)),
                        qualification=row.get('qualification', 'Not Specified'),
                        skills=row.get('skills', ''),
                        deadline=datetime.now().date() + timedelta(days=30),
                        category=row.get('category', 'General'),
                        posted_by=admin_user
                    )
                    created_count += 1

                self.stdout.write(self.style.SUCCESS(f"✅ Successfully imported {created_count} jobs."))

        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f"❌ File {file_path} not found."))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Error occurred: {e}"))
