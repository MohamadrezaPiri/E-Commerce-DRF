from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as Admin
from .models import User

@admin.register(User)
class AdminUser(Admin):
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("username", "password1", "password2",'email','first_name','last_name'),
            },
        ),
    )

