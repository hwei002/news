# 后台管理 admin 模块的蓝图

from flask import Blueprint, redirect, request, session, url_for

# url前缀也可在将蓝图注册进app时添加
admin_blu = Blueprint("admin", __name__)

from . import views


@admin_blu.before_request
def check_admin():
    if not request.url.endswith(url_for("admin.login")):  # 加上此行，否则后台登录页面都打不开！！
        is_admin = session.get("is_admin", False)
        if not is_admin:
            return redirect("/")

