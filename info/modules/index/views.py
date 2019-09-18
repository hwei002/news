# 3.导入蓝图对象，并用它注册路由，装饰视图函数
from info.models import User
from flask import render_template, current_app, session
from . import index_blu


@index_blu.route('/')
def index():

    user_id = session.get("user_id", None)  # 尝试获取当前登录用户的user_id

    user = None  # 先定义，保证后续data中的使用不会报 undefined error
    if user_id:
        try:
            user = User.query.get(user_id)  # 通过 user_id 获取用户信息
        except Exception as e:
            current_app.logger.error(e)

    data = {
        "user": user.to_dict() if user else None  # 将user转为字典形式传给前端html模板，供 js 分支判断使用
    }

    return render_template('news/index.html', data=data)


# 在打开网页时，浏览器会默认去请求【根路径+favicon.ico】作为网站标签的小图标
# send_static_file是flask提供的查找指定静态文件的方法
@index_blu.route('/favicon.ico')
def favicon():
    return current_app.send_static_file('news/favicon.ico')
