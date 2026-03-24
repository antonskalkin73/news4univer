from django.urls import path

from . import views

app_name = 'subscriptions'

urlpatterns = [
    path('subscribe/', views.subscribe, name='subscribe'),
    path('unsubscribe/<str:token>/', views.unsubscribe, name='unsubscribe'),
]
