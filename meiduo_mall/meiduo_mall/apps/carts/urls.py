from django.conf.urls import url
from django.contrib import admin
from . import views
urlpatterns = [
    # 保存购物车数据
    url(r'^carts/$', views.CartView.as_view()),
    # 全选
    url(r'^carts/selection/$', views.CartSelectionView.as_view()),
    # 获取简单购物车数据
    url(r'^carts/simple/$', views.CartSimpleView.as_view()),
]
