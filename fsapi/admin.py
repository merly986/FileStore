from django.contrib import admin

# Register your models here.
from .models import Fsfile,Fspath

admin.site.register(Fsfile)
admin.site.register(Fspath)