import urllib

from django.shortcuts import render, get_object_or_404
from django.views import View
from django.shortcuts import render, redirect
from django.core.files.storage import default_storage
from io import BytesIO
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.conf import settings
from django.utils import timezone
from django.http import JsonResponse
import boto3
from .models import Report

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from django.contrib.auth import authenticate, login, logout

from django.contrib import messages

from .forms import UserLoginForm, UserRegistrationForm
import copy

from django.urls import reverse

from django.contrib.auth import logout as auth_logout

from django.core.exceptions import ValidationError


def home(request):
    default_page = 1
    page = request.GET.get('page', default_page)

    # This will order verified (TRUE) first and then by timestamp
    approved_reports = Report.objects.filter(status='RESOLVED').order_by('-verify', '-time_stamp')

    items_per_page = 3
    paginator = Paginator(approved_reports, items_per_page)

    try:
        items_page = paginator.page(page)
    except PageNotAnInteger:
        items_page = paginator.page(default_page)
    except EmptyPage:
        items_page = paginator.page(paginator.num_pages)

    return render(request, 'tenanttalk/home.html', {'approved_reports': approved_reports, 'items_page': items_page})

def report(request):
    if request.method == 'POST':
        # Get values from the POST request
        post_title = request.POST.get('post_title', '')[:30]  # Truncate to max length
        building_address = request.POST.get('building_address', '')[:100]  # Truncate to max length
        landlord_name = request.POST.get('landlord_name', '')[:30]  # Truncate to max length
        report_text = request.POST.get('report', '')[:200]  # Truncate to max length
        timestamp = timezone.now()

        # Check if a similar report already exists
        existing_report = Report.objects.filter(
            post_title=post_title,
            building_address=building_address,
            landlord_name=landlord_name,
            report=report_text,
        ).exists()

        if existing_report:
            messages.warning(request,
                             "A similar report already exists. Please check your inputs or submit a new report with different details.")
            return render(request, "tenanttalk/report.html")

        new_report = Report(
            post_title=post_title,
            building_address=building_address,
            landlord_name=landlord_name,
            report=report_text,
            time_stamp=timestamp,
        )

        if request.user.is_authenticated:
            user_name = request.user.username[:30]  # Truncate to max length
            new_report.user = user_name
        else:
            user_name = "ANONYMOUS"

        try:
            new_report.save()
        except ValidationError as e:
            # Handle validation errors (e.g., length violations)
            messages.error(request, f"Error saving report: {e}")
            return render(request, "tenanttalk/report.html")

        # File upload handling
        post_id = post_title + '-' + timestamp.strftime('%Y%m%d-%H%M')

        def save_file(file, filename):
            if file and file.size > 0:
                data = BytesIO(file.read())
                default_storage.save(filename, data)

        # Handle optional file uploads with proper error handling
        if 'pdf' in request.FILES:
            pdf_file = request.FILES['pdf']
            if pdf_file.content_type != 'application/pdf':
                messages.error(request, "Invalid file format, must be a PDF.")
                return render(request, "tenanttalk/report.html")

            object_name = f'uploads/{user_name}/{post_id}/{pdf_file.name[:100]}'
            save_file(pdf_file, object_name)

        if 'txt' in request.FILES:
            txt_file = request.FILES['txt']
            object_name = f'uploads/{user_name}/{post_id}/{txt_file.name[:100]}'
            save_file(txt_file, object_name)

        if 'jpg' in request.FILES:
            jpg_file = request.FILES['jpg']
            object_name = f'uploads/{user_name}/{post_id}/{jpg_file.name[:100]}'
            save_file(jpg_file, object_name)

        # Redirect to home or another relevant page
        return redirect('home')  # Change 'home' to your desired redirect view name

    # Render the report page for GET requests
    return render(request, "tenanttalk/report.html")


def myaccount(request):
    default_page = 1
    page = request.GET.get('page', default_page)

    if request.user.is_superuser:
        # Render admin myaccount template for superusers
        return render(request, 'tenanttalk/adminaccount.html')
    elif request.user.is_staff:
        # Retrieve all reports for staff members

        # staff_reports = Report.objects.all()
        # return render(request, 'tenanttalk/staffaccount.html', {'staff_reports': staff_reports})

        staff_reports = Report.objects.all()
        report_files_mapping = {}
        for report in staff_reports:
            files = view_report_upload(report)
            report_files_mapping[report] = files
        return render(request, 'tenanttalk/staffaccount.html', {'staff_reports': staff_reports, 'report_files_mapping': report_files_mapping})
    
    elif request.user.is_authenticated:
        # Retrieve user's reports
        user_reports = Report.objects.filter(user=request.user.username)

        items_per_page = 3
        paginator = Paginator(user_reports, items_per_page)

        try:
            items_page = paginator.page(page)
        except PageNotAnInteger:
            items_page = paginator.page(default_page)
        except EmptyPage:
            items_page = paginator.page(paginator.num_pages)
        
        # Pass the first report (if exists) to the template context
        report = user_reports.first()
        return render(request, 'tenanttalk/myaccount.html', {'user_reports': user_reports, 'report': report, 'items_page': items_page})
    else:
        # Render regular user myaccount template for non-authenticated users
        return render(request, 'tenanttalk/myaccount.html')


def view_report(request, report_id):
    report = get_object_or_404(Report, pk=report_id)
    files = view_report_upload(report)

    if request.method == 'POST':
        # Handle feedback submission
        feedback = request.POST.get('feedback')
        if feedback:
            report.feedback = feedback

        # Change the status to IN_PROGRESS if it's NEW
        if report.status == 'NEW':
            report.status = 'IN_PROGRESS'

        resolve = request.POST.get('resolve')
        unresolve = request.POST.get('unresolve')

        if resolve:
            report.status = 'RESOLVED'
            report.verify = "TRUE"

        if unresolve:
            report.status = 'RESOLVED'

        # Save the report
        report.save()

        # Redirect back to the same view
        return redirect('view_report', report_id=report_id)

    return render(request, 'tenanttalk/viewreport.html', {'report': report, 'files': files})


def generate_presigned_url(bucket_name, key):
    s3 = boto3.client('s3',
                      aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                      aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                      region_name=settings.AWS_S3_REGION_NAME,
                      config=boto3.session.Config(signature_version='s3v4'))
    url = s3.generate_presigned_url(
        'get_object',
        Params={'Bucket': bucket_name, 'Key': key},
        ExpiresIn=3600  # URL expires in 1 hour (adjust as needed)
    )
    return url


def viewuploads(request):
    if request.user.is_staff:
        # Connect to S3
        s3 = boto3.client('s3',
                          aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                          aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)

        # Bucket name and folder prefix
        bucket_name = settings.AWS_STORAGE_BUCKET_NAME
        folder_prefix = ['pdfs/', 'txts/', 'jpgs/']
        files = []

        for folder in folder_prefix:
            # List objects in the bucket with the specified prefix
            response = s3.list_objects_v2(Bucket=bucket_name, Prefix=folder)

            # Extract file names and generate download links
            if 'Contents' in response:
                for obj in response['Contents']:
                    file_name = obj['Key'].split('/')[-1]
                    file_key = obj['Key']
                    file_url = generate_presigned_url(bucket_name, file_key)
                    files.append({'name': file_name, 'url': file_url})

        return render(request, 'tenanttalk/viewuploads.html', {'files': files})
    else:
        home(request)

def view_user_uploads(request):
    if not request.user.is_staff:
        # Connect to S3
        s3 = boto3.client('s3',
                          aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                          aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)

        # Bucket name
        bucket_name = settings.AWS_STORAGE_BUCKET_NAME
        prefix = f'uploads/{request.user.username}/'
        files = []

        # List objects in the bucket with the specified prefix
        response = s3.list_objects_v2(Bucket=bucket_name, Prefix=prefix)

        # Extract file names and generate download links
        if 'Contents' in response:
            for obj in response['Contents']:
                file_name = obj['Key'].split('/')[-1]
                file_key = obj['Key']
                file_url = generate_presigned_url(bucket_name, file_key)
                files.append({'name': file_name, 'url': file_url})
                # CHANGE THIS TEMPLATE NAME
            return render(request, 'tenanttalk/viewuploads.html', {'files': files})
        else:
            home(request)



# below edits
def custom_login(request):
    if request.method == "POST":
        form = UserLoginForm(request=request, data=request.POST)
        if form.is_valid():
            user = authenticate(
                username=form.cleaned_data["username"],
                password=form.cleaned_data["password"],
            )
            if user is not None:
                login(request, user)
                messages.success(request, f"Hello {user.username}! You have been logged in")
                return redirect("home")
            else:
                messages.error(request, "Invalid username or password")
        else:
            for key, error in form.errors.items():
                messages.error(request, f"{key}: {error}")
    else:
        form = UserLoginForm()

    if request.user.is_authenticated:
        # If the user is already authenticated, perform logout
        auth_logout(request)
        messages.info(request, "You have been logged out")
        return render(request, 'tenanttalk/account/logout.html')

    return render(request=request, template_name="tenanttalk/account/login.html", context={"form": form})


def custom_logout(request):
    logout(request)
    return render(request, 'tenanttalk/account/logout.html')   # Redirect to homepage after logout, replace 'home' with your homepage URL pattern


def custom_signup(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            # Optionally, you can authenticate and login the user immediately after registration
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            if user is not None:
                login(request, user)
                # Redirect to a success page or home page
                return redirect('home')  # Adjust this according to your URL configurations
    else:
        form = UserRegistrationForm()
    return render(request, 'tenanttalk/account/signup.html', {'form': form})


#im so confsued


GOOGLE_LOGIN_URL_PREFIX = '/accounts/google/login/?'

def redirectToGoogle(request):
    coming_from = request.GET.get("next", "/manage")
    url_params = {
        "process": "login",
        "next": coming_from
    }
    suffix = urllib.parse.urlencode(url_params)
    return redirect(GOOGLE_LOGIN_URL_PREFIX + suffix)

def view_report_upload(report):
    # Connect to S3
    s3 = boto3.client('s3',
                      aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                      aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)

    # Bucket name
    bucket_name = settings.AWS_STORAGE_BUCKET_NAME
    post_id = report.post_title + '-' + report.time_stamp.strftime('%Y%m%d-%H%M')
    prefix = f'uploads/{report.user}/{post_id}/'
    files = []

    # List objects in the bucket with the specified prefix
    response = s3.list_objects_v2(Bucket=bucket_name, Prefix=prefix)

    # Extract file names and generate download links
    if 'Contents' in response:
        for obj in response['Contents']:
            file_name = obj['Key'].split('/')[-1]
            file_key = obj['Key']
            file_url = generate_presigned_url(bucket_name, file_key)
            files.append({'name': file_name, 'url': file_url})
        return files
