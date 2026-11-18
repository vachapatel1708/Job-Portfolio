from django.urls import path
from.import views

urlpatterns = [

    # COMMON
    path('',views.home),
    path('about/',views.about,name="about"),
    path('contact/',views.contact),
    path("login/", views.login , name="login"),
    path("logout/", views.logout , name="logout"),
    path("register/",views.register,name="register"),

    # JOBSEEKER
    path('jobseeker_dashboard/',views.jobseeker_dashboard,name="jobseeker_dashboard"),
    path('profile/',views.profile , name='profile'),
    path('edit_profile/',views.edit_profile , name='edit_profile'),
    path('resume/', views.resume, name='resume'),
    path('upload_resume/', views.upload_resume, name='upload_resume'),
    path('jobs/', views.jobs , name="jobs"),
    path('job_detail/<int:id>/', views.job_detail, name="job_detail"),
    path('apply_job/<int:id>/', views.apply_job, name='apply_job'),
    path('applications/', views.applications, name='applications'),
    path('application_detail/<int:id>/', views.application_detail , name='application_detail'),
    path('saved_jobs/', views.saved_jobs, name='saved_jobs'),
    path('remove_saved_job/<int:id>/', views.remove_saved_job, name='remove_saved_job'),
    path('save_job/<int:id>/', views.save_job, name='save_job'),
    path('notifications/',views.jobseeker_notifications,name='jobseeker_notifications'),
    path('notification/read/<int:id>/',views.mark_notification_read,name='mark_notification_read'),
    path('notifications/read-all/',views.mark_all_notifications_read,name='mark_all_notifications_read'),


    # HR
    path("hr/dashboard/",views.hr_dashboard,name="hr_dashboard"),
    path("hr/profile/", views.hr_profile, name="hr_profile"), 
    path("hr/company_profile/", views.hr_company_profile, name="company_profile"), 
    path("hr/edit_company/", views.hr_edit_company, name="edit_company"), 
    path("hr/post_job/", views.hr_post_job, name="post_job"), 
    path("hr/manage_jobs/", views.hr_manage_jobs, name="manage_jobs"),
    path("hr/edit_job/<int:job_id>/", views.hr_edit_job, name="edit_job"),
    path("hr/job_detail/<int:job_id>/", views.hr_job_detail, name="hr_job_detail"),
    path("hr/applications/",views.hr_applications,name="hr_applications"),
    path("hr/application_detail/<int:application_id>/",views.hr_application_detail,name="hr_application_detail"),
    path("hr/shortlisted/", views.hr_shortlisted, name="shortlisted"), 
    path("hr/selected/", views.hr_selected, name="selected"), 
    path("hr/rejected/", views.hr_rejected, name="rejected"), 
    path("hr/notifications/", views.hr_notifications, name="hr_notifications"),
]
