from celery import shared_task

from news.models import News

from .services import send_news_notification


@shared_task
def dispatch_news_publication_notifications(news_id: int) -> int:
    news = News.objects.prefetch_related('tags').get(pk=news_id)
    if news.status != News.Status.PUBLISHED:
        return 0
    return send_news_notification(news)
