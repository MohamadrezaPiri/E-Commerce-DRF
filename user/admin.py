from django.contrib import admin
from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'first_name', 'last_name', 'email', 'is_staff']
    list_editable = ['is_staff']
    list_filter = ['is_staff']
    list_per_page = 10
    fields = ['username', 'first_name', 'last_name',
              'email', 'password', 'is_staff']
    search_fields = ['username']
