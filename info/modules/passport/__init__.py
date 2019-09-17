# 登录和注册模块的所有视图函数在此package内实现

from flask import Blueprint

passport_blu = Blueprint("passport", __name__, url_prefix="/passport")

from . import views
