from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import News, Tag


class NewsPublicTests(TestCase):
    def setUp(self):
        self.tag = Tag.objects.create(name='Объявления', slug='obyavleniya')
        self.news = News.objects.create(
            title='Тестовая новость',
            slug='test-news',
            content='<p>Важный текст новости</p>',
            status=News.Status.PUBLISHED,
            published_at=timezone.now(),
        )
        self.news.tags.add(self.tag)

    def test_news_publication(self):
        self.assertEqual(self.news.status, News.Status.PUBLISHED)
        self.assertIsNotNone(self.news.published_at)

    def test_views_deduplication(self):
        url = reverse('news:news_detail', kwargs={'slug': self.news.slug})
        self.client.get(url)
        self.client.get(url)
        self.news.refresh_from_db()
        self.assertEqual(self.news.views_count, 1)

    def test_anonymous_like_once(self):
        url = reverse('news:like_news', kwargs={'slug': self.news.slug})
        self.client.post(url)
        self.client.post(url)
        self.news.refresh_from_db()
        self.assertEqual(self.news.likes_count, 1)

    def test_filter_by_tag(self):
        resp = self.client.get(reverse('news:tag_news_list', kwargs={'slug': self.tag.slug}))
        self.assertContains(resp, self.news.title)

    def test_search_news(self):
        resp = self.client.get(reverse('news:news_list'), {'q': 'Важный'})
        self.assertContains(resp, self.news.title)
