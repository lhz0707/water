from django.conf.urls import url
from django.contrib import admin
from rest_framework_jwt.views import obtain_jwt_token

from .views import statistical, users, sepecs, images,skus,orders,permission,groups,admins,options,channels,brands,spus
from rest_framework.routers import DefaultRouter

urlpatterns = [
    # 登录
    url(r'^authorizations/$', obtain_jwt_token),

    # ----------------数据统计--------------
    # 用户总数统计
    url(r'^statistical/total_count/$', statistical.UserTotalCount.as_view()),
    # 日增用户统计
    url(r'^statistical/day_increment/$', statistical.UserDayCount.as_view()),
    # 日活用户统计
    url(r'^statistical/day_active/$', statistical.UserDayActiveCount.as_view()),
    # 下单用户用户统计
    url(r'^statistical/day_orders/$', statistical.UserDayOrdersCount.as_view()),
    # 月增用户用户统计
    url(r'^statistical/month_increment/$', statistical.UserMonthCount.as_view()),
    # 商品分类访问量统计
    url(r'^statistical/goods_day_views/$', statistical.GoodsTypeCount.as_view()),

    # ----------------用户管理--------------
    url(r'^users/$', users.UsersView.as_view()),
    # ----------------规格管理--------------
    url(r'^goods/simple/$', sepecs.SpecView.as_view({'get': 'simple'})),
    # ----------------图片管理--------------
    url(r'^skus/simple/$', images.ImageView.as_view({'get': 'simple'})),


    url(r'^goods/(?P<pk>\d+)/specs/$', skus.SKUView.as_view({'get': 'specs'})),

    # 获取权限类型
    url(r'^permission/content_types/$',permission.PermissionView.as_view({'get': 'content_types'})),

    url(r'^permission/simple/$',groups.GroupView.as_view({'get': 'simple'})),

    url(r'^permission/groups/simple/$',admins.AdminView.as_view({'get': 'groups'})),

    url(r'^goods/specs/simple/$',options.SpecificationOptionView.as_view({'get': 'simple'})),
    url(r'^goods/channel_types/$',channels.GoodsChannelView.as_view({'get': 'simple'})),
    url(r'^goods/categories/$',channels.GoodsChannelView.as_view({'get': 'category'})),

    # 获取品牌
    url(r'^goods/brands/simple/$',spus.SPUView.as_view({'get': 'brands'})),
    # 获取一级分类
    url(r'^goods/channel/categories/$',spus.SPUView.as_view({'get': 'categories'})),
    # 获取二级和三级分类
    url(r'^goods/channel/categories/(?P<pk>\d+)/$',spus.SPUView.as_view({'get': 'categories_child'})),
    url(r'^goods/images/$',spus.SPUView.as_view({'post': 'image'})),


]

# ----------------规格管理--------------
router = DefaultRouter()

router.register('goods/specs', sepecs.SpecView, base_name='specs')
print(router.urls)
urlpatterns += router.urls


# ----------------图片管理--------------
router = DefaultRouter()
router.register('skus/images', images.ImageView, base_name='images')
urlpatterns += router.urls

# ---------------SKU管理--------------
# skus/categories
router = DefaultRouter()
router.register('skus', skus.SKUView, base_name='skus')
urlpatterns += router.urls

# ---------------订单表管理--------------
router = DefaultRouter()
# /orders/(?P<pk>)/status
router.register('orders', orders.OrderInfoView, base_name='orders')
urlpatterns += router.urls


# ---------------权限表管理--------------
router = DefaultRouter()
router.register('permission/perms', permission.PermissionView, base_name='perms')
urlpatterns += router.urls


router = DefaultRouter()
# 分组表管理
router.register('permission/groups', groups.GroupView, base_name='groups')
# 管理员管理
router.register('permission/admins', admins.AdminView, base_name='admins')
# 规格选项管理
router.register('specs/options', options.SpecificationOptionView, base_name='options')
# 商品频道
router.register('goods/channels', channels.GoodsChannelView, base_name='channels')
# 商品品牌
router.register('goods/brands', brands.BrandChannelView, base_name='brands')
# SPU表
router.register('goods', spus.SPUView, base_name='goods')
urlpatterns += router.urls
