from django.conf.urls import url
from django.urls import path

from . import views

app_name = 'blog'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('posts/<int:pk>/', views.detail, name='detail'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('archives/<int:year>/<int:month>/', views.ArchiveView.as_view(), name='archive'),
    path('recent_posts', views.recent_posts, name='recent_posts'),
    path('categories/<int:pk>/', views.CategoryView.as_view(), name='category'),
    path('tags/<int:pk>/', views.TagView.as_view(), name='tag'),
    path('search/',views.search, name='search'),
]