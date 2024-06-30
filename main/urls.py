from django.urls import path

from . import views
from .views import blog_list

urlpatterns = [
    path('', blog_list, name='blog_list'),
    path('blog/createBlogPost', views.createBlogPost, name='create_blog_post'),
    path('blog/<int:blog_id>/', views.blog_detail, name='detail'),
    path('chatbot/', views.chatbot_api, name='chatbot'),
    path('login', views.login, name='login'),
    path('register', views.register, name='register'),
    path('logout', views.logout, name='logout'),
]