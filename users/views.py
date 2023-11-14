import uuid
from django.shortcuts import render, get_object_or_404
from .models import Manuscripts, Librarian, Visitors, Staffs, VisitorView, CurrentStudent, Staff, Faculty, Alumni, PageVisit
from django.db.models import Count
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import User, auth
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404, reverse
from .email import send_request_download_mail
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.db.models import Sum
import requests
from django.db.models.functions import ExtractMonth
from django.contrib.sessions.models import Session
from uuid import uuid4
from datetime import datetime
from django.db.models import Q
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models.functions import TruncDate
from datetime import date, timedelta
from django.utils import timezone
from django.db.models import Count
# Create your views here.


def graph_yesterday(request):
    # Calculate the date for yesterday
    yesterday_datetime = timezone.now()
    yesterday = yesterday_datetime - timedelta(days=1)

    # Filter PageVisit objects for visits on the previous day
    yesterday_all_visits = PageVisit.objects.filter(
        visited_at=yesterday.date()).count()



    # Filter PageVisit objects for visits on the previous day and with last_name 'Current Student'
    yesterday_students_visits = PageVisit.objects.filter(
        visited_at=yesterday.date(),
        # Make sure 'yesterday Student' is enclosed in single quotes
        user__last_name='Current Student'
    )
    yesterday_student_count = yesterday_students_visits.count()
    
    
    
    # Filter PageVisit objects for visits on the previous day and with last_name 'Current Student'
    yesterday_staff_visits = PageVisit.objects.filter(
        visited_at=yesterday.date(),
        # Make sure 'yesterday Student' is enclosed in single quotes
        user__last_name='Staff'
    )
    yesterday_staff_count = yesterday_staff_visits.count()
    
    
    
    # Filter PageVisit objects for visits on the previous day and with last_name 'Current Student'
    yesterday_alumni_visits = PageVisit.objects.filter(
        visited_at=yesterday.date(),
        # Make sure 'yesterday Student' is enclosed in single quotes
        user__last_name='Alumni'
    )
    yesterday_alumni_count = yesterday_alumni_visits.count()
    
    
    
    # Filter PageVisit objects for visits on the previous day and with last_name 'Current Student'
    yesterday_faculty_visits = PageVisit.objects.filter(
        visited_at=yesterday.date(),
        # Make sure 'yesterday Student' is enclosed in single quotes
        user__last_name='Faculty'
    )
    yesterday_faculty_count = yesterday_faculty_visits.count()
    
    visitors = User.objects.filter(Q(email='') & ~Q(is_superuser=True))
    
    context = {
        'visitors': visitors,
        'yesterday_student_count': yesterday_student_count,
        'yesterday_alumni_count': yesterday_alumni_count,
        'yesterday_faculty_count': yesterday_faculty_count,
        'yesterday_staff_count': yesterday_faculty_count,
        'yesterday_datetime': yesterday_datetime,
        'yesterday_all_visits': yesterday_all_visits,
        
    }
    return render(request, "admin/graphs-yesterday.html", context)








def graph(request):
    current_datetime = timezone.now()
    daily_all_visits = PageVisit.objects.filter(
        visited_at=current_datetime.date()).count()
 
    # Filter PageVisit objects for visits on the current day and month
    current_students_visits = PageVisit.objects.filter(
        visited_at=current_datetime.date(),
        # Replace 'last_name' with the actual field name
        user__last_name='Current Student'
    )

    # Count the PageVisits for current students
    student_count = current_students_visits.count()

    current_staffs_visits = PageVisit.objects.filter(
        visited_at=current_datetime.date(),
        user__last_name='Staff'  # Replace 'last_name' with the actual field name
    )

    # Count the PageVisits for current staffs
    staffs_count = current_staffs_visits.count()

    current_faculty_visits = PageVisit.objects.filter(
        visited_at=current_datetime.date(),
        user__last_name='Faculty'  # Replace 'last_name' with the actual field name
    )

    # Count the PageVisits for current faculty
    faculty_count = current_faculty_visits.count()

    current_alumni_visits = PageVisit.objects.filter(
        visited_at=current_datetime.date(),
        user__last_name='Alumni'  # Replace 'last_name' with the actual field name
    )

    # Count the PageVisits for current alumni
    alumni_count = current_alumni_visits.count()

    visitors = User.objects.filter(Q(email='') & ~Q(is_superuser=True))

    context = {
        'daily_all_visits': daily_all_visits,
        'student_count': student_count,
        'staffs_count': staffs_count,
        'faculty_count': faculty_count,
        'alumni_count': alumni_count,
        'current_datetime': current_datetime,
        'visitors': visitors,
    }

    return render(request, 'admin/graphs.html', context)


'''def visualgraph(request):
    return render(request, 'admin/includes/visual-graphs.html')
'''


def is_superuser_or_staff(user):
    return user.is_superuser or user.is_staff


def welcome(request):
    return render(request, 'index.html')


def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        info = auth.authenticate(username=username, password=password)
        if info is not None:
            auth.login(request, info)
            if info.is_superuser:
                return redirect('dashboard')
            elif info.is_staff:
                return redirect('dashboard')
            else:
                return redirect('visitor_index')
        else:
            messages.error(request, "Invalid USERNAME or PASSWORD")
            return redirect('login')
    else:
        return render(request, 'login.html')


def signup_stud(request):
    if request.method == 'POST':

        full_name = request.POST['name']
        program = request.POST['program']
        username = request.POST['username']
        year = request.POST['year']
        role = request.POST['role']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        if password1 == password2:
            if User.objects.filter(username=username).exists():
                messages.error(request, 'Username already taken.')
                return redirect('signup_stud')

            else:
                new_student = User.objects.create_user(
                    first_name=full_name, username=username, password=password1, last_name=role)
                new_student.save()

                profile_currentStud = CurrentStudent.objects.create(
                    user=new_student, program=program, year=year)
                profile_currentStud.save()
                messages.success(request, 'Account created')
                return redirect('login')
        else:
            messages.error(request, 'Password does not match.')
            return redirect('signup_stud')
    return render(request, 'signupstud.html')


def signup_staff(request):
    if request.method == 'POST':

        full_name = request.POST['full_name']
        office = request.POST['office']
        username = request.POST['username']
        role = request.POST['role']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        if password1 == password2:
            # Check if the username exists
            if User.objects.filter(username=username).exists():
                messages.error(request, 'Username already taken.')
                return redirect('signup_staff')

            else:
                new_staff = User.objects.create_user(
                    first_name=full_name, username=username, password=password1, last_name=role)
                new_staff.save()

                profile_staff = Staff.objects.create(
                    user=new_staff, office=office)
                profile_staff.save()
                messages.success(request, 'Account created')
                return redirect('login')
        else:
            messages.error(request, 'Password not match.')
            return redirect('signup_staff')
    return render(request, 'signup_staff.html')


def signup_faculty(request):
    if request.method == 'POST':
        full_name = request.POST['full_name']
        department = request.POST['department']
        username = request.POST['username']
        role = request.POST['role']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        if password1 == password2:
            if User.objects.filter(username=username).exists():
                messages.error(request, 'Username already taken.')
                return redirect('signup_faculty')

            else:
                new_faculty = User.objects.create_user(
                    first_name=full_name, username=username, password=password1, last_name=role)
                new_faculty.save()

                profile_faculty = Faculty.objects.create(
                    user=new_faculty, department=department)
                profile_faculty.save()
                messages.success(request, 'Account created')
                return redirect('login')
        else:
            messages.error(request, 'Password not match.')
            return redirect('signup_faculty')
    return render(request, 'signup_faculty.html')


def signup_alumni(request):

    if request.method == 'POST':

        full_name = request.POST['fullname']
        affiliation = request.POST['affiliation']
        username = request.POST['username']
        role = request.POST['role']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        if password1 == password2:
            # Check if the username exists
            if User.objects.filter(username=username).exists():
                messages.error(request, 'Username already taken.')
                return redirect('signup_alumni')

            else:
                new_alumni = User.objects.create_user(
                    first_name=full_name, username=username, password=password1, last_name=role)
                new_alumni.save()

                profile_alumni = Alumni.objects.create(
                    user=new_alumni, affiliation=affiliation)
                profile_alumni.save()
                messages.success(request, 'Account created')
                return redirect('login')
        else:
            messages.error(request, 'Password not match.')
            return redirect('signup_alumni')
    return render(request, 'signup_alumni.html')


@login_required(login_url='/login')
@user_passes_test(is_superuser_or_staff)
def dashboard(request):
    manuscripts_count = Manuscripts.objects.all().count()
    requests_count = Visitors.objects.all()
    librarians_count = User.objects.exclude(email='').count()
    visits = PageVisit.objects.all().count()

    manuscripts = Manuscripts.objects.order_by('-id')[:5]
    requests_order = Visitors.objects.order_by('-id')[:5]

    bsit_count = Manuscripts.objects.filter(program='BSIT').count()
    bsed_count = Manuscripts.objects.filter(program='BSED').count()
    beed_count = Manuscripts.objects.filter(program='BEED').count()
    bssw_count = Manuscripts.objects.filter(program='BSSW').count()
    bapos_count = Manuscripts.objects.filter(program='BAPos').count()
    baels_count = Manuscripts.objects.filter(program='BAELS').count()
    bsm_count = Manuscripts.objects.filter(program='BSM').count()
    bsa_count = Manuscripts.objects.filter(program='BSA').count()
    bsf_count = Manuscripts.objects.filter(program='BSF').count()
    bses_count = Manuscripts.objects.filter(program='BSES').count()
    bsce_count = Manuscripts.objects.filter(program='BSCE').count()

    downloads = Manuscripts.objects.values('downloads').all()
    total_downloads = downloads.aggregate(Sum('downloads'))['downloads__sum']

    api_key = '45b01a7f6a9893cc9370a6fd91f105fb'
    url = f"http://api.openweathermap.org/data/2.5/forecast?q=mati&appid={api_key}"
    w_dataset = requests.get(url).json()

    now = datetime.now()
    hour = now.hour

    if 0 <= hour < 12:
        greeting = "Good Morning"
        time = 'day'
    elif 12 <= hour < 18:
        greeting = "Good Afternoon"
        time = 'noon'
    else:
        greeting = "Good Evening"
        time = 'evening'

    context = {

        "city_name": w_dataset["city"]["name"],
        "city_country": w_dataset["city"]["country"],
        "wind": w_dataset['list'][0]['wind']['speed'],
        "degree": w_dataset['list'][0]['wind']['deg'],
        "status": w_dataset['list'][0]['weather'][0]['description'],
        "cloud": w_dataset['list'][0]['clouds']['all'],
        'date': w_dataset['list'][0]["dt_txt"],
        "temp": round(w_dataset["list"][0]["main"]["temp"] - 273.0),
        "pressure": w_dataset["list"][0]["main"]["pressure"],
        "humidity": w_dataset["list"][0]["main"]["humidity"],
        "icon": w_dataset["list"][0]["weather"][0]["icon"],
        "icon1": w_dataset["list"][1]["weather"][0]["icon"],
        "icon2": w_dataset["list"][2]["weather"][0]["icon"],
        "icon3": w_dataset["list"][3]["weather"][0]["icon"],
        "icon4": w_dataset["list"][4]["weather"][0]["icon"],
        "icon5": w_dataset["list"][5]["weather"][0]["icon"],
        "icon6": w_dataset["list"][6]["weather"][0]["icon"],


        "manuscripts_count": manuscripts_count,
        "manuscripts": manuscripts,
        "librarians_count": librarians_count,
        "requests_count": requests_count,
        "visits": visits,
        "requests": requests_order,
        "bsit_count": bsit_count,
        "bsed_count": bsed_count,
        "beed_count": beed_count,
        "bssw_count": bssw_count,
        "bapos_count": bapos_count,
        "baels_count": baels_count,
        "bsm_count": bsm_count,
        "bsa_count": bsa_count,
        "bsf_count": bsf_count,
        "bses_count": bses_count,
        "bsce_count": bsce_count,
        "total_downloads": total_downloads,

        'greeting': greeting,
        'time': time,
    }
    return render(request, 'admin/dashboard.html', context)


@login_required(login_url='login')
@user_passes_test(is_superuser_or_staff)
def manuscripts(request):
    manuscripts = Manuscripts.objects.all().order_by('id')

    if request.method == 'POST':

        title = request.POST['title']
        authors = request.POST['authors']
        filename = request.FILES['files']
        program = request.POST['program']
        year = request.POST['year']
        abes_num = request.POST['abstractESNum']

        new_books = Manuscripts(title=title, authors=authors, filename=filename,
                                program=program, year=year, abstractES_num=abes_num)
        new_books.save()
        messages.success(request, 'Manuscript added')
    context = {
        'manuscripts': manuscripts
    }
    return render(request, 'admin/manuscript.html', context)


@login_required(login_url='login')
@user_passes_test(is_superuser_or_staff)
def users(request):
    users = User.objects.all().order_by('id')
    context = {'user': users}

    if request.method == 'POST':

        first_name = request.POST['full_name']
        mobile = request.POST['mobile']
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        if password1 == password2:
            if User.objects.filter(last_name=mobile).exists():
                messages.error(request, 'Mobile Number already taken.')
                return redirect('users')

            elif User.objects.filter(username=username).exists():
                messages.error(request, 'Username already taken.')
                return redirect('users')

            elif User.objects.filter(email=email).exists():
                messages.error(request, 'Email already taken.')
                return redirect('users')
            else:
                new_user = User.objects.create_user(
                    username=username, password=password1, email=email, first_name=first_name, last_name=mobile)
                new_user.is_staff = True  # Set the user as staff
                new_user.save()

                profile_obj = Staffs.objects.create(credentials=new_user)
                profile_obj.save()
                messages.success(request, 'Librarian Account created')
                return redirect('users')
        else:
            messages.error(request, 'Password not match.')
            return redirect('users')

    return render(request, 'admin/users.html', context)


def requests_view(request):
    visitors = Visitors.objects.filter(status='Not Granted').order_by('-id')
    context = {'visitor': visitors}

    return render(request, 'admin/requests.html', context)


def send_email_download_request(request):

    if request.method == 'POST':
        email_visitor = request.POST.get('email')
        id_file = request.POST.get('id')
        isGranted = "Granted"

        if not Visitors.objects.filter(email=email_visitor)[0]:
            messages.success(request, 'No email found with this username.')
            return redirect('requests')

        token = str(uuid.uuid4())

        visitor_update = Visitors.objects.get(email=email_visitor, id=id_file)
        visitor_update.requests_email_token = token
        visitor_update.status = isGranted
        visitor_update.save()

        send_request_download_mail(email_visitor, token)
        messages.success(request, 'Request Granted')
        return redirect('requests')

    return render(request, 'visitors/request.html')


def download(request, token):

    download = Visitors.objects.filter(requests_email_token=token).first()
    file_id = download.filename_id

    download_count = get_object_or_404(Manuscripts, pk=file_id)
    download_count.downloads += 1
    download_count.save()

    context = {
        'id_file': download.filename_id,
        'file': download.file_link,
        'name': download.filename.title,
        'downloads': download.filename.downloads
    }
    return render(request, 'visitors/requests.html', context)


'''
def increment_count(request):
    file_id = request.get('item_id')
    item = get_object_or_404(Manuscripts, pk=file_id)

    # Increment the download count
    item.downloads += 1
    item.save()
    return JsonResponse({'count': item.downloads})

def update_download_count(request):
    item_id = request.POST.get('item_id')
    item = get_object_or_404(Manuscripts, pk=item_id)

    # Increment the download count
    item.downloads += 1
    item.save()

    return JsonResponse({'status': 'success'})

'''


@login_required(login_url='login')
def visitor_index(request):

    current_datetime = timezone.now()
    date_now = current_datetime.date()
    manuscripts = Manuscripts.objects.all().order_by('-year')

    if request.method == "POST":
        email = request.POST['email']
        fileLink = request.POST['file_link']
        fileName = request.POST['file_name']

        token = str(uuid.uuid4())
        new_requests = Visitors(email=email, file_link=fileLink,
                                filename_id=fileName, requests_email_token=token)
        new_requests.save()

    if request.user.is_authenticated:
        # Create a page visit record for the logged-in user
        PageVisit.objects.create(user=request.user, visited_at=date_now)

        # Get the total page visits for the current user

        page_visits = PageVisit.objects.filter(user=request.user).count()
    context = {
        'page_visits': page_visits,
        'manuscripts': manuscripts
    }
    return render(request, 'visitors/index.html', context)


def delete_users(request, user_id):
    User.objects.filter(id=user_id).delete()
    messages.success(request, 'Librarian User deleted')
    return redirect('/users')


def updatestaff(request, staff_id):
    user_fullname = request.POST.get('full_name')
    user_username = request.POST.get('username')
    user_email = request.POST.get('email')
    user_number = request.POST.get('mobile')
    new_password = request.POST.get('new_password')

    user_update = User.objects.get(id=staff_id)
    user_update.first_name = user_fullname
    user_update.email = user_email
    user_update.last_name = user_number
    user_update.username = user_username

    if new_password:
        user_update.set_password(new_password)

    user_update.save()

    # Send an email notification to the staff
    if new_password:
        subject = 'Password Changed'
        message = f'Your password has been changed successfully by the Librarian. Your new password is: {new_password}'
        from_email = 'jhmainlib.erepository@gmail.com'  # Set the sender's email address
        recipient_list = [user_email]

        EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
        EMAIL_HOST = 'smtp.gmail.com'
        EMAIL_USE_TLS = True
        EMAIL_PORT = 587
        EMAIL_HOST_USER = 'jhmainlib.erepository@gmail.com'
        EMAIL_HOST_PASSWORD = 'hlqzmmjohqrukrlv'

        send_mail(subject, message, from_email, recipient_list,
                  auth_user=EMAIL_HOST_USER, auth_password=EMAIL_HOST_PASSWORD)

    messages.success(request, 'Librarian Staff info changed')

    return redirect('/users')


def delete_books(request, books_id):
    try:
        manuscript = Manuscripts.objects.get(id=books_id)
        # Replace 'pdf_field' with the actual field name for your PDF
        pdf_file_path = manuscript.filename.path

        # Delete the PDF file from storage
        if default_storage.exists(pdf_file_path):
            default_storage.delete(pdf_file_path)

        manuscript.delete()
        messages.success(request, 'Manuscript deleted')
    except Manuscripts.DoesNotExist:
        messages.error(request, 'Manuscript not found')

    return redirect('/manuscripts')


def edit_books(request, book_id):
    manuscript_title = request.POST.get('title')
    manuscript_authors = request.POST.get('authors')
    manuscript_program = request.POST.get('program')
    manuscript_year = request.POST.get('year')
    manuscript_abstractES_num = request.POST.get('abstractESNum')
    manuscript_update = Manuscripts.objects.get(id=book_id)

    # Check if a new file was uploaded
    new_manuscript_file = request.FILES.get('files')

    if new_manuscript_file:
        # Remove the old file if it exists
        if manuscript_update.filename:
            default_storage.delete(manuscript_update.filename.path)

        # Save the new file
        manuscript_update.filename.save(
            new_manuscript_file.name, new_manuscript_file)
        manuscript_update.downloads = 0  # Reset downloads to zero here

    manuscript_update.title = manuscript_title
    manuscript_update.authors = manuscript_authors
    manuscript_update.program = manuscript_program
    manuscript_update.year = manuscript_year
    manuscript_update.abstractES_num = manuscript_abstractES_num
    manuscript_update.save()

    messages.success(request, 'Manuscript Changed')
    return redirect('/manuscripts')


def delete_request(request, request_id):
    Visitors.objects.filter(id=request_id).delete()
    messages.success(request, 'Request deleted')
    return redirect('/requests')


def signin(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = auth.authenticate(username=username, password=password)
        if user is not None:
            auth.login(request, user)
            return redirect("dashboard")
        elif username == 'admin' and password == 'admin123':
            return redirect('dashboard')
        else:
            messages.info(request, "Invalid USERNAME or PASSWORD")
            return redirect("signin")
    else:
        return render(request, 'admin/signin.html')


def logoutUser(request):
    auth.logout(request)
    messages.info(request, "Logged out Successfully!")
    return redirect('login')


@login_required(login_url='login')
def bsit(request):
    manuscripts = Manuscripts.objects.filter(program='BSIT').order_by('-year')

    if request.method == "POST":
        email = request.POST['email']
        fileLink = request.POST['file_link']
        fileName = request.POST['file_name']

        token = str(uuid.uuid4())
        new_requests = Visitors(email=email, file_link=fileLink,
                                filename_id=fileName, requests_email_token=token)
        new_requests.save()

    # Retrieve the visitor count object, or create a new one if it doesn't exist yet

    context = {
        'manuscripts': manuscripts
    }
    return render(request, 'visitors/courses.html', context)


@login_required(login_url='login')
def bsed(request):
    manuscripts = Manuscripts.objects.filter(program='BSED').order_by('-year')

    if request.method == "POST":
        email = request.POST['email']
        fileLink = request.POST['file_link']
        fileName = request.POST['file_name']

        token = str(uuid.uuid4())
        new_requests = Visitors(email=email, file_link=fileLink,
                                filename_id=fileName, requests_email_token=token)
        new_requests.save()

    # Retrieve the visitor count object, or create a new one if it doesn't exist yet

    context = {
        'manuscripts': manuscripts
    }
    return render(request, 'visitors/courses.html', context)


@login_required(login_url='login')
def beed(request):
    manuscripts = Manuscripts.objects.filter(program='BEED').order_by('-year')

    if request.method == "POST":
        email = request.POST['email']
        fileLink = request.POST['file_link']
        fileName = request.POST['file_name']

        token = str(uuid.uuid4())
        new_requests = Visitors(email=email, file_link=fileLink,
                                filename_id=fileName, requests_email_token=token)
        new_requests.save()

    # Retrieve the visitor count object, or create a new one if it doesn't exist yet

    context = {
        'manuscripts': manuscripts
    }
    return render(request, 'visitors/courses.html', context)


@login_required(login_url='login')
def bssw(request):
    manuscripts = Manuscripts.objects.filter(program='BSSW').order_by('-year')

    if request.method == "POST":
        email = request.POST['email']
        fileLink = request.POST['file_link']
        fileName = request.POST['file_name']

        token = str(uuid.uuid4())
        new_requests = Visitors(email=email, file_link=fileLink,
                                filename_id=fileName, requests_email_token=token)
        new_requests.save()

    # Retrieve the visitor count object, or create a new one if it doesn't exist yet

    context = {
        'manuscripts': manuscripts
    }
    return render(request, 'visitors/courses.html', context)


@login_required(login_url='login')
def bapos(request):
    manuscripts = Manuscripts.objects.filter(program='BAPos').order_by('-year')

    if request.method == "POST":
        email = request.POST['email']
        fileLink = request.POST['file_link']
        fileName = request.POST['file_name']

        token = str(uuid.uuid4())
        new_requests = Visitors(email=email, file_link=fileLink,
                                filename_id=fileName, requests_email_token=token)
        new_requests.save()

    # Retrieve the visitor count object, or create a new one if it doesn't exist yet

    context = {
        'manuscripts': manuscripts
    }
    return render(request, 'visitors/courses.html', context)


@login_required(login_url='login')
def baels(request):
    manuscripts = Manuscripts.objects.filter(program='BAELS').order_by('-year')

    if request.method == "POST":
        email = request.POST['email']
        fileLink = request.POST['file_link']
        fileName = request.POST['file_name']

        token = str(uuid.uuid4())
        new_requests = Visitors(email=email, file_link=fileLink,
                                filename_id=fileName, requests_email_token=token)
        new_requests.save()

    # Retrieve the visitor count object, or create a new one if it doesn't exist yet

    context = {
        'manuscripts': manuscripts
    }
    return render(request, 'visitors/courses.html', context)


@login_required(login_url='login')
def bsm(request):
    manuscripts = Manuscripts.objects.filter(program='BSM').order_by('-year')

    if request.method == "POST":
        email = request.POST['email']
        fileLink = request.POST['file_link']
        fileName = request.POST['file_name']

        token = str(uuid.uuid4())
        new_requests = Visitors(email=email, file_link=fileLink,
                                filename_id=fileName, requests_email_token=token)
        new_requests.save()

    # Retrieve the visitor count object, or create a new one if it doesn't exist yet

    context = {
        'manuscripts': manuscripts
    }
    return render(request, 'visitors/courses.html', context)


@login_required(login_url='login')
def bsa(request):
    manuscripts = Manuscripts.objects.filter(program='BSA').order_by('-year')

    if request.method == "POST":
        email = request.POST['email']
        fileLink = request.POST['file_link']
        fileName = request.POST['file_name']

        token = str(uuid.uuid4())
        new_requests = Visitors(email=email, file_link=fileLink,
                                filename_id=fileName, requests_email_token=token)
        new_requests.save()

    # Retrieve the visitor count object, or create a new one if it doesn't exist yet

    context = {
        'manuscripts': manuscripts
    }
    return render(request, 'visitors/courses.html', context)


@login_required(login_url='login')
def bsf(request):
    manuscripts = Manuscripts.objects.filter(program='BSF').order_by('-year')

    if request.method == "POST":
        email = request.POST['email']
        fileLink = request.POST['file_link']
        fileName = request.POST['file_name']

        token = str(uuid.uuid4())
        new_requests = Visitors(email=email, file_link=fileLink,
                                filename_id=fileName, requests_email_token=token)
        new_requests.save()

    # Retrieve the visitor count object, or create a new one if it doesn't exist yet

    context = {
        'manuscripts': manuscripts
    }
    return render(request, 'visitors/courses.html', context)


@login_required(login_url='login')
def bses(request):
    manuscripts = Manuscripts.objects.filter(program='BSES').order_by('-year')

    if request.method == "POST":
        email = request.POST['email']
        fileLink = request.POST['file_link']
        fileName = request.POST['file_name']

        token = str(uuid.uuid4())
        new_requests = Visitors(email=email, file_link=fileLink,
                                filename_id=fileName, requests_email_token=token)
        new_requests.save()

    # Retrieve the visitor count object, or create a new one if it doesn't exist yet

    context = {
        'manuscripts': manuscripts
    }
    return render(request, 'visitors/courses.html', context)


@login_required(login_url='login')
def bsce(request):
    manuscripts = Manuscripts.objects.filter(program='BSCE').order_by('-year')

    if request.method == "POST":
        email = request.POST['email']
        fileLink = request.POST['file_link']
        fileName = request.POST['file_name']

        token = str(uuid.uuid4())
        new_requests = Visitors(email=email, file_link=fileLink,
                                filename_id=fileName, requests_email_token=token)
        new_requests.save()

    # Retrieve the visitor count object, or create a new one if it doesn't exist yet

    context = {
        'manuscripts': manuscripts
    }
    return render(request, 'visitors/courses.html', context)













def graph_sevendays(request):
    # Calculate the date for yesterday
    yesterday_datetime = timezone.now()
    
    yesterday = yesterday_datetime - timedelta(days=1)
    yesterday_2days = yesterday_datetime - timedelta(days=2)
    yesterday_3days = yesterday_datetime - timedelta(days=3)
    yesterday_4days = yesterday_datetime - timedelta(days=4)
    yesterday_5days = yesterday_datetime - timedelta(days=5)
    yesterday_6days = yesterday_datetime - timedelta(days=6)
    yesterday_7days = yesterday_datetime - timedelta(days=7)
    yesterday_8days = yesterday_datetime - timedelta(days=8)
    # Filter PageVisit objects for visits on the previous day
    yesterday_all_visits = PageVisit.objects.filter(
        visited_at=yesterday.date()).count()

    # Filter PageVisit objects for visits on the previous day and with last_name 'Current Student'
    yesterday7_students_visits = PageVisit.objects.filter(
        visited_at=yesterday_7days.date(),
        # Make sure 'yesterday Student' is enclosed in single quotes
        user__last_name='Current Student'
    )
    yesterday7_student_count = yesterday7_students_visits.count()
    
    # Filter PageVisit objects for visits on the previous day and with last_name 'Current Student'
    yesterday7_staff_visits = PageVisit.objects.filter(
        visited_at=yesterday_7days.date(),
        # Make sure 'yesterday Student' is enclosed in single quotes
        user__last_name='Staff'
    )
    yesterday7_staff_count = yesterday7_staff_visits.count()
    
    # Filter PageVisit objects for visits on the previous day and with last_name 'Current Student'
    yesterday7_alumni_visits = PageVisit.objects.filter(
        visited_at=yesterday_7days.date(),
        # Make sure 'yesterday Student' is enclosed in single quotes
        user__last_name='Alumni'
    )
    yesterday7_alumni_count = yesterday7_alumni_visits.count()
    
    # Filter PageVisit objects for visits on the previous day and with last_name 'Current Student'
    yesterday7_faculty_visits = PageVisit.objects.filter(
        visited_at=yesterday_7days.date(),
        # Make sure 'yesterday Student' is enclosed in single quotes
        user__last_name='Faculty'
    )
    yesterday7_faculty_count = yesterday7_faculty_visits.count()

    
    # Filter PageVisit objects for visits on the previous day and with last_name 'Current Student'
    yesterday6_students_visits = PageVisit.objects.filter(
        visited_at=yesterday_6days.date(),
        # Make sure 'yesterday Student' is enclosed in single quotes
        user__last_name='Current Student'
    )
    yesterday6_student_count = yesterday6_students_visits.count()
    
    # Filter PageVisit objects for visits on the previous day and with last_name 'Current Student'
    yesterday6_staff_visits = PageVisit.objects.filter(
        visited_at=yesterday_6days.date(),
        # Make sure 'yesterday Student' is enclosed in single quotes
        user__last_name='Staff'
    )
    yesterday6_staff_count = yesterday6_staff_visits.count()
    
    # Filter PageVisit objects for visits on the previous day and with last_name 'Current Student'
    yesterday6_alumni_visits = PageVisit.objects.filter(
        visited_at=yesterday_6days.date(),
        # Make sure 'yesterday Student' is enclosed in single quotes
        user__last_name='Alumni'
    )
    yesterday6_alumni_count = yesterday6_alumni_visits.count()
    
    # Filter PageVisit objects for visits on the previous day and with last_name 'Current Student'
    yesterday6_faculty_visits = PageVisit.objects.filter(
        visited_at=yesterday_6days.date(),
        # Make sure 'yesterday Student' is enclosed in single quotes
        user__last_name='Faculty'
    )
    yesterday6_faculty_count = yesterday6_faculty_visits.count()
    
    

     # Filter PageVisit objects for visits on the previous day and with last_name 'Current Student'
    yesterday5_students_visits = PageVisit.objects.filter(
        visited_at=yesterday_5days.date(),
        # Make sure 'yesterday Student' is enclosed in single quotes
        user__last_name='Current Student'
    )
    yesterday5_student_count = yesterday5_students_visits.count()
    
    # Filter PageVisit objects for visits on the previous day and with last_name 'Current Student'
    yesterday5_staff_visits = PageVisit.objects.filter(
        visited_at=yesterday_5days.date(),
        # Make sure 'yesterday Student' is enclosed in single quotes
        user__last_name='Staff'
    )
    yesterday5_staff_count = yesterday5_staff_visits.count()
    
    # Filter PageVisit objects for visits on the previous day and with last_name 'Current Student'
    yesterday5_alumni_visits = PageVisit.objects.filter(
        visited_at=yesterday_5days.date(),
        # Make sure 'yesterday Student' is enclosed in single quotes
        user__last_name='Alumni'
    )
    yesterday5_alumni_count = yesterday5_alumni_visits.count()
    
    # Filter PageVisit objects for visits on the previous day and with last_name 'Current Student'
    yesterday5_faculty_visits = PageVisit.objects.filter(
        visited_at=yesterday_5days.date(),
        # Make sure 'yesterday Student' is enclosed in single quotes
        user__last_name='Faculty'
    )
    yesterday5_faculty_count = yesterday5_faculty_visits.count()

    
    

     # Filter PageVisit objects for visits on the previous day and with last_name 'Current Student'
    yesterday4_students_visits = PageVisit.objects.filter(
        visited_at=yesterday_4days.date(),
        # Make sure 'yesterday Student' is enclosed in single quotes
        user__last_name='Current Student'
    )
    yesterday4_student_count = yesterday4_students_visits.count()
    
    # Filter PageVisit objects for visits on the previous day and with last_name 'Current Student'
    yesterday4_staff_visits = PageVisit.objects.filter(
        visited_at=yesterday_4days.date(),
        # Make sure 'yesterday Student' is enclosed in single quotes
        user__last_name='Staff'
    )
    yesterday4_staff_count = yesterday4_staff_visits.count()
    
    # Filter PageVisit objects for visits on the previous day and with last_name 'Current Student'
    yesterday4_alumni_visits = PageVisit.objects.filter(
        visited_at=yesterday_4days.date(),
        # Make sure 'yesterday Student' is enclosed in single quotes
        user__last_name='Alumni'
    )
    yesterday4_alumni_count = yesterday4_alumni_visits.count()
    
    # Filter PageVisit objects for visits on the previous day and with last_name 'Current Student'
    yesterday4_faculty_visits = PageVisit.objects.filter(
        visited_at=yesterday_4days.date(),
        # Make sure 'yesterday Student' is enclosed in single quotes
        user__last_name='Faculty'
    )
    yesterday4_faculty_count = yesterday4_faculty_visits.count()
    
    

    # Filter PageVisit objects for visits on the previous day and with last_name 'Current Student'
    yesterday3_students_visits = PageVisit.objects.filter(
        visited_at=yesterday_3days.date(),
        # Make sure 'yesterday Student' is enclosed in single quotes
        user__last_name='Current Student'
    )
    yesterday3_student_count = yesterday3_students_visits.count()
    
    # Filter PageVisit objects for visits on the previous day and with last_name 'Current Student'
    yesterday3_staff_visits = PageVisit.objects.filter(
        visited_at=yesterday_3days.date(),
        # Make sure 'yesterday Student' is enclosed in single quotes
        user__last_name='Staff'
    )
    yesterday3_staff_count = yesterday3_staff_visits.count()
    
    # Filter PageVisit objects for visits on the previous day and with last_name 'Current Student'
    yesterday3_alumni_visits = PageVisit.objects.filter(
        visited_at=yesterday_3days.date(),
        # Make sure 'yesterday Student' is enclosed in single quotes
        user__last_name='Alumni'
    )
    yesterday3_alumni_count = yesterday3_alumni_visits.count()
    
    # Filter PageVisit objects for visits on the previous day and with last_name 'Current Student'
    yesterday3_faculty_visits = PageVisit.objects.filter(
        visited_at=yesterday_3days.date(),
        # Make sure 'yesterday Student' is enclosed in single quotes
        user__last_name='Faculty'
    )
    yesterday3_faculty_count = yesterday3_faculty_visits.count()





    # Filter PageVisit objects for visits on the previous day and with last_name 'Current Student'
    yesterday2_students_visits = PageVisit.objects.filter(
        visited_at=yesterday_2days.date(),
        # Make sure 'yesterday Student' is enclosed in single quotes
        user__last_name='Current Student'
    )
    yesterday2_student_count = yesterday2_students_visits.count()
    
    # Filter PageVisit objects for visits on the previous day and with last_name 'Current Student'
    yesterday2_staff_visits = PageVisit.objects.filter(
        visited_at=yesterday_2days.date(),
        # Make sure 'yesterday Student' is enclosed in single quotes
        user__last_name='Staff'
    )
    yesterday2_staff_count = yesterday2_staff_visits.count()
    
    # Filter PageVisit objects for visits on the previous day and with last_name 'Current Student'
    yesterday2_alumni_visits = PageVisit.objects.filter(
        visited_at=yesterday_2days.date(),
        # Make sure 'yesterday Student' is enclosed in single quotes
        user__last_name='Alumni'
    )
    yesterday2_alumni_count = yesterday2_alumni_visits.count()
    
    # Filter PageVisit objects for visits on the previous day and with last_name 'Current Student'
    yesterday2_faculty_visits = PageVisit.objects.filter(
        visited_at=yesterday_2days.date(),
        # Make sure 'yesterday Student' is enclosed in single quotes
        user__last_name='Faculty'
    )
    yesterday2_faculty_count = yesterday2_faculty_visits.count()



    # Filter PageVisit objects for visits on the previous day and with last_name 'Current Student'
    yesterday_students_visits = PageVisit.objects.filter(
        visited_at=yesterday.date(),
        # Make sure 'yesterday Student' is enclosed in single quotes
        user__last_name='Current Student'
    )
    yesterday_student_count = yesterday_students_visits.count()
    
    # Filter PageVisit objects for visits on the previous day and with last_name 'Current Student'
    yesterday_staff_visits = PageVisit.objects.filter(
        visited_at=yesterday.date(),
        # Make sure 'yesterday Student' is enclosed in single quotes
        user__last_name='Staff'
    )
    yesterday_staff_count = yesterday_staff_visits.count()
    
    # Filter PageVisit objects for visits on the previous day and with last_name 'Current Student'
    yesterday_alumni_visits = PageVisit.objects.filter(
        visited_at=yesterday.date(),
        # Make sure 'yesterday Student' is enclosed in single quotes
        user__last_name='Alumni'
    )
    yesterday_alumni_count = yesterday_alumni_visits.count()
    
    # Filter PageVisit objects for visits on the previous day and with last_name 'Current Student'
    yesterday_faculty_visits = PageVisit.objects.filter(
        visited_at=yesterday.date(),
        # Make sure 'yesterday Student' is enclosed in single quotes
        user__last_name='Faculty'
    )
    yesterday_faculty_count = yesterday_faculty_visits.count()
    
    visitors = User.objects.filter(Q(email='') & ~Q(is_superuser=True))
    
    context = {
        'visitors': visitors,
        'yesterday7_student_count':yesterday7_student_count,
        'yesterday7_staff_count':yesterday7_staff_count,
        'yesterday7_alumni_count':yesterday7_alumni_count,
        'yesterday7_faculty_count':yesterday7_faculty_count,
        
        'yesterday6_student_count':yesterday6_student_count,
        'yesterday6_staff_count':yesterday6_staff_count,
        'yesterday6_alumni_count':yesterday6_alumni_count,
        'yesterday6_faculty_count':yesterday6_faculty_count,
        
        'yesterday5_student_count':yesterday5_student_count,
        'yesterday5_staff_count':yesterday5_staff_count,
        'yesterday5_alumni_count':yesterday5_alumni_count,
        'yesterday5_faculty_count':yesterday5_faculty_count,
        
        'yesterday4_student_count':yesterday4_student_count,
        'yesterday4_staff_count':yesterday4_staff_count,
        'yesterday4_alumni_count':yesterday4_alumni_count,
        'yesterday4_faculty_count':yesterday4_faculty_count,
        
        'yesterday3_student_count':yesterday3_student_count,
        'yesterday3_staff_count':yesterday3_staff_count,
        'yesterday3_alumni_count':yesterday3_alumni_count,
        'yesterday3_faculty_count':yesterday3_faculty_count,
        
        'yesterday2_student_count':yesterday2_student_count,
        'yesterday2_staff_count':yesterday2_staff_count,
        'yesterday2_alumni_count':yesterday2_alumni_count,
        'yesterday2_faculty_count':yesterday2_faculty_count,
        
        'yesterday_student_count': yesterday_student_count,
        'yesterday_alumni_count': yesterday_alumni_count,
        'yesterday_faculty_count': yesterday_faculty_count,
        'yesterday_staff_count': yesterday_faculty_count,
        
        'yesterday_all_visits': yesterday_all_visits,
        
        'yesterday': yesterday,
        'yesterday_2days': yesterday_2days,
        'yesterday_3days': yesterday_3days,
        'yesterday_4days': yesterday_4days,
        'yesterday_5days': yesterday_5days,
        'yesterday_6days': yesterday_6days,
        'yesterday_7days': yesterday_7days,
        'yesterday_8days': yesterday_8days,
    }
    return render(request, "admin/graphs-7days.html", context)










def graph_thirtydays(request):
    
    # Assuming you have a User model and PageVisit model defined

    # Filter PageVisit objects for visits in November and associated users with last name 'Current Student'
    novemberVisits_student = PageVisit.objects.filter(
        visited_at__month=11,
        user__last_name='Current Student'
    )

    # Count the number of such PageVisit objects
    studentNovember = novemberVisits_student.count()
    
    
    novemberVisits_faculty = PageVisit.objects.filter(
        visited_at__month=11,
        user__last_name='Faculty'
    )

    # Count the number of such PageVisit objects
    facultyNovember = novemberVisits_faculty.count()
    
    
    novemberVisits_staff = PageVisit.objects.filter(
        visited_at__month=11,
        user__last_name='Staff'
    )

    # Count the number of such PageVisit objects
    staffNovember = novemberVisits_staff.count()
    
    
    novemberVisits_alumni = PageVisit.objects.filter(
        visited_at__month=11,
        user__last_name='Alumni'
    )

    # Count the number of such PageVisit objects
    alumniNovember = novemberVisits_alumni.count()
    
    
    # Filter PageVisit objects for visits in November and associated users with last name 'Current Student'
    decemberVisits_student = PageVisit.objects.filter(
        visited_at__month=12,
        user__last_name='Current Student'
    )

    # Count the number of such PageVisit objects
    studentdecember = decemberVisits_student.count()

    decemberVisits_faculty = PageVisit.objects.filter(
        visited_at__month=12,
        user__last_name='Faculty'
    )

    # Count the number of such PageVisit objects
    facultydecember = decemberVisits_faculty.count()

    decemberVisits_staff = PageVisit.objects.filter(
        visited_at__month=12,
        user__last_name='Staff'
    )

    # Count the number of such PageVisit objects
    staffdecember = decemberVisits_staff.count()

    decemberVisits_alumni = PageVisit.objects.filter(
        visited_at__month=12,
        user__last_name='Alumni'
    )

    # Count the number of such PageVisit objects
    alumnidecember = decemberVisits_alumni.count()
 
    visitors = User.objects.filter(Q(email='') & ~Q(is_superuser=True))
    context = {
        'visitors': visitors,
        'studentNovember': studentNovember,
        'facultyNovember': facultyNovember,
        'staffNovember': staffNovember,
        'alumniNovember': alumniNovember,
        
        'studentdecember': studentdecember,
        'facultydecember': facultydecember,
        'staffdecember': staffdecember,
        'alumnidecember': alumnidecember,
        
    }
    return render(request, 'admin/graphs-30days.html', context)






'''
def graph_thirtydays(request):
    # Calculate the date for yesterday
    yesterday_datetime = timezone.now()
    
    yesterday = yesterday_datetime - timedelta(days=1)
    yesterday_2days = yesterday_datetime - timedelta(days=2)
    yesterday_3days = yesterday_datetime - timedelta(days=3)
    yesterday_4days = yesterday_datetime - timedelta(days=4)
    yesterday_5days = yesterday_datetime - timedelta(days=5)
    yesterday_6days = yesterday_datetime - timedelta(days=6)
    yesterday_7days = yesterday_datetime - timedelta(days=7)
    yesterday_8days = yesterday_datetime - timedelta(days=8)
    yesterday_9days = yesterday_datetime - timedelta(days=9)
    yesterday_10days = yesterday_datetime - timedelta(days=8)
    yesterday_11days = yesterday_datetime - timedelta(days=11)
    yesterday_12days = yesterday_datetime - timedelta(days=12)
    yesterday_13days = yesterday_datetime - timedelta(days=13)
    yesterday_14days = yesterday_datetime - timedelta(days=14)
    yesterday_15days = yesterday_datetime - timedelta(days=15)
    yesterday_16days = yesterday_datetime - timedelta(days=16)
    yesterday_17days = yesterday_datetime - timedelta(days=17)
    yesterday_18days = yesterday_datetime - timedelta(days=18)
    yesterday_19days = yesterday_datetime - timedelta(days=19)
    yesterday_20days = yesterday_datetime - timedelta(days=20)
    yesterday_21days = yesterday_datetime - timedelta(days=21)
    yesterday_22days = yesterday_datetime - timedelta(days=22)
    yesterday_23days = yesterday_datetime - timedelta(days=23)
    yesterday_24days = yesterday_datetime - timedelta(days=24)
    yesterday_25days = yesterday_datetime - timedelta(days=25)
    yesterday_26days = yesterday_datetime - timedelta(days=26)
    yesterday_27days = yesterday_datetime - timedelta(days=27)
    yesterday_28days = yesterday_datetime - timedelta(days=28)
    yesterday_29days = yesterday_datetime - timedelta(days=29)
    yesterday_30days = yesterday_datetime - timedelta(days=30)
    # Filter PageVisit objects for visits on the previous day
    yesterday_all_visits = PageVisit.objects.filter(
        visited_at=yesterday.date()).count()

    
    yesterday30_students_visits = PageVisit.objects.filter(
        visited_at=yesterday_30days.date(),
        # Make sure 'yesterday Student' is enclosed in single quotes
        user__last_name='Current Student'
    )
    yesterday30_student_count = yesterday30_students_visits.count()
    
    # Filter PageVisit objects for visits on the previous day and with last_name 'Current Student'
    yesterday30_staff_visits = PageVisit.objects.filter(
        visited_at=yesterday_30days.date(),
        # Make sure 'yesterday Student' is enclosed in single quotes
        user__last_name='Staff'
    )
    yesterday30_staff_count = yesterday30_staff_visits.count()
    
    # Filter PageVisit objects for visits on the previous day and with last_name 'Current Student'
    yesterday30_alumni_visits = PageVisit.objects.filter(
        visited_at=yesterday_30days.date(),
        # Make sure 'yesterday Student' is enclosed in single quotes
        user__last_name='Alumni'
    )
    yesterday30_alumni_count = yesterday30_alumni_visits.count()
    
    # Filter PageVisit objects for visits on the previous day and with last_name 'Current Student'
    yesterday30_faculty_visits = PageVisit.objects.filter(
        visited_at=yesterday_30days.date(),
        # Make sure 'yesterday Student' is enclosed in single quotes
        user__last_name='Faculty'
    )
    yesterday30_faculty_count = yesterday30_faculty_visits.count()
    
    
    
    
    yesterday29_students_visits = PageVisit.objects.filter(
        visited_at=yesterday_29days.date(),
        # Make sure 'yesterday Student' is enclosed in single quotes
        user__last_name='Current Student'
    )
    yesterday29_student_count = yesterday29_students_visits.count()
    
    # Filter PageVisit objects for visits on the previous day and with last_name 'Current Student'
    yesterday29_staff_visits = PageVisit.objects.filter(
        visited_at=yesterday_29days.date(),
        # Make sure 'yesterday Student' is enclosed in single quotes
        user__last_name='Staff'
    )
    yesterday29_staff_count = yesterday29_staff_visits.count()
    
    # Filter PageVisit objects for visits on the previous day and with last_name 'Current Student'
    yesterday29_alumni_visits = PageVisit.objects.filter(
        visited_at=yesterday_29days.date(),
        # Make sure 'yesterday Student' is enclosed in single quotes
        user__last_name='Alumni'
    )
    yesterday29_alumni_count = yesterday29_alumni_visits.count()
    
    # Filter PageVisit objects for visits on the previous day and with last_name 'Current Student'
    yesterday29_faculty_visits = PageVisit.objects.filter(
        visited_at=yesterday_29days.date(),
        # Make sure 'yesterday Student' is enclosed in single quotes
        user__last_name='Faculty'
    )
    yesterday29_faculty_count = yesterday29_faculty_visits.count()
    
    
    
    
    yesterday28_students_visits = PageVisit.objects.filter(
        visited_at=yesterday_28days.date(),
        # Make sure 'yesterday Student' is enclosed in single quotes
        user__last_name='Current Student'
    )
    yesterday28_student_count = yesterday28_students_visits.count()
    
    # Filter PageVisit objects for visits on the previous day and with last_name 'Current Student'
    yesterday28_staff_visits = PageVisit.objects.filter(
        visited_at=yesterday_28days.date(),
        # Make sure 'yesterday Student' is enclosed in single quotes
        user__last_name='Staff'
    )
    yesterday28_staff_count = yesterday28_staff_visits.count()
    
    # Filter PageVisit objects for visits on the previous day and with last_name 'Current Student'
    yesterday28_alumni_visits = PageVisit.objects.filter(
        visited_at=yesterday_28days.date(),
        # Make sure 'yesterday Student' is enclosed in single quotes
        user__last_name='Alumni'
    )
    yesterday28_alumni_count = yesterday28_alumni_visits.count()
    
    # Filter PageVisit objects for visits on the previous day and with last_name 'Current Student'
    yesterday28_faculty_visits = PageVisit.objects.filter(
        visited_at=yesterday_28days.date(),
        # Make sure 'yesterday Student' is enclosed in single quotes
        user__last_name='Faculty'
    )
    yesterday28_faculty_count = yesterday28_faculty_visits.count()
    
    
    yesterday27_students_visits = PageVisit.objects.filter(
        visited_at=yesterday_27days.date(),
        # Make sure 'yesterday Student' is enclosed in single quotes
        user__last_name='Current Student'
    )
    yesterday27_student_count = yesterday27_students_visits.count()
    
    # Filter PageVisit objects for visits on the previous day and with last_name 'Current Student'
    yesterday27_staff_visits = PageVisit.objects.filter(
        visited_at=yesterday_27days.date(),
        # Make sure 'yesterday Student' is enclosed in single quotes
        user__last_name='Staff'
    )
    yesterday27_staff_count = yesterday27_staff_visits.count()
    
    # Filter PageVisit objects for visits on the previous day and with last_name 'Current Student'
    yesterday27_alumni_visits = PageVisit.objects.filter(
        visited_at=yesterday_27days.date(),
        # Make sure 'yesterday Student' is enclosed in single quotes
        user__last_name='Alumni'
    )
    yesterday27_alumni_count = yesterday27_alumni_visits.count()
    
    # Filter PageVisit objects for visits on the previous day and with last_name 'Current Student'
    yesterday27_faculty_visits = PageVisit.objects.filter(
        visited_at=yesterday_27days.date(),
        # Make sure 'yesterday Student' is enclosed in single quotes
        user__last_name='Faculty'
    )
    yesterday27_faculty_count = yesterday27_faculty_visits.count()
    
    
    
    
    
    yesterday26_students_visits = PageVisit.objects.filter(
        visited_at=yesterday_26days.date(),
        # Make sure 'yesterday Student' is enclosed in single quotes
        user__last_name='Current Student'
    )
    yesterday26_student_count = yesterday26_students_visits.count()
    
    # Filter PageVisit objects for visits on the previous day and with last_name 'Current Student'
    yesterday26_staff_visits = PageVisit.objects.filter(
        visited_at=yesterday_26days.date(),
        # Make sure 'yesterday Student' is enclosed in single quotes
        user__last_name='Staff'
    )
    yesterday26_staff_count = yesterday26_staff_visits.count()
    
    # Filter PageVisit objects for visits on the previous day and with last_name 'Current Student'
    yesterday26_alumni_visits = PageVisit.objects.filter(
        visited_at=yesterday_26days.date(),
        # Make sure 'yesterday Student' is enclosed in single quotes
        user__last_name='Alumni'
    )
    yesterday26_alumni_count = yesterday26_alumni_visits.count()
    
    # Filter PageVisit objects for visits on the previous day and with last_name 'Current Student'
    yesterday26_faculty_visits = PageVisit.objects.filter(
        visited_at=yesterday_26days.date(),
        # Make sure 'yesterday Student' is enclosed in single quotes
        user__last_name='Faculty'
    )
    yesterday26_faculty_count = yesterday26_faculty_visits.count()
    
    
    
    
    yesterday25_students_visits = PageVisit.objects.filter(
        visited_at=yesterday_25days.date(),
        # Make sure 'yesterday Student' is enclosed in single quotes
        user__last_name='Current Student'
    )
    yesterday25_student_count = yesterday25_students_visits.count()
    
    # Filter PageVisit objects for visits on the previous day and with last_name 'Current Student'
    yesterday25_staff_visits = PageVisit.objects.filter(
        visited_at=yesterday_25days.date(),
        # Make sure 'yesterday Student' is enclosed in single quotes
        user__last_name='Staff'
    )
    yesterday25_staff_count = yesterday25_staff_visits.count()
    
    # Filter PageVisit objects for visits on the previous day and with last_name 'Current Student'
    yesterday25_alumni_visits = PageVisit.objects.filter(
        visited_at=yesterday_25days.date(),
        # Make sure 'yesterday Student' is enclosed in single quotes
        user__last_name='Alumni'
    )
    yesterday25_alumni_count = yesterday25_alumni_visits.count()
    
    # Filter PageVisit objects for visits on the previous day and with last_name 'Current Student'
    yesterday25_faculty_visits = PageVisit.objects.filter(
        visited_at=yesterday_25days.date(),
        # Make sure 'yesterday Student' is enclosed in single quotes
        user__last_name='Faculty'
    )
    yesterday25_faculty_count = yesterday25_faculty_visits.count()
    
    
    
    
    yesterday24_students_visits = PageVisit.objects.filter(
        visited_at=yesterday_24days.date(),
        # Make sure 'yesterday Student' is enclosed in single quotes
        user__last_name='Current Student'
    )
    yesterday24_student_count = yesterday24_students_visits.count()
    
    # Filter PageVisit objects for visits on the previous day and with last_name 'Current Student'
    yesterday24_staff_visits = PageVisit.objects.filter(
        visited_at=yesterday_24days.date(),
        # Make sure 'yesterday Student' is enclosed in single quotes
        user__last_name='Staff'
    )
    yesterday24_staff_count = yesterday24_staff_visits.count()
    
    # Filter PageVisit objects for visits on the previous day and with last_name 'Current Student'
    yesterday24_alumni_visits = PageVisit.objects.filter(
        visited_at=yesterday_24days.date(),
        # Make sure 'yesterday Student' is enclosed in single quotes
        user__last_name='Alumni'
    )
    yesterday24_alumni_count = yesterday24_alumni_visits.count()
    
    # Filter PageVisit objects for visits on the previous day and with last_name 'Current Student'
    yesterday24_faculty_visits = PageVisit.objects.filter(
        visited_at=yesterday_24days.date(),
        # Make sure 'yesterday Student' is enclosed in single quotes
        user__last_name='Faculty'
    )
    yesterday24_faculty_count = yesterday24_faculty_visits.count()
    
    
    
    
    yesterday23_students_visits = PageVisit.objects.filter(
        visited_at=yesterday_23days.date(),
        # Make sure 'yesterday Student' is enclosed in single quotes
        user__last_name='Current Student'
    )
    yesterday23_student_count = yesterday23_students_visits.count()
    
    # Filter PageVisit objects for visits on the previous day and with last_name 'Current Student'
    yesterday23_staff_visits = PageVisit.objects.filter(
        visited_at=yesterday_23days.date(),
        # Make sure 'yesterday Student' is enclosed in single quotes
        user__last_name='Staff'
    )
    yesterday23_staff_count = yesterday23_staff_visits.count()
    
    # Filter PageVisit objects for visits on the previous day and with last_name 'Current Student'
    yesterday23_alumni_visits = PageVisit.objects.filter(
        visited_at=yesterday_23days.date(),
        # Make sure 'yesterday Student' is enclosed in single quotes
        user__last_name='Alumni'
    )
    yesterday23_alumni_count = yesterday23_alumni_visits.count()
    
    # Filter PageVisit objects for visits on the previous day and with last_name 'Current Student'
    yesterday23_faculty_visits = PageVisit.objects.filter(
        visited_at=yesterday_23days.date(),
        # Make sure 'yesterday Student' is enclosed in single quotes
        user__last_name='Faculty'
    )
    yesterday23_faculty_count = yesterday23_faculty_visits.count()
    
    
    
    
    yesterday22_students_visits = PageVisit.objects.filter(
        visited_at=yesterday_22days.date(),
        # Make sure 'yesterday Student' is enclosed in single quotes
        user__last_name='Current Student'
    )
    yesterday22_student_count = yesterday22_students_visits.count()
    
    # Filter PageVisit objects for visits on the previous day and with last_name 'Current Student'
    yesterday22_staff_visits = PageVisit.objects.filter(
        visited_at=yesterday_22days.date(),
        # Make sure 'yesterday Student' is enclosed in single quotes
        user__last_name='Staff'
    )
    yesterday22_staff_count = yesterday22_staff_visits.count()
    
    # Filter PageVisit objects for visits on the previous day and with last_name 'Current Student'
    yesterday22_alumni_visits = PageVisit.objects.filter(
        visited_at=yesterday_22days.date(),
        # Make sure 'yesterday Student' is enclosed in single quotes
        user__last_name='Alumni'
    )
    yesterday22_alumni_count = yesterday22_alumni_visits.count()
    
    # Filter PageVisit objects for visits on the previous day and with last_name 'Current Student'
    yesterday22_faculty_visits = PageVisit.objects.filter(
        visited_at=yesterday_22days.date(),
        # Make sure 'yesterday Student' is enclosed in single quotes
        user__last_name='Faculty'
    )
    yesterday22_faculty_count = yesterday22_faculty_visits.count()
    
    
    
    

    yesterday21_students_visits = PageVisit.objects.filter(
        visited_at=yesterday_21days.date(),
        # Make sure 'yesterday Student' is enclosed in single quotes
        user__last_name='Current Student'
    )
    yesterday21_student_count = yesterday21_students_visits.count()
    
    # Filter PageVisit objects for visits on the previous day and with last_name 'Current Student'
    yesterday21_staff_visits = PageVisit.objects.filter(
        visited_at=yesterday_21days.date(),
        # Make sure 'yesterday Student' is enclosed in single quotes
        user__last_name='Staff'
    )
    yesterday21_staff_count = yesterday21_staff_visits.count()
    
    # Filter PageVisit objects for visits on the previous day and with last_name 'Current Student'
    yesterday21_alumni_visits = PageVisit.objects.filter(
        visited_at=yesterday_21days.date(),
        # Make sure 'yesterday Student' is enclosed in single quotes
        user__last_name='Alumni'
    )
    yesterday21_alumni_count = yesterday21_alumni_visits.count()
    
    # Filter PageVisit objects for visits on the previous day and with last_name 'Current Student'
    yesterday15_faculty_visits = PageVisit.objects.filter(
        visited_at=yesterday_15days.date(),
        # Make sure 'yesterday Student' is enclosed in single quotes
        user__last_name='Faculty'
    )
    yesterday15_faculty_count = yesterday15_faculty_visits.count()
    
    
    
    yesterday20_students_visits = PageVisit.objects.filter(
        visited_at=yesterday_20days.date(),
        # Make sure 'yesterday Student' is enclosed in single quotes
        user__last_name='Current Student'
    )
    yesterday20_student_count = yesterday20_students_visits.count()
    
    # Filter PageVisit objects for visits on the previous day and with last_name 'Current Student'
    yesterday20_staff_visits = PageVisit.objects.filter(
        visited_at=yesterday_20days.date(),
        # Make sure 'yesterday Student' is enclosed in single quotes
        user__last_name='Staff'
    )
    yesterday20_staff_count = yesterday20_staff_visits.count()
    
    # Filter PageVisit objects for visits on the previous day and with last_name 'Current Student'
    yesterday20_alumni_visits = PageVisit.objects.filter(
        visited_at=yesterday_20days.date(),
        # Make sure 'yesterday Student' is enclosed in single quotes
        user__last_name='Alumni'
    )
    yesterday20_alumni_count = yesterday20_alumni_visits.count()
    
    # Filter PageVisit objects for visits on the previous day and with last_name 'Current Student'
    yesterday20_faculty_visits = PageVisit.objects.filter(
        visited_at=yesterday_20days.date(),
        # Make sure 'yesterday Student' is enclosed in single quotes
        user__last_name='Faculty'
    )
    yesterday20_faculty_count = yesterday20_faculty_visits.count()
    
    
    
    
    yesterday19_students_visits = PageVisit.objects.filter(
        visited_at=yesterday_19days.date(),
        # Make sure 'yesterday Student' is enclosed in single quotes
        user__last_name='Current Student'
    )
    yesterday19_student_count = yesterday19_students_visits.count()
    
    # Filter PageVisit objects for visits on the previous day and with last_name 'Current Student'
    yesterday19_staff_visits = PageVisit.objects.filter(
        visited_at=yesterday_19days.date(),
        # Make sure 'yesterday Student' is enclosed in single quotes
        user__last_name='Staff'
    )
    yesterday19_staff_count = yesterday19_staff_visits.count()
    
    # Filter PageVisit objects for visits on the previous day and with last_name 'Current Student'
    yesterday19_alumni_visits = PageVisit.objects.filter(
        visited_at=yesterday_19days.date(),
        # Make sure 'yesterday Student' is enclosed in single quotes
        user__last_name='Alumni'
    )
    yesterday19_alumni_count = yesterday19_alumni_visits.count()
    
    # Filter PageVisit objects for visits on the previous day and with last_name 'Current Student'
    yesterday19_faculty_visits = PageVisit.objects.filter(
        visited_at=yesterday_19days.date(),
        # Make sure 'yesterday Student' is enclosed in single quotes
        user__last_name='Faculty'
    )
    yesterday19_faculty_count = yesterday19_faculty_visits.count()
    
    
    yesterday18_students_visits = PageVisit.objects.filter(
        visited_at=yesterday_18days.date(),
        # Make sure 'yesterday Student' is enclosed in single quotes
        user__last_name='Current Student'
    )
    yesterday18_student_count = yesterday18_students_visits.count()
    
    # Filter PageVisit objects for visits on the previous day and with last_name 'Current Student'
    yesterday18_staff_visits = PageVisit.objects.filter(
        visited_at=yesterday_18days.date(),
        # Make sure 'yesterday Student' is enclosed in single quotes
        user__last_name='Staff'
    )
    yesterday18_staff_count = yesterday18_staff_visits.count()
    
    # Filter PageVisit objects for visits on the previous day and with last_name 'Current Student'
    yesterday18_alumni_visits = PageVisit.objects.filter(
        visited_at=yesterday_18days.date(),
        # Make sure 'yesterday Student' is enclosed in single quotes
        user__last_name='Alumni'
    )
    yesterday18_alumni_count = yesterday18_alumni_visits.count()
    
    # Filter PageVisit objects for visits on the previous day and with last_name 'Current Student'
    yesterday18_faculty_visits = PageVisit.objects.filter(
        visited_at=yesterday_18days.date(),
        # Make sure 'yesterday Student' is enclosed in single quotes
        user__last_name='Faculty'
    )
    yesterday18_faculty_count = yesterday18_faculty_visits.count()
    
    
    
    
    yesterday17_students_visits = PageVisit.objects.filter(
        visited_at=yesterday_17days.date(),
        # Make sure 'yesterday Student' is enclosed in single quotes
        user__last_name='Current Student'
    )
    yesterday17_student_count = yesterday17_students_visits.count()
    
    # Filter PageVisit objects for visits on the previous day and with last_name 'Current Student'
    yesterday17_staff_visits = PageVisit.objects.filter(
        visited_at=yesterday_17days.date(),
        # Make sure 'yesterday Student' is enclosed in single quotes
        user__last_name='Staff'
    )
    yesterday17_staff_count = yesterday17_staff_visits.count()
    
    # Filter PageVisit objects for visits on the previous day and with last_name 'Current Student'
    yesterday17_alumni_visits = PageVisit.objects.filter(
        visited_at=yesterday_17days.date(),
        # Make sure 'yesterday Student' is enclosed in single quotes
        user__last_name='Alumni'
    )
    yesterday17_alumni_count = yesterday17_alumni_visits.count()
    
    # Filter PageVisit objects for visits on the previous day and with last_name 'Current Student'
    yesterday17_faculty_visits = PageVisit.objects.filter(
        visited_at=yesterday_17days.date(),
        # Make sure 'yesterday Student' is enclosed in single quotes
        user__last_name='Faculty'
    )
    yesterday17_faculty_count = yesterday17_faculty_visits.count()
    
    
    
    
    yesterday16_students_visits = PageVisit.objects.filter(
        visited_at=yesterday_16days.date(),
        # Make sure 'yesterday Student' is enclosed in single quotes
        user__last_name='Current Student'
    )
    yesterday16_student_count = yesterday16_students_visits.count()
    
    # Filter PageVisit objects for visits on the previous day and with last_name 'Current Student'
    yesterday16_staff_visits = PageVisit.objects.filter(
        visited_at=yesterday_16days.date(),
        # Make sure 'yesterday Student' is enclosed in single quotes
        user__last_name='Staff'
    )
    yesterday16_staff_count = yesterday16_staff_visits.count()
    
    # Filter PageVisit objects for visits on the previous day and with last_name 'Current Student'
    yesterday16_alumni_visits = PageVisit.objects.filter(
        visited_at=yesterday_16days.date(),
        # Make sure 'yesterday Student' is enclosed in single quotes
        user__last_name='Alumni'
    )
    yesterday16_alumni_count = yesterday16_alumni_visits.count()
    
    # Filter PageVisit objects for visits on the previous day and with last_name 'Current Student'
    yesterday16_faculty_visits = PageVisit.objects.filter(
        visited_at=yesterday_16days.date(),
        # Make sure 'yesterday Student' is enclosed in single quotes
        user__last_name='Faculty'
    )
    yesterday16_faculty_count = yesterday16_faculty_visits.count()
    
    
    
    yesterday15_students_visits = PageVisit.objects.filter(
        visited_at=yesterday_15days.date(),
        # Make sure 'yesterday Student' is enclosed in single quotes
        user__last_name='Current Student'
    )
    yesterday15_student_count = yesterday15_students_visits.count()
    
    # Filter PageVisit objects for visits on the previous day and with last_name 'Current Student'
    yesterday15_staff_visits = PageVisit.objects.filter(
        visited_at=yesterday_15days.date(),
        # Make sure 'yesterday Student' is enclosed in single quotes
        user__last_name='Staff'
    )
    yesterday15_staff_count = yesterday15_staff_visits.count()
    
    # Filter PageVisit objects for visits on the previous day and with last_name 'Current Student'
    yesterday15_alumni_visits = PageVisit.objects.filter(
        visited_at=yesterday_15days.date(),
        # Make sure 'yesterday Student' is enclosed in single quotes
        user__last_name='Alumni'
    )
    yesterday15_alumni_count = yesterday15_alumni_visits.count()
    
    # Filter PageVisit objects for visits on the previous day and with last_name 'Current Student'
    yesterday15_faculty_visits = PageVisit.objects.filter(
        visited_at=yesterday_15days.date(),
        # Make sure 'yesterday Student' is enclosed in single quotes
        user__last_name='Faculty'
    )
    yesterday15_faculty_count = yesterday15_faculty_visits.count()
    
    

    
    yesterday14_students_visits = PageVisit.objects.filter(
        visited_at=yesterday_14days.date(),
        # Make sure 'yesterday Student' is enclosed in single quotes
        user__last_name='Current Student'
    )
    yesterday14_student_count = yesterday14_students_visits.count()
    
    # Filter PageVisit objects for visits on the previous day and with last_name 'Current Student'
    yesterday14_staff_visits = PageVisit.objects.filter(
        visited_at=yesterday_14days.date(),
        # Make sure 'yesterday Student' is enclosed in single quotes
        user__last_name='Staff'
    )
    yesterday14_staff_count = yesterday14_staff_visits.count()
    
    # Filter PageVisit objects for visits on the previous day and with last_name 'Current Student'
    yesterday14_alumni_visits = PageVisit.objects.filter(
        visited_at=yesterday_14days.date(),
        # Make sure 'yesterday Student' is enclosed in single quotes
        user__last_name='Alumni'
    )
    yesterday14_alumni_count = yesterday14_alumni_visits.count()
    
    # Filter PageVisit objects for visits on the previous day and with last_name 'Current Student'
    yesterday14_faculty_visits = PageVisit.objects.filter(
        visited_at=yesterday_14days.date(),
        # Make sure 'yesterday Student' is enclosed in single quotes
        user__last_name='Faculty'
    )
    yesterday14_faculty_count = yesterday14_faculty_visits.count()
    
    
    
    yesterday13_students_visits = PageVisit.objects.filter(
        visited_at=yesterday_13days.date(),
        # Make sure 'yesterday Student' is enclosed in single quotes
        user__last_name='Current Student'
    )
    yesterday13_student_count = yesterday13_students_visits.count()
    
    # Filter PageVisit objects for visits on the previous day and with last_name 'Current Student'
    yesterday13_staff_visits = PageVisit.objects.filter(
        visited_at=yesterday_13days.date(),
        # Make sure 'yesterday Student' is enclosed in single quotes
        user__last_name='Staff'
    )
    yesterday13_staff_count = yesterday13_staff_visits.count()
    
    # Filter PageVisit objects for visits on the previous day and with last_name 'Current Student'
    yesterday13_alumni_visits = PageVisit.objects.filter(
        visited_at=yesterday_13days.date(),
        # Make sure 'yesterday Student' is enclosed in single quotes
        user__last_name='Alumni'
    )
    yesterday13_alumni_count = yesterday13_alumni_visits.count()
    
    # Filter PageVisit objects for visits on the previous day and with last_name 'Current Student'
    yesterday13_faculty_visits = PageVisit.objects.filter(
        visited_at=yesterday_13days.date(),
        # Make sure 'yesterday Student' is enclosed in single quotes
        user__last_name='Faculty'
    )
    yesterday13_faculty_count = yesterday13_faculty_visits.count()
    
    
    
    yesterday12_students_visits = PageVisit.objects.filter(
        visited_at=yesterday_12days.date(),
        # Make sure 'yesterday Student' is enclosed in single quotes
        user__last_name='Current Student'
    )
    yesterday12_student_count = yesterday12_students_visits.count()
    
    # Filter PageVisit objects for visits on the previous day and with last_name 'Current Student'
    yesterday12_staff_visits = PageVisit.objects.filter(
        visited_at=yesterday_12days.date(),
        # Make sure 'yesterday Student' is enclosed in single quotes
        user__last_name='Staff'
    )
    yesterday12_staff_count = yesterday12_staff_visits.count()
    
    # Filter PageVisit objects for visits on the previous day and with last_name 'Current Student'
    yesterday12_alumni_visits = PageVisit.objects.filter(
        visited_at=yesterday_12days.date(),
        # Make sure 'yesterday Student' is enclosed in single quotes
        user__last_name='Alumni'
    )
    yesterday12_alumni_count = yesterday12_alumni_visits.count()
    
    # Filter PageVisit objects for visits on the previous day and with last_name 'Current Student'
    yesterday12_faculty_visits = PageVisit.objects.filter(
        visited_at=yesterday_12days.date(),
        # Make sure 'yesterday Student' is enclosed in single quotes
        user__last_name='Faculty'
    )
    yesterday12_faculty_count = yesterday12_faculty_visits.count()
    
    
    
    yesterday11_students_visits = PageVisit.objects.filter(
        visited_at=yesterday_11days.date(),
        # Make sure 'yesterday Student' is enclosed in single quotes
        user__last_name='Current Student'
    )
    yesterday11_student_count = yesterday11_students_visits.count()
    
    # Filter PageVisit objects for visits on the previous day and with last_name 'Current Student'
    yesterday11_staff_visits = PageVisit.objects.filter(
        visited_at=yesterday_11days.date(),
        # Make sure 'yesterday Student' is enclosed in single quotes
        user__last_name='Staff'
    )
    yesterday11_staff_count = yesterday11_staff_visits.count()
    
    # Filter PageVisit objects for visits on the previous day and with last_name 'Current Student'
    yesterday11_alumni_visits = PageVisit.objects.filter(
        visited_at=yesterday_11days.date(),
        # Make sure 'yesterday Student' is enclosed in single quotes
        user__last_name='Alumni'
    )
    yesterday11_alumni_count = yesterday11_alumni_visits.count()
    
    # Filter PageVisit objects for visits on the previous day and with last_name 'Current Student'
    yesterday11_faculty_visits = PageVisit.objects.filter(
        visited_at=yesterday_11days.date(),
        # Make sure 'yesterday Student' is enclosed in single quotes
        user__last_name='Faculty'
    )
    yesterday11_faculty_count = yesterday11_faculty_visits.count()
    
    
    
    
    yesterday10_students_visits = PageVisit.objects.filter(
        visited_at=yesterday_10days.date(),
        # Make sure 'yesterday Student' is enclosed in single quotes
        user__last_name='Current Student'
    )
    yesterday10_student_count = yesterday10_students_visits.count()
    
    # Filter PageVisit objects for visits on the previous day and with last_name 'Current Student'
    yesterday10_staff_visits = PageVisit.objects.filter(
        visited_at=yesterday_10days.date(),
        # Make sure 'yesterday Student' is enclosed in single quotes
        user__last_name='Staff'
    )
    yesterday10_staff_count = yesterday10_staff_visits.count()
    
    # Filter PageVisit objects for visits on the previous day and with last_name 'Current Student'
    yesterday10_alumni_visits = PageVisit.objects.filter(
        visited_at=yesterday_10days.date(),
        # Make sure 'yesterday Student' is enclosed in single quotes
        user__last_name='Alumni'
    )
    yesterday10_alumni_count = yesterday10_alumni_visits.count()
    
    # Filter PageVisit objects for visits on the previous day and with last_name 'Current Student'
    yesterday10_faculty_visits = PageVisit.objects.filter(
        visited_at=yesterday_10days.date(),
        # Make sure 'yesterday Student' is enclosed in single quotes
        user__last_name='Faculty'
    )
    yesterday10_faculty_count = yesterday10_faculty_visits.count()






    yesterday9_students_visits = PageVisit.objects.filter(
        visited_at=yesterday_9days.date(),
        # Make sure 'yesterday Student' is enclosed in single quotes
        user__last_name='Current Student'
    )
    yesterday9_student_count = yesterday9_students_visits.count()
    
    # Filter PageVisit objects for visits on the previous day and with last_name 'Current Student'
    yesterday9_staff_visits = PageVisit.objects.filter(
        visited_at=yesterday_9days.date(),
        # Make sure 'yesterday Student' is enclosed in single quotes
        user__last_name='Staff'
    )
    yesterday9_staff_count = yesterday9_staff_visits.count()
    
    # Filter PageVisit objects for visits on the previous day and with last_name 'Current Student'
    yesterday9_alumni_visits = PageVisit.objects.filter(
        visited_at=yesterday_9days.date(),
        # Make sure 'yesterday Student' is enclosed in single quotes
        user__last_name='Alumni'
    )
    yesterday9_alumni_count = yesterday9_alumni_visits.count()
    
    # Filter PageVisit objects for visits on the previous day and with last_name 'Current Student'
    yesterday9_faculty_visits = PageVisit.objects.filter(
        visited_at=yesterday_9days.date(),
        # Make sure 'yesterday Student' is enclosed in single quotes
        user__last_name='Faculty'
    )
    yesterday9_faculty_count = yesterday9_faculty_visits.count()
    

    yesterday8_students_visits = PageVisit.objects.filter(
        visited_at=yesterday_8days.date(),
        # Make sure 'yesterday Student' is enclosed in single quotes
        user__last_name='Current Student'
    )
    yesterday8_student_count = yesterday8_students_visits.count()
    
    # Filter PageVisit objects for visits on the previous day and with last_name 'Current Student'
    yesterday8_staff_visits = PageVisit.objects.filter(
        visited_at=yesterday_8days.date(),
        # Make sure 'yesterday Student' is enclosed in single quotes
        user__last_name='Staff'
    )
    yesterday8_staff_count = yesterday8_staff_visits.count()
    
    # Filter PageVisit objects for visits on the previous day and with last_name 'Current Student'
    yesterday8_alumni_visits = PageVisit.objects.filter(
        visited_at=yesterday_8days.date(),
        # Make sure 'yesterday Student' is enclosed in single quotes
        user__last_name='Alumni'
    )
    yesterday8_alumni_count = yesterday8_alumni_visits.count()
    
    # Filter PageVisit objects for visits on the previous day and with last_name 'Current Student'
    yesterday8_faculty_visits = PageVisit.objects.filter(
        visited_at=yesterday_8days.date(),
        # Make sure 'yesterday Student' is enclosed in single quotes
        user__last_name='Faculty'
    )
    yesterday8_faculty_count = yesterday8_faculty_visits.count()



    # Filter PageVisit objects for visits on the previous day and with last_name 'Current Student'
    yesterday7_students_visits = PageVisit.objects.filter(
        visited_at=yesterday_7days.date(),
        # Make sure 'yesterday Student' is enclosed in single quotes
        user__last_name='Current Student'
    )
    yesterday7_student_count = yesterday7_students_visits.count()
    
    # Filter PageVisit objects for visits on the previous day and with last_name 'Current Student'
    yesterday7_staff_visits = PageVisit.objects.filter(
        visited_at=yesterday_7days.date(),
        # Make sure 'yesterday Student' is enclosed in single quotes
        user__last_name='Staff'
    )
    yesterday7_staff_count = yesterday7_staff_visits.count()
    
    # Filter PageVisit objects for visits on the previous day and with last_name 'Current Student'
    yesterday7_alumni_visits = PageVisit.objects.filter(
        visited_at=yesterday_7days.date(),
        # Make sure 'yesterday Student' is enclosed in single quotes
        user__last_name='Alumni'
    )
    yesterday7_alumni_count = yesterday7_alumni_visits.count()
    
    # Filter PageVisit objects for visits on the previous day and with last_name 'Current Student'
    yesterday7_faculty_visits = PageVisit.objects.filter(
        visited_at=yesterday_7days.date(),
        # Make sure 'yesterday Student' is enclosed in single quotes
        user__last_name='Faculty'
    )
    yesterday7_faculty_count = yesterday7_faculty_visits.count()

    
    # Filter PageVisit objects for visits on the previous day and with last_name 'Current Student'
    yesterday6_students_visits = PageVisit.objects.filter(
        visited_at=yesterday_6days.date(),
        # Make sure 'yesterday Student' is enclosed in single quotes
        user__last_name='Current Student'
    )
    yesterday6_student_count = yesterday6_students_visits.count()
    
    # Filter PageVisit objects for visits on the previous day and with last_name 'Current Student'
    yesterday6_staff_visits = PageVisit.objects.filter(
        visited_at=yesterday_6days.date(),
        # Make sure 'yesterday Student' is enclosed in single quotes
        user__last_name='Staff'
    )
    yesterday6_staff_count = yesterday6_staff_visits.count()
    
    # Filter PageVisit objects for visits on the previous day and with last_name 'Current Student'
    yesterday6_alumni_visits = PageVisit.objects.filter(
        visited_at=yesterday_6days.date(),
        # Make sure 'yesterday Student' is enclosed in single quotes
        user__last_name='Alumni'
    )
    yesterday6_alumni_count = yesterday6_alumni_visits.count()
    
    # Filter PageVisit objects for visits on the previous day and with last_name 'Current Student'
    yesterday6_faculty_visits = PageVisit.objects.filter(
        visited_at=yesterday_6days.date(),
        # Make sure 'yesterday Student' is enclosed in single quotes
        user__last_name='Faculty'
    )
    yesterday6_faculty_count = yesterday6_faculty_visits.count()
    
    

     # Filter PageVisit objects for visits on the previous day and with last_name 'Current Student'
    yesterday5_students_visits = PageVisit.objects.filter(
        visited_at=yesterday_5days.date(),
        # Make sure 'yesterday Student' is enclosed in single quotes
        user__last_name='Current Student'
    )
    yesterday5_student_count = yesterday5_students_visits.count()
    
    # Filter PageVisit objects for visits on the previous day and with last_name 'Current Student'
    yesterday5_staff_visits = PageVisit.objects.filter(
        visited_at=yesterday_5days.date(),
        # Make sure 'yesterday Student' is enclosed in single quotes
        user__last_name='Staff'
    )
    yesterday5_staff_count = yesterday5_staff_visits.count()
    
    # Filter PageVisit objects for visits on the previous day and with last_name 'Current Student'
    yesterday5_alumni_visits = PageVisit.objects.filter(
        visited_at=yesterday_5days.date(),
        # Make sure 'yesterday Student' is enclosed in single quotes
        user__last_name='Alumni'
    )
    yesterday5_alumni_count = yesterday5_alumni_visits.count()
    
    # Filter PageVisit objects for visits on the previous day and with last_name 'Current Student'
    yesterday5_faculty_visits = PageVisit.objects.filter(
        visited_at=yesterday_5days.date(),
        # Make sure 'yesterday Student' is enclosed in single quotes
        user__last_name='Faculty'
    )
    yesterday5_faculty_count = yesterday5_faculty_visits.count()

    
    

     # Filter PageVisit objects for visits on the previous day and with last_name 'Current Student'
    yesterday4_students_visits = PageVisit.objects.filter(
        visited_at=yesterday_4days.date(),
        # Make sure 'yesterday Student' is enclosed in single quotes
        user__last_name='Current Student'
    )
    yesterday4_student_count = yesterday4_students_visits.count()
    
    # Filter PageVisit objects for visits on the previous day and with last_name 'Current Student'
    yesterday4_staff_visits = PageVisit.objects.filter(
        visited_at=yesterday_4days.date(),
        # Make sure 'yesterday Student' is enclosed in single quotes
        user__last_name='Staff'
    )
    yesterday4_staff_count = yesterday4_staff_visits.count()
    
    # Filter PageVisit objects for visits on the previous day and with last_name 'Current Student'
    yesterday4_alumni_visits = PageVisit.objects.filter(
        visited_at=yesterday_4days.date(),
        # Make sure 'yesterday Student' is enclosed in single quotes
        user__last_name='Alumni'
    )
    yesterday4_alumni_count = yesterday4_alumni_visits.count()
    
    # Filter PageVisit objects for visits on the previous day and with last_name 'Current Student'
    yesterday4_faculty_visits = PageVisit.objects.filter(
        visited_at=yesterday_4days.date(),
        # Make sure 'yesterday Student' is enclosed in single quotes
        user__last_name='Faculty'
    )
    yesterday4_faculty_count = yesterday4_faculty_visits.count()
    
    

    # Filter PageVisit objects for visits on the previous day and with last_name 'Current Student'
    yesterday3_students_visits = PageVisit.objects.filter(
        visited_at=yesterday_3days.date(),
        # Make sure 'yesterday Student' is enclosed in single quotes
        user__last_name='Current Student'
    )
    yesterday3_student_count = yesterday3_students_visits.count()
    
    # Filter PageVisit objects for visits on the previous day and with last_name 'Current Student'
    yesterday3_staff_visits = PageVisit.objects.filter(
        visited_at=yesterday_3days.date(),
        # Make sure 'yesterday Student' is enclosed in single quotes
        user__last_name='Staff'
    )
    yesterday3_staff_count = yesterday3_staff_visits.count()
    
    # Filter PageVisit objects for visits on the previous day and with last_name 'Current Student'
    yesterday3_alumni_visits = PageVisit.objects.filter(
        visited_at=yesterday_3days.date(),
        # Make sure 'yesterday Student' is enclosed in single quotes
        user__last_name='Alumni'
    )
    yesterday3_alumni_count = yesterday3_alumni_visits.count()
    
    # Filter PageVisit objects for visits on the previous day and with last_name 'Current Student'
    yesterday3_faculty_visits = PageVisit.objects.filter(
        visited_at=yesterday_3days.date(),
        # Make sure 'yesterday Student' is enclosed in single quotes
        user__last_name='Faculty'
    )
    yesterday3_faculty_count = yesterday3_faculty_visits.count()





    # Filter PageVisit objects for visits on the previous day and with last_name 'Current Student'
    yesterday2_students_visits = PageVisit.objects.filter(
        visited_at=yesterday_2days.date(),
        # Make sure 'yesterday Student' is enclosed in single quotes
        user__last_name='Current Student'
    )
    yesterday2_student_count = yesterday2_students_visits.count()
    
    # Filter PageVisit objects for visits on the previous day and with last_name 'Current Student'
    yesterday2_staff_visits = PageVisit.objects.filter(
        visited_at=yesterday_2days.date(),
        # Make sure 'yesterday Student' is enclosed in single quotes
        user__last_name='Staff'
    )
    yesterday2_staff_count = yesterday2_staff_visits.count()
    
    # Filter PageVisit objects for visits on the previous day and with last_name 'Current Student'
    yesterday2_alumni_visits = PageVisit.objects.filter(
        visited_at=yesterday_2days.date(),
        # Make sure 'yesterday Student' is enclosed in single quotes
        user__last_name='Alumni'
    )
    yesterday2_alumni_count = yesterday2_alumni_visits.count()
    
    # Filter PageVisit objects for visits on the previous day and with last_name 'Current Student'
    yesterday2_faculty_visits = PageVisit.objects.filter(
        visited_at=yesterday_2days.date(),
        # Make sure 'yesterday Student' is enclosed in single quotes
        user__last_name='Faculty'
    )
    yesterday2_faculty_count = yesterday2_faculty_visits.count()



    # Filter PageVisit objects for visits on the previous day and with last_name 'Current Student'
    yesterday_students_visits = PageVisit.objects.filter(
        visited_at=yesterday.date(),
        # Make sure 'yesterday Student' is enclosed in single quotes
        user__last_name='Current Student'
    )
    yesterday_student_count = yesterday_students_visits.count()
    
    # Filter PageVisit objects for visits on the previous day and with last_name 'Current Student'
    yesterday_staff_visits = PageVisit.objects.filter(
        visited_at=yesterday.date(),
        # Make sure 'yesterday Student' is enclosed in single quotes
        user__last_name='Staff'
    )
    yesterday_staff_count = yesterday_staff_visits.count()
    
    # Filter PageVisit objects for visits on the previous day and with last_name 'Current Student'
    yesterday_alumni_visits = PageVisit.objects.filter(
        visited_at=yesterday.date(),
        # Make sure 'yesterday Student' is enclosed in single quotes
        user__last_name='Alumni'
    )
    yesterday_alumni_count = yesterday_alumni_visits.count()
    
    # Filter PageVisit objects for visits on the previous day and with last_name 'Current Student'
    yesterday_faculty_visits = PageVisit.objects.filter(
        visited_at=yesterday.date(),
        # Make sure 'yesterday Student' is enclosed in single quotes
        user__last_name='Faculty'
    )
    yesterday_faculty_count = yesterday_faculty_visits.count()
    
    
    
    
    
     
    context = {
        'yesterday_datetime':yesterday_datetime,
        'yesterday7_student_count':yesterday7_student_count,
        'yesterday7_staff_count':yesterday7_staff_count,
        'yesterday7_alumni_count':yesterday7_alumni_count,
        'yesterday7_faculty_count':yesterday7_faculty_count,
        
        'yesterday6_student_count':yesterday6_student_count,
        'yesterday6_staff_count':yesterday6_staff_count,
        'yesterday6_alumni_count':yesterday6_alumni_count,
        'yesterday6_faculty_count':yesterday6_faculty_count,
        
        'yesterday5_student_count':yesterday5_student_count,
        'yesterday5_staff_count':yesterday5_staff_count,
        'yesterday5_alumni_count':yesterday5_alumni_count,
        'yesterday5_faculty_count':yesterday5_faculty_count,
        
        'yesterday4_student_count':yesterday4_student_count,
        'yesterday4_staff_count':yesterday4_staff_count,
        'yesterday4_alumni_count':yesterday4_alumni_count,
        'yesterday4_faculty_count':yesterday4_faculty_count,
        
        'yesterday3_student_count':yesterday3_student_count,
        'yesterday3_staff_count':yesterday3_staff_count,
        'yesterday3_alumni_count':yesterday3_alumni_count,
        'yesterday3_faculty_count':yesterday3_faculty_count,
        
        'yesterday2_student_count':yesterday2_student_count,
        'yesterday2_staff_count':yesterday2_staff_count,
        'yesterday2_alumni_count':yesterday2_alumni_count,
        'yesterday2_faculty_count':yesterday2_faculty_count,
        
        'yesterday_student_count': yesterday_student_count,
        'yesterday_alumni_count': yesterday_alumni_count,
        'yesterday_faculty_count': yesterday_faculty_count,
        'yesterday_staff_count': yesterday_faculty_count,
        
        'yesterday_all_visits': yesterday_all_visits,
        
        'yesterday': yesterday,
        'yesterday_2days': yesterday_2days,
        'yesterday_3days': yesterday_3days,
        'yesterday_4days': yesterday_4days,
        'yesterday_5days': yesterday_5days,
        'yesterday_6days': yesterday_6days,
        'yesterday_7days': yesterday_7days,
        'yesterday_8days': yesterday_8days,
        'yesterday_9days': yesterday_9days,
        'yesterday_10days': yesterday_10days,
        'yesterday_11days': yesterday_11days,
        'yesterday_12days': yesterday_12days,
        'yesterday_13days': yesterday_13days,
        'yesterday_14days': yesterday_14days,
        'yesterday_15days': yesterday_15days,
        'yesterday_16days': yesterday_16days,
        'yesterday_17days': yesterday_17days,
        'yesterday_18days': yesterday_18days,
        'yesterday_19days': yesterday_19days,
        'yesterday_20days': yesterday_20days,
        'yesterday_21days': yesterday_21days,
        'yesterday_22days': yesterday_22days,
        'yesterday_23days': yesterday_23days,
        'yesterday_24days': yesterday_24days,
        'yesterday_25days': yesterday_25days,
        'yesterday_26days': yesterday_26days,
        'yesterday_27days': yesterday_27days,
        'yesterday_28days': yesterday_28days,
        'yesterday_29days': yesterday_29days,
        'yesterday_30days': yesterday_30days,
    }
    return render(request, "admin/graphs-30days.html", context) 
    
    '''