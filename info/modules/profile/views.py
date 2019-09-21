from flask import g, redirect, render_template
from info.modules.profile import profile_blu
from info.utils.common import user_login_data


@profile_blu.route('/info')
@user_login_data
def user_info():
    user = g.user
    if not user:
        return redirect("/")  # 用户未登录，重定向到主页
    data = {
        "user": user.to_dict()
    }
    return render_template("news/user.html", data=data)

