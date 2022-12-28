from django.contrib import admin

# Register your models here.
from .models import Fsfile,Fspart

admin.site.register(Fsfile)
admin.site.register(Fspart)