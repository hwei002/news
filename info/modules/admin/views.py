from flask import current_app, redirect, render_template, request, session, g
from datetime import datetime
from info.models import User
from info.utils.common import user_login_data
from . import admin_blu


@admin_blu.route('/index')
@user_login_data
def index():  # 访问任一后台管理页面，均需查验is_admin。每个视图函数都查验，不如统一写进before_request钩子
    user = g.user
    return render_template("admin/index.html", user=user.to_dict())


@admin_blu.route('/login', methods=["GET", "POST"])
def login():
    if request.method=="GET":
        user_id = session.get("user_id", None)
        is_admin = session.get("is_admin", None)
        if user_id and is_admin:  # 如果已登录且是管理员，自动跳转到管理员首页
            return redirect("/admin/index")
        else:
            return render_template("admin/login.html", errmsg=None)
    else:
        username = request.form.get("username", None)
        password = request.form.get("password", None)
        if not all([username, password]):
            return render_template("admin/login.html", errmsg="参数不能为空")
        try:
            user = User.query.filter(User.mobile==username,
                                     User.is_admin==1).first()
        except Exception as e:
            current_app.logger.error(e)
            return render_template("admin/login.html", errmsg="数据库查询出错")
        if not user:
            return render_template("admin/login.html", errmsg="该管理员账户不存在")
        if not user.check_password(password):
            return render_template("admin/login.html", errmsg="用户名或密码错误")
        session["user_id"] = user.id   # 保存登录状态到session中
        session["mobile"] = user.mobile
        session["nick_name"] = user.nick_name
        session["is_admin"] = user.is_admin
        user.last_login = datetime.now()  # 更新用户最近一次登录时间
        return redirect("/admin/index")







