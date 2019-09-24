# 后台管理 admin 模块的蓝图

from flask import Blueprint

# url前缀也可在将蓝图注册进app时添加
admin_blu = Blueprint("admin", __name__)

from . import views

