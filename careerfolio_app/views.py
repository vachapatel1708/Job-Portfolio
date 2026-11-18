from django.shortcuts import render, redirect , get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import login as auth_login, authenticate, logout
from django.contrib.auth import logout as django_logout
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.core.paginator import Paginator
from django.contrib import messages
from django.db.models import Count

from .models import JobSeekerProfile,HRProfile,Company,JobCategory,Skill,Job,SavedJob,JobApplication,Notification,JobReport

# ------------------------------------------------ FRONTEND -------------------------------------------------- #

# COMMON

def home(request):
    jobs = Job.objects.all().order_by('-id')[:3]

    active_jobs = Job.objects.filter(status='Active').count()
    companies = Company.objects.count()
    job_seekers = JobSeekerProfile.objects.count()
    successful_hires = JobApplication.objects.filter(status='Selected').count()

    categories = JobCategory.objects.all().order_by('-id')[:4]

    context = {
        'jobs': jobs,
        'active_jobs': active_jobs,
        'companies': companies,
        'job_seekers': job_seekers,
        'successful_hires': successful_hires,
        'categories': categories,
    }

    return render(request, 'frontend/common/home.html', context)

def about(request):

    active_jobs = Job.objects.filter(status="Active").count()
    companies = Company.objects.count()
    job_seekers = JobSeekerProfile.objects.count()
    successful_hires = JobApplication.objects.filter(status="Selected").count()

    context = {
        "active_jobs": active_jobs,
        "companies": companies,
        "job_seekers": job_seekers,
        "successful_hires": successful_hires,
    }

    return render(request, "frontend/common/about.html", context)

def contact(request):
    return render(request,'frontend/common/contact.html')

def login(request):

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request,username=username,password=password)

        if user is not None:

            auth_login(request, user)

            next_url = request.POST.get("next") or request.GET.get("next")

            if next_url:
                return redirect(next_url)

            if JobSeekerProfile.objects.filter(user=user).exists():
                return redirect("jobseeker_dashboard")

            elif HRProfile.objects.filter(user=user).exists():
                return redirect("hr_dashboard")

        else:

            return render(request,"frontend/common/login.html",{"error": "Invalid username or password."})

    return render(request,"frontend/common/login.html")

def logout(request):
    django_logout(request)
    return redirect('/')

def register(request):

    if request.method == "POST":

        full_name = request.POST.get("full_name")
        username = request.POST.get("username")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        role = request.POST.get("role")
        password = request.POST.get("password")

        # Get next URL
        next_url = request.POST.get("next")

        # Check username already exists
        if User.objects.filter(username=username).exists():

            return render(
                request,
                "frontend/common/register.html",
                {
                    "error": "Username already taken.",
                    "next": next_url
                }
            )

        # Check email already exists
        if User.objects.filter(email=email).exists():

            return render(
                request,
                "frontend/common/register.html",
                {
                    "error": "Email already registered.",
                    "next": next_url
                }
            )

        # Create User
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=full_name
        )

        # Create Job Seeker Profile
        if role == "jobseeker":

            JobSeekerProfile.objects.create(user=user,phone=phone)

        # Create HR Profile
        elif role == "hr":

            HRProfile.objects.create(user=user,phone=phone)

        # Automatically login
        auth_login(request, user)

        # If user came from Apply / Jobs page
        if next_url:
            return redirect(next_url)

        # Normal registration
        if role == "jobseeker":
            return redirect("jobseeker_dashboard")

        elif role == "hr":
            return redirect("hr_dashboard")

    return render(request,"frontend/common/register.html")



# JOBSEEKER

@login_required(login_url="login")
def jobseeker_dashboard(request):

    user = request.user

    # Applied Jobs
    applied_jobs_count = JobApplication.objects.filter(job_seeker=user).count()

    # Saved Jobs
    saved_jobs_count = SavedJob.objects.filter(user=user).count()

    # Interviews
    interview_count = JobApplication.objects.filter(job_seeker=user,status='Interview').count()

    # Recent Applications
    recent_applications = JobApplication.objects.filter(job_seeker=user).select_related('job', 'job__company').order_by('-applied_date')[:5]

    # Latest Active Jobs
    latest_jobs = Job.objects.filter(status='Active').select_related('company','category').order_by('-created_at')[:6]

    context = {
        'applied_jobs_count': applied_jobs_count,
        'saved_jobs_count': saved_jobs_count,
        'interview_count': interview_count,
        'profile_views': 0,
        'recent_applications': recent_applications,
        'latest_jobs': latest_jobs,
    }

    return render(request,'frontend/jobseeker/jobseeker_dashboard.html',context)


@login_required
def profile(request):

    profile_data = JobSeekerProfile.objects.get(user=request.user)

    # Jobs Applied
    applied_jobs_count = JobApplication.objects.filter(job_seeker=request.user).count()

    # Saved Jobs
    saved_jobs_count = SavedJob.objects.filter(user=request.user).count()

    # Resume Uploaded
    resume_uploaded = 1 if profile_data.resume else 0

    context = {
        'profile': profile_data,
        'applied_jobs_count': applied_jobs_count,
        'saved_jobs_count': saved_jobs_count,
        'resume_uploaded': resume_uploaded,
    }

    return render(request,'frontend/jobseeker/profile.html',context)


@login_required(login_url="login")
def edit_profile(request):

    profile, created = JobSeekerProfile.objects.get_or_create(
        user=request.user
    )

    if request.method == "POST":

        # User information
        request.user.first_name = request.POST.get("first_name", "")
        request.user.last_name = request.POST.get("last_name", "")
        request.user.email = request.POST.get("email", "")

        request.user.save()

        # Profile information
        profile.phone = request.POST.get("phone", "")

        location = request.POST.get("location", "")

        if "," in location:
            city, state = location.split(",", 1)
            profile.city = city.strip()
            profile.state = state.strip()
        else:
            profile.city = location.strip()
            profile.state = ""

        profile.date_of_birth = request.POST.get("date_of_birth") or None

        profile.experience = request.POST.get("experience_level", "")

        profile.about = request.POST.get("summary", "")

        profile.skills = request.POST.get("skills", "")

        degree = request.POST.get("degree", "")
        field_of_study = request.POST.get("field_of_study", "")

        profile.education = f"{degree} - {field_of_study}"

        # Profile image
        if request.FILES.get("profile_image"):
            profile.profile_image = request.FILES.get("profile_image")

        profile.save()

        return redirect("profile")

    return render(request,"frontend/jobseeker/edit_profile.html",{"profile": profile})



@login_required(login_url="login")
def resume(request):

    profile = JobSeekerProfile.objects.get(user=request.user)

    completed = 0
    total = 5

    if request.user.first_name and request.user.last_name:
        completed += 1

    if profile.phone:
        completed += 1

    if profile.skills:
        completed += 1

    if profile.education:
        completed += 1

    if profile.resume:
        completed += 1

    profile_percentage = int((completed / total) * 100)

    return render(request,"frontend/jobseeker/resume.html",{"profile": profile,"profile_percentage": profile_percentage})



@login_required(login_url="login")
def upload_resume(request):

    profile, created = JobSeekerProfile.objects.get_or_create( user=request.user )

    if request.method == "POST":

        resume_file = request.FILES.get("resume")

        if resume_file:
            profile.resume = resume_file
            profile.save()

            return redirect("resume")

    return render(request,"frontend/jobseeker/upload_resume.html", {"profile": profile} )



def jobs(request):

    # Get category first so we can preserve it for login/register
    category = request.GET.get("category", "").strip()

    # If user is not logged in
    if not request.user.is_authenticated:

        next_url = "/jobs/"

        if category:
            next_url += f"?category={category}"

        return redirect(f"/register/?next={next_url}")

    # Active jobs
    jobs = Job.objects.filter(status="Active")

    # Search
    search = request.GET.get("search", "").strip()

    if search:
        jobs = jobs.filter(
            Q(title__icontains=search) |
            Q(description__icontains=search) |
            Q(requirements__icontains=search) |
            Q(responsibilities__icontains=search) |
            Q(company__company_name__icontains=search) |
            Q(skills__name__icontains=search)
        ).distinct()

    # Location filter
    location = request.GET.get("location", "").strip()

    if location:
        jobs = jobs.filter(location__iexact=location)

    # Job Type filter
    job_type = request.GET.get("job_type", "").strip()

    if job_type:
        jobs = jobs.filter(job_type=job_type)

    # Category filter
    if category:
        jobs = jobs.filter(category_id=category)

    # Sort
    sort = request.GET.get("sort", "latest")

    if sort == "salary":
        jobs = jobs.order_by("-salary_max", "-created_at")

    elif sort == "relevance":
        jobs = jobs.order_by("-created_at")

    else:
        jobs = jobs.order_by("-created_at")

    # Locations for dropdown
    locations = (
        Job.objects
        .filter(status="Active")
        .exclude(location="")
        .values_list("location", flat=True)
        .distinct()
        .order_by("location")
    )

    # ALL JOB CATEGORIES
    categories = (
        JobCategory.objects
        .annotate(
            job_count=Count(
                "jobs",
                filter=Q(jobs__status="Active")
            )
        )
        .order_by("name")
    )

    context = {
        "jobs": jobs,
        "locations": locations,
        "categories": categories,
        "search": search,
        "selected_location": location,
        "selected_job_type": job_type,
        "selected_category": category,
        "selected_sort": sort,
    }

    return render(
        request,
        "frontend/jobseeker/jobs.html",
        context
    )


@login_required(login_url="login")
def job_detail(request, id):

    job = get_object_or_404(Job, id=id)

    is_saved = SavedJob.objects.filter(user=request.user,job=job).exists()

    return render(request,'frontend/jobseeker/job_detail.html',{'job': job,'is_saved': is_saved,})


def apply_job(request, id):

    # Login required
    if not request.user.is_authenticated:

        next_url = f"/apply_job/{id}/"

        return redirect(
            f"/login/?next={next_url}"
        )

    # Get selected job
    job = get_object_or_404(Job, id=id)

    # Get candidate profile
    profile = JobSeekerProfile.objects.filter(
        user=request.user
    ).first()

    # Submit application
    if request.method == "POST":

        # Resume required
        if not profile or not profile.resume:

            return render(
                request,
                "frontend/jobseeker/apply_job.html",
                {
                    "job": job,
                    "profile": profile,
                    "error": "Please upload your resume before applying."
                }
            )

        cover_letter = request.POST.get("cover_letter", "").strip()

        # Check duplicate application
        already_applied = JobApplication.objects.filter(
            job=job,
            job_seeker=request.user
        ).exists()

        if already_applied:
            return redirect("applications")

        # Create application
        application = JobApplication.objects.create(
            job=job,
            job_seeker=request.user,
            resume=profile.resume,
            cover_letter=cover_letter,
            status="Applied"
        )

        # Notification
        Notification.objects.create(
            user=request.user,
            title="Application Submitted",
            message=f"Your application for {job.title} has been submitted successfully.",
            notification_type="Application"
        )

        return redirect("applications")

    # Open apply page
    return render(
        request,
        "frontend/jobseeker/apply_job.html",
        {
            "job": job,
            "profile": profile
        }
    )



@login_required(login_url="login")
def applications(request):

    applications = JobApplication.objects.filter(job_seeker=request.user).select_related('job','job__company').order_by('-applied_date')

    total_applications = applications.count()

    under_review = applications.filter(status='Under Review').count()

    shortlisted = applications.filter(status='Shortlisted').count()

    selected = applications.filter(status='Selected').count()

    context = {
        'applications': applications,
        'total_applications': total_applications,
        'under_review': under_review,
        'shortlisted': shortlisted,
        'selected': selected,
    }

    return render(request,'frontend/jobseeker/applications.html',context)



@login_required(login_url="login")
def application_detail(request, id):

    application = get_object_or_404(JobApplication.objects.select_related('job','job__company','job_seeker'),
    id=id,job_seeker=request.user)

    profile = JobSeekerProfile.objects.filter(user=request.user).first()

    return render(request,'frontend/jobseeker/application_detail.html',{'application': application,'profile': profile,})



@login_required(login_url="login")
def saved_jobs(request):

    saved_jobs = SavedJob.objects.filter(user=request.user).select_related('job','job__company').prefetch_related('job__skills').order_by('-saved_at')

    context = {'saved_jobs': saved_jobs,'saved_count': saved_jobs.count()}

    return render(request,'frontend/jobseeker/saved_jobs.html',context)



@login_required(login_url="login")
def remove_saved_job(request, id):

    saved_job = get_object_or_404(SavedJob,user=request.user,job_id=id)

    saved_job.delete()

    return redirect('saved_jobs')


@login_required(login_url="login")
def save_job(request, id):

    job = get_object_or_404(Job, id=id)

    SavedJob.objects.get_or_create(user=request.user,job=job)

    return redirect('job_detail', id=id)


@login_required(login_url="login")
def jobseeker_notifications(request):

    notifications = Notification.objects.filter(user=request.user).order_by("-created_at")

    return render(request,"frontend/jobseeker/notifications.html",{"notifications": notifications})


@login_required(login_url="login")
def mark_notification_read(request, id):

    notification = get_object_or_404(Notification,id=id,user=request.user)

    notification.is_read = True
    notification.save()

    return redirect("jobseeker_notifications")


@login_required(login_url="login")
def mark_all_notifications_read(request):

    Notification.objects.filter(user=request.user,is_read=False).update(is_read=True)

    return redirect("jobseeker_notifications")


# HR

@login_required(login_url="login")
def hr_dashboard(request):

    # Logged-in HR profile
    hr_profile = get_object_or_404(HRProfile, user=request.user)

    # HR ki company
    company = Company.objects.filter(hr=hr_profile).first()

    # Default values
    active_jobs = 0
    total_applications = 0
    shortlisted_count = 0
    selected_count = 0
    recent_applications = []

    if company:

        # HR ki company ke jobs
        jobs = Job.objects.filter(company=company)

        # Active jobs
        active_jobs = jobs.filter(status="Active").count()

        # Company ke jobs par applications
        applications = JobApplication.objects.filter(job__company=company
        ).select_related(
            "job",
            "job_seeker",
            "job_seeker__jobseekerprofile"
        )

        # Total applications
        total_applications = applications.count()

        # Shortlisted
        shortlisted_count = applications.filter(status="Shortlisted").count()

        # Selected
        selected_count = applications.filter(status="Selected").count()

        # Latest 5 applications
        recent_applications = applications.order_by("-applied_date")[:5]

    # HR notifications
    notifications = Notification.objects.filter(user=request.user).order_by("-created_at")

    unread_notifications_count = notifications.filter(is_read=False).count()

    context = {
        "hr_profile": hr_profile,
        "company": company,
        "active_jobs": active_jobs,
        "total_applications": total_applications,
        "shortlisted_count": shortlisted_count,
        "selected_count": selected_count,
        "recent_applications": recent_applications,

        # Notifications
        "notifications": notifications[:5],
        "unread_notifications_count": unread_notifications_count,
    }

    return render(request,"frontend/hr/hr_dashboard.html",context)



@login_required(login_url="login")
def hr_profile(request):

    hr_profile = get_object_or_404(HRProfile,user=request.user)

    company = Company.objects.filter(hr=hr_profile).first()

    # HR company ke jobs
    jobs = Job.objects.filter(company=company) if company else Job.objects.none()

    # HR company ki applications
    applications = JobApplication.objects.filter(job__company=company) if company else JobApplication.objects.none()

    context = {
        "profile": hr_profile,
        "company": company,
        "jobs_count": jobs.count(),
        "applications_count": applications.count(),
        "shortlisted_count": applications.filter(
            status="Shortlisted"
        ).count(),
    }

    return render(request,"frontend/hr/profile.html",context)



@login_required(login_url="login")
def hr_company_profile(request):

    hr_profile = get_object_or_404(HRProfile,user=request.user)

    company = get_object_or_404(Company,hr=hr_profile)

    jobs = Job.objects.filter(company=company)

    applications = JobApplication.objects.filter(job__company=company)

    context = {
        "company": company,

        "active_jobs": jobs.filter(
            status="Active"
        ).count(),

        "total_applications": applications.count(),

        "employees_count": company.company_size,
    }

    return render(request,"frontend/hr/company_profile.html",context)



@login_required(login_url="login")
def hr_edit_company(request):

    hr_profile = get_object_or_404(HRProfile,user=request.user)

    company = get_object_or_404(Company,hr=hr_profile)

    if request.method == "POST":

        company.company_name = request.POST.get("company_name")

        company.industry = request.POST.get("industry")

        company.company_size = request.POST.get("company_size")

        company.founded_year = request.POST.get("founded_year") or None

        company.description = request.POST.get("description")

        company.email = request.POST.get("email")

        company.phone = request.POST.get("phone")

        company.website = request.POST.get("website")

        company.location = request.POST.get("location")

        company.save()

        return redirect("company_profile")

    context = {"company": company}

    return render(request,"frontend/hr/edit_company.html",context)



@login_required(login_url="login")
def hr_post_job(request):

    hr_profile = get_object_or_404(HRProfile,user=request.user)

    company = get_object_or_404(Company,hr=hr_profile)

    categories = JobCategory.objects.all()

    if request.method == "POST":

        title = request.POST.get("title")
        category_id = request.POST.get("category")
        job_type = request.POST.get("job_type")
        experience = request.POST.get("experience")
        vacancies = request.POST.get("vacancies")

        description = request.POST.get("description")
        requirements = request.POST.get("requirements")
        responsibilities = request.POST.get("responsibilities")

        skills_input = request.POST.get("skills")

        salary_min = request.POST.get("salary_min") or None
        salary_max = request.POST.get("salary_max") or None

        city = request.POST.get("city")
        state = request.POST.get("state")

        location = f"{city}, {state}"

        work_mode = request.POST.get("work_mode")

        application_deadline = request.POST.get("application_deadline")

        category = get_object_or_404(JobCategory,id=category_id)

        job = Job.objects.create(
            company=company,
            category=category,
            title=title,
            description=description,
            requirements=requirements,
            responsibilities=responsibilities,
            job_type=job_type,
            experience=experience,
            salary_min=salary_min,
            salary_max=salary_max,
            location=location,
            work_mode=work_mode,
            vacancies=vacancies,
            application_deadline=application_deadline,
            status="Active"
        )

        # Skills create/select
        if skills_input:

            skills_list = skills_input.split(",")

            for skill_name in skills_list:

                skill_name = skill_name.strip()

                if skill_name:

                    skill, created = Skill.objects.get_or_create(
                        name__iexact=skill_name,
                        defaults={"name": skill_name}
                    )

                    job.skills.add(skill)

        return redirect("manage_jobs")

    context = {"categories": categories}

    return render(request,"frontend/hr/post_job.html",context)



@login_required(login_url="login")
def hr_manage_jobs(request):

    hr_profile = get_object_or_404(HRProfile, user=request.user)

    company = get_object_or_404(Company, hr=hr_profile)

    # All jobs of this HR's company
    jobs = Job.objects.filter(company=company).prefetch_related("skills")

    # Search only by job title
    search = request.GET.get("search", "").strip()

    if search:
        jobs = jobs.filter(title__icontains=search)

    # Latest jobs first
    jobs = jobs.order_by("-created_at")

    total_jobs = jobs.count()

    active_jobs = jobs.filter(status="Active").count()

    closed_jobs = jobs.filter(status="Closed").count()

    draft_jobs = jobs.filter(status="Draft").count()

    context = {
        "jobs": jobs,
        "total_jobs": total_jobs,
        "active_jobs": active_jobs,
        "closed_jobs": closed_jobs,
        "draft_jobs": draft_jobs,
        "search": search,
    }

    return render(request,"frontend/hr/manage_jobs.html",context)




@login_required(login_url="login")
def hr_edit_job(request, job_id):

    hr_profile = get_object_or_404(HRProfile, user=request.user)
    company = get_object_or_404(Company, hr=hr_profile)

    job = get_object_or_404(Job,id=job_id,company=company)

    categories = JobCategory.objects.all()
    skills = Skill.objects.all()

    if request.method == "POST":

        # Basic Information
        job.title = request.POST.get("title")

        # Category
        category_id = request.POST.get("category")

        if category_id:
            job.category = get_object_or_404(JobCategory,id=category_id)
        else:
            job.category = None

        # Job Details
        job.job_type = request.POST.get("job_type")
        job.experience = request.POST.get("experience")
        job.vacancies = request.POST.get("vacancies") or 1

        # Description
        job.description = request.POST.get("description")
        job.requirements = request.POST.get("requirements")
        job.responsibilities = request.POST.get("responsibilities")

        # Salary
        job.salary_min = request.POST.get("salary_min") or None
        job.salary_max = request.POST.get("salary_max") or None

        # Location
        job.location = request.POST.get("location")
        job.work_mode = request.POST.get("work_mode")

        # Deadline & Status
        job.application_deadline = request.POST.get("application_deadline")

        job.status = request.POST.get("status")

        # Save Job
        job.save()

        # Update Skills
        skill_ids = request.POST.getlist("skills")
        job.skills.set(skill_ids)

        return redirect("manage_jobs")

    context = {"job": job,"categories": categories,"skills": skills,}

    return render(request,"frontend/hr/edit_job.html",context)



@login_required(login_url="login")
def hr_job_detail(request, job_id):

    hr_profile = get_object_or_404(HRProfile,user=request.user)

    company = get_object_or_404(Company,hr=hr_profile)

    job = get_object_or_404(Job,id=job_id,company=company)

    context = {"job": job,}

    return render(request,"frontend/hr/job_detail.html",context)



@login_required(login_url="login")
def hr_applications(request):

    hr_profile = get_object_or_404(HRProfile, user=request.user)

    company = get_object_or_404(Company, hr=hr_profile)

    applications = JobApplication.objects.filter(job__company=company).select_related("job","job_seeker")

    # Search only by candidate name
    search = request.GET.get("search", "").strip()

    if search:
        applications = applications.filter(
            Q(job_seeker__first_name__icontains=search) |
            Q(job_seeker__last_name__icontains=search)
        )

    applications = applications.order_by("-applied_date")

    total_applications = applications.count()

    new_applications = applications.filter(status="Applied").count()

    shortlisted_applications = applications.filter(status="Shortlisted").count()

    selected_applications = applications.filter(status="Selected").count()

    context = {
        "applications": applications,
        "total_applications": total_applications,
        "new_applications": new_applications,
        "shortlisted_applications": shortlisted_applications,
        "selected_applications": selected_applications,
        "search": search,
    }

    return render(request,"frontend/hr/applications.html",context)




@login_required(login_url="login")
def hr_application_detail(request, application_id):

    hr_profile = get_object_or_404(HRProfile,user=request.user)

    company = get_object_or_404(Company,hr=hr_profile)

    application = get_object_or_404(
        JobApplication.objects.select_related(
            "job",
            "job__company",
            "job__category",
            "job_seeker"
        ).prefetch_related(
            "job__skills"
        ),
        id=application_id,
        job__company=company
    )

    if request.method == "POST":

        new_status = request.POST.get("status")

        valid_statuses = dict(JobApplication.STATUS_CHOICES)

        old_status = application.status

        # Only update if status is valid AND actually changed
        if new_status in valid_statuses and new_status != old_status:

            application.status = new_status
            application.save()

            # Notification message according to status
            status_messages = {

                "Under Review":
                    f"Your application for {application.job.title} is now under review.",

                "Shortlisted":
                    f"Your application for {application.job.title} has been shortlisted.",

                "Interview":
                    f"You have been selected for an interview for {application.job.title}.",

                "Selected":
                    f"Congratulations! Your application for {application.job.title} has been selected.",

                "Rejected":
                    f"Your application for {application.job.title} has been rejected.",
            }

            Notification.objects.create(

                user=application.job_seeker,

                title=f"Application {new_status}",

                message=status_messages.get(
                    new_status,
                    f"Your application status has been changed to {new_status}."
                ),

                notification_type="Application",
            )

        return redirect("hr_application_detail",application_id=application.id)

    candidate_profile = getattr(application.job_seeker,"jobseekerprofile",None)

    candidate_skills = []

    if candidate_profile and candidate_profile.skills:
        candidate_skills = [
            skill.strip()
            for skill in candidate_profile.skills.split(",")
            if skill.strip()
        ]

    context = {
        "application": application,
        "candidate_profile": candidate_profile,
        "candidate_skills": candidate_skills,
    }

    return render(request,"frontend/hr/application_detail.html",context)



@login_required(login_url="login")
def hr_shortlisted(request):

    hr_profile = get_object_or_404(HRProfile,user=request.user)

    company = get_object_or_404(Company,hr=hr_profile)

    applications = JobApplication.objects.filter(
        job__company=company,
        status="Shortlisted"
    ).select_related(
        "job",
        "job_seeker"
    ).order_by("-updated_at")

    context = {
        "applications": applications,
        "page_title": "Shortlisted Candidates",
        "status": "Shortlisted",
    }

    return render(request,"frontend/hr/shortlisted.html",context)


@login_required(login_url="login")
def hr_selected(request):

    hr_profile = get_object_or_404(HRProfile,user=request.user)

    company = get_object_or_404(Company,hr=hr_profile)

    applications = JobApplication.objects.filter(
        job__company=company,
        status="Selected"
    ).select_related(
        "job",
        "job_seeker"
    ).order_by("-updated_at")

    context = {
        "applications": applications,
        "page_title": "Selected Candidates",
        "status": "Selected",
    }

    return render(request,"frontend/hr/selected.html",context)


@login_required(login_url="login")
def hr_rejected(request):

    hr_profile = get_object_or_404(HRProfile,user=request.user)

    company = get_object_or_404(Company,hr=hr_profile)

    applications = JobApplication.objects.filter(
        job__company=company,
        status="Rejected"
    ).select_related(
        "job",
        "job_seeker"
    ).order_by("-updated_at")

    context = {
        "applications": applications,
        "page_title": "Rejected Candidates",
        "status": "Rejected",
    }

    return render(request,"frontend/hr/rejected.html",context)

@login_required(login_url="login")
def hr_notifications(request):

    notifications = Notification.objects.filter(user=request.user).order_by("-created_at")

    unread_notifications_count = notifications.filter(is_read=False).count()

    context = {
        "notifications": notifications,
        "unread_notifications_count": unread_notifications_count,
    }

    return render(request,"frontend/hr/notifications.html",context)