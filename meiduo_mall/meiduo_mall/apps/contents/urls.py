from django.conf.urls import url
from django.contrib import admin
from . import views
urlpatterns = [
    url(r'^img/$', views.ImageView.as_view()),
    # 首页处理
    url(r'^$', views.IndexView.as_view()),
]
