from flask import current_app, g, redirect, render_template, request, jsonify
from info import constants
from info.modules.profile import profile_blu
from info.utils.common import user_login_data
from info.utils.image_storage import storage
from info.utils.response_code import RET


@profile_blu.route('/pass_info', methods=["GET", "POST"])
@user_login_data
def pass_info():
    if request.method == "GET":
        return render_template("news/user_pass_info.html")
    elif request.method == "POST":
        old_password = request.json.get("old_password", None)
        new_password = request.json.get("new_password", None)
        if not all([old_password, new_password]):
            return jsonify(errno=RET.PARAMERR, errmsg="参数错误")
        if old_password == new_password:
            return jsonify(errno=RET.PARAMERR, errmsg="新旧密码相同")
        user = g.user
        if not user.check_password(old_password):
            return jsonify(errno=RET.PWDERR, errmsg="原密码校验失败")
        user.password = new_password
        return jsonify(errno=RET.OK, errmsg="密码修改成功")











@profile_blu.route('/pic_info', methods=["GET", "POST"])
@user_login_data
def pic_info():
    user = g.user
    if request.method == "GET":
        return render_template("news/user_pic_info.html", data={"user":user.to_dict()})
    elif request.method == "POST":
        # 1. 获取图片
        try:
            avatar = request.files.get("avatar").read()  # 修改头像页面，点击保存按钮触发post请求，通过request获得用户上传的图片
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.PARAMERR, errmsg="参数错误")
        # 2. 上传图片
        try:
            key = storage(avatar)
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.THIRDERR, errmsg="文件上传七牛云失败")
        # 3. 更新当前用户avatar_url字段为相对路径，返回绝对路径供前端使用（更新多处头像）
        user.avatar_url = key
        data = {
            "avatar_url": constants.QINIU_DOMIN_PREFIX + key
        }
        return jsonify(errno=RET.OK, errmsg="文件上传成功", data=data)


@profile_blu.route('/base_info', methods=["GET", "POST"])
@user_login_data
def base_info():
    user = g.user
    if request.method == "GET":
        return render_template("news/user_base_info.html", data={"user": user.to_dict()})
    elif request.method == "POST":
        nick_name = request.json.get("nick_name", None)
        signature = request.json.get("signature", None)
        gender = request.json.get("gender", None)
        if not all([nick_name, signature]) or gender not in ["MAN", "WOMAN"]:
            return jsonify(errno=RET.PARAMERR, errmsg="参数错误")
        user.nick_name = nick_name
        user.signature = signature
        user.gender = gender
        return jsonify(errno=RET.OK, errmsg="个人基本信息修改成功")


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

