from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import PageVisit  # Import your model here

admin.site.register(PageVisit)  # Register your model