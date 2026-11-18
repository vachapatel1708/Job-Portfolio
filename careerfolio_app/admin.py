from django.contrib import admin
from .models import JobSeekerProfile,HRProfile,Company,JobCategory,Skill,Job,SavedJob,JobApplication,Notification,JobReport


admin.site.register(JobSeekerProfile)
admin.site.register(HRProfile)
admin.site.register(Company)
admin.site.register(JobCategory)
admin.site.register(Skill)
admin.site.register(Job)
admin.site.register(SavedJob)
admin.site.register(JobApplication)
admin.site.register(Notification)
admin.site.register(JobReport)
