import pickle

import base64
from django_redis import get_redis_connection


def get_carts(request,response,user):
    """
        合并购物车
    :return:
    """
    # 1、获取cookie数据
    cart_cookie = request.COOKIES.get('cart_cookie')
    if not cart_cookie:
        return response
    # 2、解密cookie获取购车数据 {}
    data_dict = pickle.loads(base64.b64decode(cart_cookie))
    # 3、判断购物车数据是存在  {sku_id:{count:2,selected:True}}
    if data_dict is None:
        return response
    # 4、拆分购物车数据 形成hash和set形式方便保存在reids中
    cart_dict = {}  # hash
    cart_list = []  # 选中状态的sku_id列表
    cart_list_none = []  # 未选中状态的sku_id列表
    for sku_id, sku_data in data_dict.items():
        cart_dict[sku_id] = sku_data['count']
        if sku_data['selected']:
            # 获取选中状态
            cart_list.append(sku_id)
        else:
            cart_list_none.append(sku_id)

    # 5、写入redis
    client = get_redis_connection('carts')
    # 写入hash
    client.hmset('carts_%s' % user.id, cart_dict)
    if cart_list:
        # cart_list存储的是需要选中的sku_id,所以需要全部添加到集合
        client.sadd('carts_selected_%d' % user.id, *cart_list)
    if cart_list_none:
        # cart_list存储的是未选中的sku_id,所以需要全部从集合删除
        client.srem('carts_selected_%d' % user.id, *cart_list_none)
    # 6、删除cookie
    response.delete_cookie('cart_cookie')
    return response