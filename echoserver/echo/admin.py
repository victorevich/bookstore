from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Books, User
admin.site.register(User, UserAdmin)
admin.site.register(Books)


