# 1.导入蓝图包
from flask import Blueprint

# 2.创建蓝图对象
index_blu = Blueprint("index", __name__)

# 4.将用蓝图注册路由装饰过的视图函数导回
from . import views

# 5.将蓝图注册添加到create_app函数中

