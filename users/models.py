from email.policy import default
from tkinter import CASCADE
from django.db import models
from datetime import datetime
from django.utils import timezone
from django.core.validators import FileExtensionValidator
from django.contrib.auth.models import User


now = timezone.now()
currentDate = now.date()

class Librarian(models.Model):
    username = models.CharField(max_length=250)
    password = models.CharField(max_length=250)
    
class Manuscripts(models.Model):
    title = models.CharField(max_length=250)
    authors = models.CharField(max_length=1000)
    filename = models.FileField(upload_to='media/', validators=[FileExtensionValidator(allowed_extensions=['pdf'])],)
    downloads = models.IntegerField(default=0)
    year = models.CharField(max_length=250)
    program = models.CharField(max_length=20)
    upload_date = models.DateField(default=now)
    abstractES_num = models.IntegerField()

class Staffs(models.Model):
    credentials = models.OneToOneField(User , on_delete=models.CASCADE)
    forget_password_token = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    
class Visitors(models.Model):
    email = models.CharField(max_length=250)
    file_link = models.CharField(max_length=250)
    filename = models.ForeignKey(Manuscripts, on_delete=models.CASCADE)
    requests_email_token = models.CharField(max_length=250)
    requested_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=100, default="Not Granted")

class PageVisit(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    visited_at = models.DateField()
    

class VisitorView(models.Model):
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    anonymous_uuid = models.UUIDField(null=True, blank=True, unique=True)
    
class CurrentStudent(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    program = models.CharField(max_length=250)
    year = models.CharField(max_length=250)
   
class Staff(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    office = models.CharField(max_length=250)
    
class Faculty(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    department = models.CharField(max_length=250)
    
class Alumni(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    affiliation = models.CharField(max_length=250)    