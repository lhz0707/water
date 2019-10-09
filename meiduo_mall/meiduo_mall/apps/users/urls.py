from django.conf.urls import url
from django.contrib import admin
from . import views
urlpatterns = [

    # 注册
    url(r'^register/$', views.UserRegisterView.as_view()),
    # 登录
    url(r'^login/$', views.UserLoginView.as_view()),
    # 退出登录
    url(r'^logout/$', views.UserLogoutView.as_view()),

    # 用户中心
    url(r'^info/$', views.UserInfoView.as_view()),
    # 更新邮箱
    url(r'^emails/$',views.UserEmailView.as_view()),
    # 验证邮箱
    url(r'^emails/verification/$', views.UserEmailVerifyView.as_view()),


    # 修改密码
    url(r'^password/$', views.ChangePWDView.as_view())




]
