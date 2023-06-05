from django.utils.html import format_html, urlencode
from django.db.models import Count
from django.contrib import admin
from django.urls import reverse
from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'first_name',
                    'last_name', 'email', 'is_staff']
    list_editable = ['is_staff']
    list_filter = ['is_staff']
    list_per_page = 10
    fields = ['username', 'first_name', 'last_name',
              'email', 'password', 'is_staff']
    search_fields = ['username']

    def _reviews(self, user):
        url = (
            reverse('admin:store_reviews_changelist')
            + '?'
            + urlencode({
                'user__id': str(user.id)
            }))
        return format_html('<a href="{}">{}</a>', url, user.reviews_count)

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            reviews_count=Count('reviews')
        )
