from django.utils.html import format_html, urlencode
from django.db.models import Count
from django.contrib import admin, messages
from django.urls import reverse
from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'first_name',
                    'last_name', 'email', 'is_staff', '_reviews']
    list_editable = ['is_staff']
    list_filter = ['is_staff']
    list_per_page = 10
    fields = ['username', 'first_name', 'last_name',
              'email', 'password', 'is_staff']
    search_fields = ['username']
    actions = ['delete_reviews']

    @admin.display(ordering='reviews_count')
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

    @admin.action(description='Delete reviews')
    def delete_reviews(self, request, queryset):
        total_reviews_count = sum(user.reviews_set.count()
                                  for user in queryset)

        for user in queryset:
            user.reviews_set.all().delete()

        self.message_user(
            request,
            f'{total_reviews_count} were successfully deleted.',
            messages.SUCCESS
        )
