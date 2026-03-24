from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.urls import reverse

from news.models import News

from .models import TagSubscription


def get_unique_subscribers_for_news(news: News) -> dict[str, str]:
    data: dict[str, str] = {}
    subscriptions = TagSubscription.objects.filter(
        tag__in=news.tags.all(),
        is_active=True,
    ).select_related('tag')

    for item in subscriptions:
        data.setdefault(item.email, item.unsubscribe_token)
    return data


def send_news_notification(news: News) -> int:
    recipients = get_unique_subscribers_for_news(news)
    if not recipients:
        return 0

    sent = 0
    for email, token in recipients.items():
        unsubscribe_link = settings.SITE_URL + reverse('subscriptions:unsubscribe', kwargs={'token': token})
        context = {
            'news': news,
            'unsubscribe_link': unsubscribe_link,
            'site_url': settings.SITE_URL,
        }
        text_body = render_to_string('emails/news_published.txt', context)
        html_body = render_to_string('emails/news_published.html', context)

        msg = EmailMultiAlternatives(
            subject=f'Новая новость: {news.title}',
            body=text_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[email],
        )
        msg.attach_alternative(html_body, 'text/html')
        msg.send(fail_silently=False)
        sent += 1

    return sent
