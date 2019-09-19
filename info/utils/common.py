# 公用的自定义工具类
import functools
from flask import current_app, session, g
from info.models import User


def do_index_class(index):
    """为点击排行class自定义过滤器"""
    if index == 1:
        return "first"
    elif index == 2:
        return "second"
    elif index == 3:
        return "third"
    else:
        return ""


# 自定义装饰器，装饰视图函数，代替视图函数内部【查询数据库获取已登录用户信息】功能，简化代码！
def user_login_data(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        user_id = session.get("user_id", None)  # 尝试获取当前登录用户的user_id
        user = None  # 先定义，保证后续data中的使用不会报 undefined error
        if user_id:
            try:
                user = User.query.get(user_id)  # 通过 user_id 获取用户信息
            except Exception as e:
                current_app.logger.error(e)
        g.user = user  # 获得的已登录用户的用户对象，存储在应用上下文变量【g变量】中！
        return func(*args, **kwargs)
    return wrapper

