from datetime import timedelta

from django.conf import settings
from django.db.models import F
from django.utils import timezone

from .models import News


def increment_news_view(request, news: News) -> bool:
    key = f'viewed_news_{news.pk}'
    viewed = request.session.get(key)
    now = timezone.now().timestamp()
    dedup_seconds = settings.NEWS_VIEW_DEDUP_HOURS * 3600

    if viewed and now - viewed < dedup_seconds:
        return False

    News.objects.filter(pk=news.pk).update(views_count=F('views_count') + 1)
    request.session[key] = now
    request.session.modified = True
    return True


def register_like(request, news: News) -> bool:
    key = f'liked_news_{news.pk}'
    if request.session.get(key):
        return False

    News.objects.filter(pk=news.pk).update(likes_count=F('likes_count') + 1)
    request.session[key] = True
    request.session.modified = True
    return True
