from django.urls import path

from . import views
from .views import article_list

urlpatterns = [
    path('', article_list, name='article_list'),
    path('article/createBlogPost', views.createBlogPost, name='create_blog_post'),
]