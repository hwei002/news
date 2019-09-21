# 用户profile详情模块的蓝图

from flask import Blueprint

profile_blu = Blueprint("profile", __name__, url_prefix="/user")

from . import views

