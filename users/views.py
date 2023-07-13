from django.shortcuts import render, get_object_or_404
from .models import Manuscripts, Librarian, Visitors, Staffs
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
# Create your views here.


def dashboard(request):
    manuscripts_count = Manuscripts.objects.all().count()
    requests_count = Visitors.objects.all()
    librarians_count = User.objects.all().count()
    manuscripts = Manuscripts.objects.order_by('-id')[:5]
    requests = Visitors.objects.order_by('-id')[:5]
    
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
    context = {
        "manuscripts_count" : manuscripts_count,
        "manuscripts" : manuscripts,
        "librarians_count" : librarians_count,
        "requests_count" : requests_count,
        "requests" : requests,
        "bsit_count" : bsit_count,
        "bsed_count" : bsed_count,
        "beed_count" : beed_count,
        "bssw_count" : bssw_count,
        "bapos_count" : bapos_count,
        "baels_count" : baels_count,
        "bsm_count" : bsm_count,
        "bsa_count" : bsa_count,
        "bsf_count" : bsf_count,
        "bses_count" : bses_count,
        "bsce_count" : bsce_count,
        "total_downloads" : total_downloads,
        
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
       
        
        new_books = Manuscripts(title=title, authors=authors, filename=filename, program=program, year=year, abstractES_num=abes_num)
        new_books.save()
        messages.success(request, 'Manuscript added')
    context = {
        'manuscripts' : manuscripts
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
                new_user = User.objects.create_user(username=username, password=password1, email=email, first_name=first_name, last_name=mobile)
                new_user.save()
               
                
                profile_obj = Staffs.objects.create(credentials = new_user )
                profile_obj.save()
                messages.success(request, 'Librarian Account created')
                return redirect('users')
        else:
            messages.error(request, 'Password not match.')
            return redirect('users')
        
    return render(request, 'admin/users.html', context)



def requests(request):
    visitors = Visitors.objects.all().order_by('-id')
    context = {'visitor': visitors}
    
    return render(request, 'admin/requests.html', context)




import uuid
def send_email_download_request(request):
   
        if request.method == 'POST':
            email_visitor = request.POST.get('email')
            id_file = request.POST.get('id')
            
            if not Visitors.objects.filter(email=email_visitor)[0]:
                messages.success(request, 'No email found with this username.')
                return redirect('requests')
            
            token = str(uuid.uuid4())
            
            visitor_update = Visitors.objects.get(email=email_visitor, id=id_file)
            visitor_update.requests_email_token = token
            visitor_update.save()
            
            send_request_download_mail(email_visitor, token)
            messages.success(request, 'Request Granted')
            return redirect('requests')
                
        return render(request, 'visitors/request.html')


def download(request, token):
    
    download = Visitors.objects.filter(requests_email_token = token).first()
    file_id = download.filename_id
    
    download_count = get_object_or_404(Manuscripts, pk=file_id)
    download_count.downloads += 1
    download_count.save()
    
    context = {
            'id_file' : download.filename_id,
            'file' : download.file_link,
            'name' : download.filename.title,
            'downloads' : download.filename.downloads
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

import uuid
def visitor_index(request):
    manuscripts = Manuscripts.objects.all().order_by('-year')
    
    if request.method == "POST":
        email = request.POST['email']
        fileLink = request.POST['file_link']
        fileName = request.POST['file_name']
        
        token = str(uuid.uuid4())
        new_requests = Visitors(email=email, file_link=fileLink, filename_id=fileName, requests_email_token=token)
        new_requests.save()
    
    context = {
        'manuscripts' : manuscripts
    }
    return render(request, 'visitors/index.html', context)




def delete_users(request, user_id):
    User.objects.filter(id=user_id).delete()
    messages.success(request, 'Librarian User deleted')
    return redirect('/users')



def delete_books(request, books_id):
    Manuscripts.objects.filter(id=books_id).delete()
    messages.success(request, 'Manuscript deleted')
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