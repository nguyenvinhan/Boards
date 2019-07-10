"""Board URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from django.conf.urls import url
from . import views



urlpatterns = [
    path('',views.BoardListView.as_view(), name = 'home'),
    path('boards/<int:board_id>/', views.TopicListView.as_view(), name = 'board_topics'),
    path('boards/<int:board_id>/new', views.new_topic, name = 'new_topic'),
    path('boards/<int:board_id>/topics/<int:topic_id>/', 
        views.PostListView.as_view(), name = 'topic_posts'),

    path('boards/<int:board_id>/topics/<int:topic_id>/reply/', 
        views.reply_topic, name='reply_topic'),

    path('boards/<int:board_id>/topics/<int:topic_id>/posts/<int:post_id>/edit/',
        views.PostUpdateView.as_view(), name='edit_post'),
]
