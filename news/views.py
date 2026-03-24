from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from subscriptions.forms import TagSubscriptionForm

from .forms import NewsSearchForm
from .models import News, Tag
from .services import increment_news_view, register_like


def news_list(request: HttpRequest) -> HttpResponse:
    qs = News.objects.filter(status=News.Status.PUBLISHED).prefetch_related('tags')
    form = NewsSearchForm(request.GET)
    tag_slug = request.GET.get('tag')

    if form.is_valid() and form.cleaned_data.get('q'):
        query = form.cleaned_data['q']
        qs = qs.filter(Q(title__icontains=query) | Q(content__icontains=query))

    if tag_slug:
        qs = qs.filter(tags__slug=tag_slug)

    paginator = Paginator(qs.distinct(), 10)
    page_obj = paginator.get_page(request.GET.get('page', 1))

    return render(request, 'news/news_list.html', {
        'page_obj': page_obj,
        'search_form': form,
        'active_tag_slug': tag_slug,
    })


def news_detail(request: HttpRequest, slug: str) -> HttpResponse:
    news = get_object_or_404(
        News.objects.prefetch_related('tags', 'attachments'),
        slug=slug,
        status=News.Status.PUBLISHED,
    )
    increment_news_view(request, news)
    news.refresh_from_db(fields=['views_count', 'likes_count'])
    return render(request, 'news/news_detail.html', {
        'news': news,
        'liked': bool(request.session.get(f'liked_news_{news.pk}')),
        'subscription_form': TagSubscriptionForm(),
    })


@require_POST
def like_news(request: HttpRequest, slug: str) -> HttpResponse:
    news = get_object_or_404(News, slug=slug, status=News.Status.PUBLISHED)
    liked = register_like(request, news)
    if not liked:
        messages.info(request, 'Вы уже поставили лайк этой новости.')
    else:
        messages.success(request, 'Спасибо за реакцию!')
    return redirect(news.get_absolute_url())


def tag_news_list(request: HttpRequest, slug: str) -> HttpResponse:
    tag = get_object_or_404(Tag, slug=slug)
    qs = News.objects.filter(status=News.Status.PUBLISHED, tags=tag).prefetch_related('tags')
    paginator = Paginator(qs.distinct(), 10)
    page_obj = paginator.get_page(request.GET.get('page', 1))

    return render(request, 'news/tag_detail.html', {
        'tag': tag,
        'page_obj': page_obj,
        'subscription_form': TagSubscriptionForm(initial={'tag': tag.pk}),
    })
