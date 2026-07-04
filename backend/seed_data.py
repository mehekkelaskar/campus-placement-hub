"""Seed script to create an admin user and sample data."""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.users.models import User
from apps.companies.models import Company, PlacementDrive
from datetime import timedelta
from django.utils import timezone

# Create admin user
if not User.objects.filter(email='admin@plc.com').exists():
    admin = User.objects.create_superuser(
        username='admin',
        email='admin@plc.com',
        password='admin123',
        first_name='Admin',
        last_name='User',
        role='admin',
        is_verified=True
    )
    print(f"Admin created: {admin.email}")
else:
    print("Admin already exists")

# Create student user
if not User.objects.filter(email='student@plc.com').exists():
    student = User.objects.create_user(
        username='student',
        email='student@plc.com',
        password='student123',
        first_name='John',
        last_name='Doe',
        role='student',
        branch='CSE',
        year=4,
        phone='1234567890',
        is_verified=True
    )
    print(f"Student created: {student.email}")
else:
    print("Student already exists")

# Sample companies
sample_companies = [
    {
        'name': 'Google',
        'about': 'Google LLC is an American multinational technology company focusing on AI, online advertising, search engine technology, cloud computing, and more.',
        'official_message': 'Google is visiting our campus for SDE roles. Prepare well!',
        'hiring_role': 'Software Development Engineer',
        'eligibility': 'B.Tech CSE/IT, CGPA >= 7.0, No active backlogs',
        'apply_link': 'https://careers.google.com',
        'website': 'https://google.com',
        'recruitment_process': '1. Online Assessment\n2. Technical Interview Round 1\n3. Technical Interview Round 2\n4. HR Interview',
    },
    {
        'name': 'Microsoft',
        'about': 'Microsoft Corporation is an American multinational technology corporation producing software, consumer electronics, and personal computers.',
        'official_message': 'Microsoft is hiring fresh graduates for their Hyderabad office.',
        'hiring_role': 'Software Engineer',
        'eligibility': 'B.Tech All Branches, CGPA >= 6.5',
        'apply_link': 'https://careers.microsoft.com',
        'website': 'https://microsoft.com',
        'recruitment_process': '1. Online Coding Test\n2. Technical Interview\n3. Hiring Manager Interview',
    },
    {
        'name': 'Amazon',
        'about': 'Amazon.com is an American multinational technology company focusing on e-commerce, cloud computing, digital streaming, and AI.',
        'official_message': 'Amazon SDE-1 campus drive coming soon. Stay tuned!',
        'hiring_role': 'SDE-1',
        'eligibility': 'B.Tech CSE/IT/ECE, CGPA >= 7.5',
        'apply_link': 'https://amazon.jobs',
        'website': 'https://amazon.in',
        'recruitment_process': '1. Online Assessment (OA)\n2. Technical Phone Screen\n3. Loop Interviews (4 rounds)\n4. Bar Raiser',
    },
    {
        'name': 'TCS',
        'about': 'Tata Consultancy Services is an Indian multinational IT services and consulting company headquartered in Mumbai.',
        'official_message': 'TCS Digital hiring for 2026 batch.',
        'hiring_role': 'Digital Software Engineer',
        'eligibility': 'B.Tech All Branches, CGPA >= 6.0, No active backlogs',
        'apply_link': 'https://tcs.com/careers',
        'website': 'https://tcs.com',
        'recruitment_process': '1. NQT (National Qualifier Test)\n2. Technical Interview\n3. HR Interview',
    },
    {
        'name': 'Infosys',
        'about': 'Infosys Limited is an Indian multinational IT company that provides business consulting, IT services, and outsourcing.',
        'official_message': 'Infosys is conducting campus placement for multiple roles.',
        'hiring_role': 'Systems Engineer',
        'eligibility': 'B.Tech All Branches, CGPA >= 6.0',
        'apply_link': 'https://infosys.com/careers',
        'website': 'https://infosys.com',
        'recruitment_process': '1. Online Aptitude Test\n2. Technical Interview\n3. HR Interview',
    },
    {
        'name': 'Flipkart',
        'about': 'Flipkart is an Indian e-commerce company headquartered in Bangalore, offering products across various categories.',
        'official_message': 'Flipkart GRiD challenge is live. Top performers get direct interview.',
        'hiring_role': 'Software Development Engineer - 1',
        'eligibility': 'B.Tech CSE/IT, CGPA >= 7.5',
        'apply_link': 'https://flipkartcareers.com',
        'website': 'https://flipkart.com',
        'recruitment_process': '1. Online Coding Round\n2. Machine Coding Round\n3. System Design (Optional for freshers)\n4. Hiring Manager Round',
    },
    {
        'name': 'Deloitte',
        'about': 'Deloitte is a multinational professional services network providing audit, consulting, and advisory services.',
        'official_message': 'Deloitte USI is hiring analysts for the technology team.',
        'hiring_role': 'Analyst - Technology',
        'eligibility': 'B.Tech All Branches, CGPA >= 6.5',
        'apply_link': 'https://deloitte.com/careers',
        'website': 'https://deloitte.com',
        'recruitment_process': '1. Online Assessment\n2. Group Discussion\n3. Technical Interview\n4. HR Interview',
    },
    {
        'name': 'Wipro',
        'about': 'Wipro Limited is an Indian multinational corporation providing IT services and consulting.',
        'official_message': 'Wipro Elite NLTH drive for 2026 batch.',
        'hiring_role': 'Project Engineer',
        'eligibility': 'B.Tech All Branches, CGPA >= 6.0, No standing arrears',
        'apply_link': 'https://wipro.com/careers',
        'website': 'https://wipro.com',
        'recruitment_process': '1. Online Test (Aptitude + Technical)\n2. Essay Writing\n3. Technical Interview\n4. HR Interview',
    },
]

now = timezone.now()
for i, data in enumerate(sample_companies):
    company, created = Company.objects.get_or_create(
        name=data['name'],
        defaults={
            **data,
            'deadline': now + timedelta(days=7 + i * 3),
            'is_published': True,
        }
    )
    if created:
        # Create a placement drive for each company
        PlacementDrive.objects.create(
            company=company,
            drive_date=(now + timedelta(days=10 + i * 5)).date(),
            test_date=(now + timedelta(days=7 + i * 5)).date(),
            interview_date=(now + timedelta(days=12 + i * 5)).date(),
            status='upcoming' if i < 5 else 'closed',
        )
        print(f"Created company: {company.name}")

print("\nSeed complete!")
