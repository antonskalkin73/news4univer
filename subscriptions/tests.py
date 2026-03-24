from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from news.models import News, Tag

from .models import TagSubscription
from .services import get_unique_subscribers_for_news


class SubscriptionTests(TestCase):
    def setUp(self):
        self.tag1 = Tag.objects.create(name='Наука', slug='science')
        self.tag2 = Tag.objects.create(name='Учеба', slug='study')
        self.news = News.objects.create(
            title='Запуск лаборатории',
            slug='lab-start',
            content='<p>Контент</p>',
            status=News.Status.PUBLISHED,
            published_at=timezone.now(),
        )
        self.news.tags.add(self.tag1, self.tag2)

    def test_unique_email_tag_subscription(self):
        TagSubscription.objects.create(email='a@example.com', tag=self.tag1)
        with self.assertRaises(Exception):
            TagSubscription.objects.create(email='a@example.com', tag=self.tag1)

    def test_unsubscribe_by_token(self):
        sub = TagSubscription.objects.create(email='a@example.com', tag=self.tag1)
        resp = self.client.get(reverse('subscriptions:unsubscribe', kwargs={'token': sub.unsubscribe_token}))
        self.assertEqual(resp.status_code, 200)
        sub.refresh_from_db()
        self.assertFalse(sub.is_active)

    def test_no_duplicate_emails_for_multiple_tags(self):
        TagSubscription.objects.create(email='a@example.com', tag=self.tag1)
        TagSubscription.objects.create(email='a@example.com', tag=self.tag2)
        uniq = get_unique_subscribers_for_news(self.news)
        self.assertEqual(len(uniq), 1)

    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend', SITE_URL='http://testserver')
    def test_notification_sent_once_per_email(self):
        from .services import send_news_notification

        TagSubscription.objects.create(email='a@example.com', tag=self.tag1)
        TagSubscription.objects.create(email='a@example.com', tag=self.tag2)
        count = send_news_notification(self.news)
        self.assertEqual(count, 1)
        self.assertEqual(len(mail.outbox), 1)
