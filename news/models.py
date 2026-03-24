import os
import uuid
from pathlib import Path

import bleach
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.template.defaultfilters import slugify
from django.urls import reverse
from django.utils import timezone
from tinymce.models import HTMLField

from .constants import ALLOWED_ATTACHMENT_EXTENSIONS


class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True)

    class Meta:
        ordering = ['name']

    def __str__(self) -> str:
        return self.name


class News(models.Model):
    class Status(models.TextChoices):
        DRAFT = 'draft', 'Черновик'
        PUBLISHED = 'published', 'Опубликовано'

    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=280, unique=True)
    content = HTMLField()
    tags = models.ManyToManyField(Tag, related_name='news_items', blank=True)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.DRAFT)
    views_count = models.PositiveIntegerField(default=0)
    likes_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ['-published_at', '-created_at']

    def save(self, *args, **kwargs):
        was_published = False
        if self.pk:
            was_published = News.objects.filter(pk=self.pk, status=News.Status.PUBLISHED).exists()

        if not self.slug:
            base = slugify(self.title)[:250] or 'news'
            candidate = base
            idx = 1
            while News.objects.filter(slug=candidate).exclude(pk=self.pk).exists():
                idx += 1
                candidate = f'{base}-{idx}'[:280]
            self.slug = candidate

        if self.status == News.Status.PUBLISHED and not self.published_at:
            self.published_at = timezone.now()

        self.content = bleach.clean(
            self.content,
            tags=['p', 'br', 'strong', 'b', 'em', 'i', 'ul', 'ol', 'li', 'a', 'blockquote', 'h2', 'h3', 'h4'],
            attributes={'a': ['href', 'title', 'rel', 'target']},
            strip=True,
        )
        super().save(*args, **kwargs)

        if self.status == News.Status.PUBLISHED and self.published_at and not was_published:
            from subscriptions.tasks import dispatch_news_publication_notifications
            dispatch_news_publication_notifications.delay(self.pk)

    def get_absolute_url(self):
        return reverse('news:news_detail', kwargs={'slug': self.slug})

    def __str__(self) -> str:
        return self.title


def attachment_upload_path(instance: 'Attachment', filename: str) -> str:
    suffix = Path(filename).suffix.lower()
    safe_name = slugify(Path(filename).stem)[:120] or 'document'
    return f'attachments/{instance.news_id}/{safe_name}-{uuid.uuid4().hex[:8]}{suffix}'


class Attachment(models.Model):
    news = models.ForeignKey(News, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to=attachment_upload_path)
    original_name = models.CharField(max_length=255)
    file_size = models.PositiveBigIntegerField(default=0)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-uploaded_at']

    def clean(self):
        ext = Path(self.file.name).suffix.lower()
        if ext not in ALLOWED_ATTACHMENT_EXTENSIONS:
            raise ValidationError('Недопустимый тип файла.')

        max_size = settings.MAX_ATTACHMENT_SIZE_MB * 1024 * 1024
        if self.file.size > max_size:
            raise ValidationError(f'Максимальный размер файла: {settings.MAX_ATTACHMENT_SIZE_MB} MB')

    def save(self, *args, **kwargs):
        if not self.original_name:
            self.original_name = os.path.basename(self.file.name)
        self.file_size = self.file.size
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.original_name
