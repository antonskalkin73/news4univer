from django.conf import settings
from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from .forms import TagSubscriptionForm
from .models import TagSubscription


@require_http_methods(['POST'])
def subscribe(request: HttpRequest) -> HttpResponse:
    last_attempt = request.session.get('subscription_last_attempt', 0)
    now_ts = int(timezone.now().timestamp())
    if now_ts - last_attempt < settings.SUBSCRIPTION_RATE_LIMIT_SECONDS:
        messages.error(request, 'Слишком частые запросы. Попробуйте позже.')
        return redirect(request.META.get('HTTP_REFERER', 'news:news_list'))

    form = TagSubscriptionForm(request.POST)
    if form.is_valid():
        obj, created = TagSubscription.objects.get_or_create(
            email=form.cleaned_data['email'],
            tag=form.cleaned_data['tag'],
            defaults={'is_active': True},
        )
        if not created and not obj.is_active:
            obj.is_active = True
            obj.save(update_fields=['is_active'])
            messages.success(request, 'Подписка восстановлена.')
        elif created:
            messages.success(request, 'Подписка оформлена успешно.')
        else:
            messages.info(request, 'Вы уже подписаны на этот тег.')
    else:
        messages.error(request, 'Некорректные данные формы подписки.')

    request.session['subscription_last_attempt'] = now_ts
    return redirect(request.META.get('HTTP_REFERER', '/'))


def unsubscribe(request: HttpRequest, token: str) -> HttpResponse:
    subscription = get_object_or_404(TagSubscription, unsubscribe_token=token)
    subscription.is_active = False
    subscription.save(update_fields=['is_active'])
    return render(request, 'subscriptions/unsubscribe_done.html', {'subscription': subscription})
