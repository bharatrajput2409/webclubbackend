from django.contrib import admin
from .models import blogs,tag,taginblog
# Register your models here.
admin.site.register(blogs)
admin.site.register(tag)
admin.site.register(taginblog)
