from django.contrib import admin

from .models import TagSubscription


@admin.register(TagSubscription)
class TagSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('email', 'tag', 'is_active', 'created_at')
    list_filter = ('is_active', 'tag')
    search_fields = ('email', 'tag__name')
