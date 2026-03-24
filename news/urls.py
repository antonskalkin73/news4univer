from django.urls import path

from . import views

app_name = 'news'

urlpatterns = [
    path('', views.news_list, name='news_list'),
    path('news/<slug:slug>/', views.news_detail, name='news_detail'),
    path('news/<slug:slug>/like/', views.like_news, name='like_news'),
    path('tags/<slug:slug>/', views.tag_news_list, name='tag_news_list'),
]
