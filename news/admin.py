from django.contrib import admin
from django.db import models
from django.utils import timezone
from tinymce.widgets import TinyMCE

from .models import Attachment, News, Tag


class AttachmentInline(admin.TabularInline):
    model = Attachment
    extra = 1


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'published_at', 'views_count', 'likes_count', 'updated_at')
    list_filter = ('status', 'tags')
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ('title', 'content')
    filter_horizontal = ('tags',)
    inlines = [AttachmentInline]
    formfield_overrides = {
        models.TextField: {'widget': TinyMCE()},
    }

    def save_model(self, request, obj: News, form, change):
        if obj.status == News.Status.PUBLISHED and not obj.published_at:
            obj.published_at = timezone.now()
        super().save_model(request, obj, form, change)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)


@admin.register(Attachment)
class AttachmentAdmin(admin.ModelAdmin):
    list_display = ('original_name', 'news', 'file_size', 'uploaded_at')
    list_filter = ('uploaded_at',)
