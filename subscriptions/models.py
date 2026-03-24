import secrets

from django.db import models

from news.models import Tag


class TagSubscription(models.Model):
    email = models.EmailField()
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE, related_name='subscriptions')
    unsubscribe_token = models.CharField(max_length=64, unique=True, editable=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['email', 'tag'], name='unique_email_tag_subscription'),
        ]
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.unsubscribe_token:
            self.unsubscribe_token = secrets.token_urlsafe(32)
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f'{self.email} -> {self.tag.name}'
