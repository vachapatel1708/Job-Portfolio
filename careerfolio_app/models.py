from django.db import models
from django.contrib.auth.models import User
from django.apps import apps

# Create your models here.

class JobSeekerProfile(models.Model):

    user = models.OneToOneField(User,on_delete=models.CASCADE)

    profile_image = models.ImageField(upload_to='profiles/',blank=True,null=True)

    phone = models.CharField(max_length=15,blank=True)

    gender = models.CharField(max_length=20,blank=True)

    date_of_birth = models.DateField(blank=True,null=True)

    address = models.TextField(blank=True)

    city = models.CharField(max_length=100,blank=True)

    state = models.CharField(max_length=100,blank=True)

    education = models.CharField(max_length=200,blank=True)

    experience = models.CharField(max_length=100,blank=True)

    skills = models.TextField(blank=True)

    resume = models.FileField(upload_to='resumes/',blank=True,null=True)

    linkedin = models.URLField(blank=True)

    github = models.URLField(blank=True)

    portfolio = models.URLField(blank=True)

    about = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.username

class HRProfile(models.Model):

    user = models.OneToOneField(User,on_delete=models.CASCADE)

    profile_image = models.ImageField(upload_to='hr_profiles/',blank=True,null=True)

    phone = models.CharField(max_length=15,blank=True)

    designation = models.CharField(max_length=100,blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.username

class Company(models.Model):

    hr = models.OneToOneField(HRProfile,on_delete=models.CASCADE)

    company_name = models.CharField(max_length=200)

    description = models.TextField(blank=True)

    website = models.URLField(blank=True)

    email = models.EmailField(blank=True)

    phone = models.CharField(max_length=15,blank=True)

    industry = models.CharField(max_length=100,blank=True)

    company_size = models.CharField(max_length=100,blank=True)

    location = models.CharField(max_length=200,blank=True)

    founded_year = models.PositiveIntegerField(blank=True,null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.company_name

class JobCategory(models.Model):

    name = models.CharField(max_length=100)

    description = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Skill(models.Model):

    name = models.CharField(max_length=100,unique=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Job(models.Model):

    JOB_TYPE_CHOICES = [
        ('Full Time', 'Full Time'),
        ('Part Time', 'Part Time'),
        ('Internship', 'Internship'),
        ('Contract', 'Contract'),
        ('Freelance', 'Freelance'),
    ]

    WORK_MODE_CHOICES = [
        ('Onsite', 'Onsite'),
        ('Remote', 'Remote'),
        ('Hybrid', 'Hybrid'),
    ]

    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Closed', 'Closed'),
        ('Draft', 'Draft'),
    ]

    company = models.ForeignKey(Company,on_delete=models.CASCADE,related_name='jobs')

    category = models.ForeignKey(JobCategory,on_delete=models.SET_NULL,null=True,blank=True,related_name='jobs')

    title = models.CharField(max_length=200)

    description = models.TextField()

    requirements = models.TextField(blank=True)

    responsibilities = models.TextField(blank=True)

    skills = models.ManyToManyField(Skill,blank=True,related_name='jobs')

    job_type = models.CharField(max_length=50,choices=JOB_TYPE_CHOICES)

    experience = models.CharField(max_length=100)

    salary_min = models.DecimalField(max_digits=10,decimal_places=2,blank=True,null=True)

    salary_max = models.DecimalField(max_digits=10,decimal_places=2,blank=True,null=True)

    location = models.CharField(max_length=200)

    work_mode = models.CharField(max_length=50,choices=WORK_MODE_CHOICES)

    vacancies = models.PositiveIntegerField(default=1)

    application_deadline = models.DateField()

    status = models.CharField(max_length=20,choices=STATUS_CHOICES,default='Active')

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class SavedJob(models.Model):

    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name='saved_jobs')

    job = models.ForeignKey(Job,on_delete=models.CASCADE,related_name='saved_by')

    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'job')

    def __str__(self):
        return f"{self.user.username} - {self.job.title}"

class JobApplication(models.Model):

    STATUS_CHOICES = [
        ('Applied', 'Applied'),
        ('Under Review', 'Under Review'),
        ('Shortlisted', 'Shortlisted'),
        ('Interview', 'Interview'),
        ('Selected', 'Selected'),
        ('Rejected', 'Rejected'),
    ]

    job = models.ForeignKey(Job,on_delete=models.CASCADE,related_name='applications')

    job_seeker = models.ForeignKey(User,on_delete=models.CASCADE,related_name='job_applications')

    resume = models.FileField(upload_to='applications/resumes/',blank=True,null=True)

    cover_letter = models.TextField(blank=True)

    status = models.CharField(max_length=30,choices=STATUS_CHOICES,default='Applied')

    applied_date = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('job', 'job_seeker')

    def __str__(self):
        return f"{self.job_seeker.username} - {self.job.title}"

class Notification(models.Model):

    NOTIFICATION_TYPES = [
        ('Application', 'Application'),
        ('Job', 'Job'),
        ('System', 'System'),
    ]

    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name='notifications')

    title = models.CharField(max_length=200)

    message = models.TextField()

    notification_type = models.CharField(max_length=50,choices=NOTIFICATION_TYPES,default='System')

    is_read = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.title}"

class JobReport(models.Model):

    REPORT_STATUS = [
        ('Pending', 'Pending'),
        ('Reviewed', 'Reviewed'),
        ('Resolved', 'Resolved'),
        ('Rejected', 'Rejected'),
    ]

    job = models.ForeignKey(Job,on_delete=models.CASCADE,related_name='reports')

    reported_by = models.ForeignKey(User,on_delete=models.CASCADE,related_name='job_reports')

    reason = models.CharField(max_length=200)

    description = models.TextField(blank=True)

    status = models.CharField(max_length=20,choices=REPORT_STATUS,default='Pending')

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.job.title} - {self.reason}"