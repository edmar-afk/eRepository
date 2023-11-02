import uuid
from django.shortcuts import render, get_object_or_404
from .models import Manuscripts, Librarian, Visitors, Staffs, VisitorView, VisitorCount
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
from django.utils import timezone
from django.contrib.sessions.models import Session
from uuid import uuid4
from datetime import datetime
from django.db.models import Q
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail
# Create your views here.


def dashboard(request):
    manuscripts_count = Manuscripts.objects.all().count()
    requests_count = Visitors.objects.all()
    librarians_count = User.objects.all().count()
    visitors_view_count = VisitorView.objects.count()

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
        "visitors_view_count": visitors_view_count,
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


def visitor_index(request):
    manuscripts = Manuscripts.objects.all().order_by('-year')

    if request.method == "POST":
        email = request.POST['email']
        fileLink = request.POST['file_link']
        fileName = request.POST['file_name']

        token = str(uuid.uuid4())
        new_requests = Visitors(email=email, file_link=fileLink,
                                filename_id=fileName, requests_email_token=token)
        new_requests.save()

    # Retrieve the visitor count object, or create a new one if it doesn't exist yet
    visitor_count, created = VisitorCount.objects.get_or_create(pk=1)

    if created:
        visitor_count.count = 1
        visitor_count.save()

    ip_address = request.META.get('REMOTE_ADDR')
    user_agent = request.META.get('HTTP_USER_AGENT')

    try:
        visitor = VisitorView.objects.get(
            ip_address=ip_address, user_agent=user_agent)
    except VisitorView.DoesNotExist:
        anonymous_uuid = uuid4()  # Generate a new UUID for anonymous users
        visitor = VisitorView.objects.create(
            ip_address=ip_address, user_agent=user_agent, anonymous_uuid=anonymous_uuid)

    count_visitor = VisitorView.objects.count()

    # Get the current time
    current_time = timezone.now()

    # Get all the sessions that are currently active
    sessions = Session.objects.filter(expire_date__gte=current_time)

    # Initialize a counter for anonymous users
    anonymous_user_count = 0

    # Iterate through each session and check if the user is anonymous
    for session in sessions:
        session_data = session.get_decoded()
        if '_auth_user_id' not in session_data:
            anonymous_user_count += 1

    context = {
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

        send_mail(subject, message, from_email, recipient_list, auth_user=EMAIL_HOST_USER, auth_password=EMAIL_HOST_PASSWORD)

    messages.success(request, 'Librarian Staff info changed')

    return redirect('/users')


def delete_books(request, books_id):
    try:
        manuscript = Manuscripts.objects.get(id=books_id)
        pdf_file_path = manuscript.filename.path  # Replace 'pdf_field' with the actual field name for your PDF

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
        manuscript_update.filename.save(new_manuscript_file.name, new_manuscript_file)
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
    return redirect('signin')







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
    visitor_count, created = VisitorCount.objects.get_or_create(pk=1)

    if created:
        visitor_count.count = 1
        visitor_count.save()

    ip_address = request.META.get('REMOTE_ADDR')
    user_agent = request.META.get('HTTP_USER_AGENT')

    try:
        visitor = VisitorView.objects.get(
            ip_address=ip_address, user_agent=user_agent)
    except VisitorView.DoesNotExist:
        anonymous_uuid = uuid4()  # Generate a new UUID for anonymous users
        visitor = VisitorView.objects.create(
            ip_address=ip_address, user_agent=user_agent, anonymous_uuid=anonymous_uuid)

    count_visitor = VisitorView.objects.count()

    # Get the current time
    current_time = timezone.now()

    # Get all the sessions that are currently active
    sessions = Session.objects.filter(expire_date__gte=current_time)

    # Initialize a counter for anonymous users
    anonymous_user_count = 0

    # Iterate through each session and check if the user is anonymous
    for session in sessions:
        session_data = session.get_decoded()
        if '_auth_user_id' not in session_data:
            anonymous_user_count += 1

    context = {
        'manuscripts': manuscripts
    }
    return render(request, 'visitors/courses.html', context)

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
    visitor_count, created = VisitorCount.objects.get_or_create(pk=1)

    if created:
        visitor_count.count = 1
        visitor_count.save()

    ip_address = request.META.get('REMOTE_ADDR')
    user_agent = request.META.get('HTTP_USER_AGENT')

    try:
        visitor = VisitorView.objects.get(
            ip_address=ip_address, user_agent=user_agent)
    except VisitorView.DoesNotExist:
        anonymous_uuid = uuid4()  # Generate a new UUID for anonymous users
        visitor = VisitorView.objects.create(
            ip_address=ip_address, user_agent=user_agent, anonymous_uuid=anonymous_uuid)

    count_visitor = VisitorView.objects.count()

    # Get the current time
    current_time = timezone.now()

    # Get all the sessions that are currently active
    sessions = Session.objects.filter(expire_date__gte=current_time)

    # Initialize a counter for anonymous users
    anonymous_user_count = 0

    # Iterate through each session and check if the user is anonymous
    for session in sessions:
        session_data = session.get_decoded()
        if '_auth_user_id' not in session_data:
            anonymous_user_count += 1

    context = {
        'manuscripts': manuscripts
    }
    return render(request, 'visitors/courses.html', context)

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
    visitor_count, created = VisitorCount.objects.get_or_create(pk=1)

    if created:
        visitor_count.count = 1
        visitor_count.save()

    ip_address = request.META.get('REMOTE_ADDR')
    user_agent = request.META.get('HTTP_USER_AGENT')

    try:
        visitor = VisitorView.objects.get(
            ip_address=ip_address, user_agent=user_agent)
    except VisitorView.DoesNotExist:
        anonymous_uuid = uuid4()  # Generate a new UUID for anonymous users
        visitor = VisitorView.objects.create(
            ip_address=ip_address, user_agent=user_agent, anonymous_uuid=anonymous_uuid)

    count_visitor = VisitorView.objects.count()

    # Get the current time
    current_time = timezone.now()

    # Get all the sessions that are currently active
    sessions = Session.objects.filter(expire_date__gte=current_time)

    # Initialize a counter for anonymous users
    anonymous_user_count = 0

    # Iterate through each session and check if the user is anonymous
    for session in sessions:
        session_data = session.get_decoded()
        if '_auth_user_id' not in session_data:
            anonymous_user_count += 1

    context = {
        'manuscripts': manuscripts
    }
    return render(request, 'visitors/courses.html', context)

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
    visitor_count, created = VisitorCount.objects.get_or_create(pk=1)

    if created:
        visitor_count.count = 1
        visitor_count.save()

    ip_address = request.META.get('REMOTE_ADDR')
    user_agent = request.META.get('HTTP_USER_AGENT')

    try:
        visitor = VisitorView.objects.get(
            ip_address=ip_address, user_agent=user_agent)
    except VisitorView.DoesNotExist:
        anonymous_uuid = uuid4()  # Generate a new UUID for anonymous users
        visitor = VisitorView.objects.create(
            ip_address=ip_address, user_agent=user_agent, anonymous_uuid=anonymous_uuid)

    count_visitor = VisitorView.objects.count()

    # Get the current time
    current_time = timezone.now()

    # Get all the sessions that are currently active
    sessions = Session.objects.filter(expire_date__gte=current_time)

    # Initialize a counter for anonymous users
    anonymous_user_count = 0

    # Iterate through each session and check if the user is anonymous
    for session in sessions:
        session_data = session.get_decoded()
        if '_auth_user_id' not in session_data:
            anonymous_user_count += 1

    context = {
        'manuscripts': manuscripts
    }
    return render(request, 'visitors/courses.html', context)

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
    visitor_count, created = VisitorCount.objects.get_or_create(pk=1)

    if created:
        visitor_count.count = 1
        visitor_count.save()

    ip_address = request.META.get('REMOTE_ADDR')
    user_agent = request.META.get('HTTP_USER_AGENT')

    try:
        visitor = VisitorView.objects.get(
            ip_address=ip_address, user_agent=user_agent)
    except VisitorView.DoesNotExist:
        anonymous_uuid = uuid4()  # Generate a new UUID for anonymous users
        visitor = VisitorView.objects.create(
            ip_address=ip_address, user_agent=user_agent, anonymous_uuid=anonymous_uuid)

    count_visitor = VisitorView.objects.count()

    # Get the current time
    current_time = timezone.now()

    # Get all the sessions that are currently active
    sessions = Session.objects.filter(expire_date__gte=current_time)

    # Initialize a counter for anonymous users
    anonymous_user_count = 0

    # Iterate through each session and check if the user is anonymous
    for session in sessions:
        session_data = session.get_decoded()
        if '_auth_user_id' not in session_data:
            anonymous_user_count += 1

    context = {
        'manuscripts': manuscripts
    }
    return render(request, 'visitors/courses.html', context)

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
    visitor_count, created = VisitorCount.objects.get_or_create(pk=1)

    if created:
        visitor_count.count = 1
        visitor_count.save()

    ip_address = request.META.get('REMOTE_ADDR')
    user_agent = request.META.get('HTTP_USER_AGENT')

    try:
        visitor = VisitorView.objects.get(
            ip_address=ip_address, user_agent=user_agent)
    except VisitorView.DoesNotExist:
        anonymous_uuid = uuid4()  # Generate a new UUID for anonymous users
        visitor = VisitorView.objects.create(
            ip_address=ip_address, user_agent=user_agent, anonymous_uuid=anonymous_uuid)

    count_visitor = VisitorView.objects.count()

    # Get the current time
    current_time = timezone.now()

    # Get all the sessions that are currently active
    sessions = Session.objects.filter(expire_date__gte=current_time)

    # Initialize a counter for anonymous users
    anonymous_user_count = 0

    # Iterate through each session and check if the user is anonymous
    for session in sessions:
        session_data = session.get_decoded()
        if '_auth_user_id' not in session_data:
            anonymous_user_count += 1

    context = {
        'manuscripts': manuscripts
    }
    return render(request, 'visitors/courses.html', context)

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
    visitor_count, created = VisitorCount.objects.get_or_create(pk=1)

    if created:
        visitor_count.count = 1
        visitor_count.save()

    ip_address = request.META.get('REMOTE_ADDR')
    user_agent = request.META.get('HTTP_USER_AGENT')

    try:
        visitor = VisitorView.objects.get(
            ip_address=ip_address, user_agent=user_agent)
    except VisitorView.DoesNotExist:
        anonymous_uuid = uuid4()  # Generate a new UUID for anonymous users
        visitor = VisitorView.objects.create(
            ip_address=ip_address, user_agent=user_agent, anonymous_uuid=anonymous_uuid)

    count_visitor = VisitorView.objects.count()

    # Get the current time
    current_time = timezone.now()

    # Get all the sessions that are currently active
    sessions = Session.objects.filter(expire_date__gte=current_time)

    # Initialize a counter for anonymous users
    anonymous_user_count = 0

    # Iterate through each session and check if the user is anonymous
    for session in sessions:
        session_data = session.get_decoded()
        if '_auth_user_id' not in session_data:
            anonymous_user_count += 1

    context = {
        'manuscripts': manuscripts
    }
    return render(request, 'visitors/courses.html', context)

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
    visitor_count, created = VisitorCount.objects.get_or_create(pk=1)

    if created:
        visitor_count.count = 1
        visitor_count.save()

    ip_address = request.META.get('REMOTE_ADDR')
    user_agent = request.META.get('HTTP_USER_AGENT')

    try:
        visitor = VisitorView.objects.get(
            ip_address=ip_address, user_agent=user_agent)
    except VisitorView.DoesNotExist:
        anonymous_uuid = uuid4()  # Generate a new UUID for anonymous users
        visitor = VisitorView.objects.create(
            ip_address=ip_address, user_agent=user_agent, anonymous_uuid=anonymous_uuid)

    count_visitor = VisitorView.objects.count()

    # Get the current time
    current_time = timezone.now()

    # Get all the sessions that are currently active
    sessions = Session.objects.filter(expire_date__gte=current_time)

    # Initialize a counter for anonymous users
    anonymous_user_count = 0

    # Iterate through each session and check if the user is anonymous
    for session in sessions:
        session_data = session.get_decoded()
        if '_auth_user_id' not in session_data:
            anonymous_user_count += 1

    context = {
        'manuscripts': manuscripts
    }
    return render(request, 'visitors/courses.html', context)

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
    visitor_count, created = VisitorCount.objects.get_or_create(pk=1)

    if created:
        visitor_count.count = 1
        visitor_count.save()

    ip_address = request.META.get('REMOTE_ADDR')
    user_agent = request.META.get('HTTP_USER_AGENT')

    try:
        visitor = VisitorView.objects.get(
            ip_address=ip_address, user_agent=user_agent)
    except VisitorView.DoesNotExist:
        anonymous_uuid = uuid4()  # Generate a new UUID for anonymous users
        visitor = VisitorView.objects.create(
            ip_address=ip_address, user_agent=user_agent, anonymous_uuid=anonymous_uuid)

    count_visitor = VisitorView.objects.count()

    # Get the current time
    current_time = timezone.now()

    # Get all the sessions that are currently active
    sessions = Session.objects.filter(expire_date__gte=current_time)

    # Initialize a counter for anonymous users
    anonymous_user_count = 0

    # Iterate through each session and check if the user is anonymous
    for session in sessions:
        session_data = session.get_decoded()
        if '_auth_user_id' not in session_data:
            anonymous_user_count += 1

    context = {
        'manuscripts': manuscripts
    }
    return render(request, 'visitors/courses.html', context)

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
    visitor_count, created = VisitorCount.objects.get_or_create(pk=1)

    if created:
        visitor_count.count = 1
        visitor_count.save()

    ip_address = request.META.get('REMOTE_ADDR')
    user_agent = request.META.get('HTTP_USER_AGENT')

    try:
        visitor = VisitorView.objects.get(
            ip_address=ip_address, user_agent=user_agent)
    except VisitorView.DoesNotExist:
        anonymous_uuid = uuid4()  # Generate a new UUID for anonymous users
        visitor = VisitorView.objects.create(
            ip_address=ip_address, user_agent=user_agent, anonymous_uuid=anonymous_uuid)

    count_visitor = VisitorView.objects.count()

    # Get the current time
    current_time = timezone.now()

    # Get all the sessions that are currently active
    sessions = Session.objects.filter(expire_date__gte=current_time)

    # Initialize a counter for anonymous users
    anonymous_user_count = 0

    # Iterate through each session and check if the user is anonymous
    for session in sessions:
        session_data = session.get_decoded()
        if '_auth_user_id' not in session_data:
            anonymous_user_count += 1

    context = {
        'manuscripts': manuscripts
    }
    return render(request, 'visitors/courses.html', context)

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
    visitor_count, created = VisitorCount.objects.get_or_create(pk=1)

    if created:
        visitor_count.count = 1
        visitor_count.save()

    ip_address = request.META.get('REMOTE_ADDR')
    user_agent = request.META.get('HTTP_USER_AGENT')

    try:
        visitor = VisitorView.objects.get(
            ip_address=ip_address, user_agent=user_agent)
    except VisitorView.DoesNotExist:
        anonymous_uuid = uuid4()  # Generate a new UUID for anonymous users
        visitor = VisitorView.objects.create(
            ip_address=ip_address, user_agent=user_agent, anonymous_uuid=anonymous_uuid)

    count_visitor = VisitorView.objects.count()

    # Get the current time
    current_time = timezone.now()

    # Get all the sessions that are currently active
    sessions = Session.objects.filter(expire_date__gte=current_time)

    # Initialize a counter for anonymous users
    anonymous_user_count = 0

    # Iterate through each session and check if the user is anonymous
    for session in sessions:
        session_data = session.get_decoded()
        if '_auth_user_id' not in session_data:
            anonymous_user_count += 1

    context = {
        'manuscripts': manuscripts
    }
    return render(request, 'visitors/courses.html', context)




