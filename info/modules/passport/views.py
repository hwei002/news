import random, re
from datetime import datetime
from flask import abort, current_app, request, make_response, jsonify, session
from info import constants, redis_store, db
from info.libs.yuntongxun.sms import CCP
from info.models import User
from info.utils.captcha.captcha import captcha
from info.utils.response_code import RET
from . import passport_blu


@passport_blu.route('/register', methods=['POST'])
def register():

    # 1. 获取参数（用户手机号、短信验证码、用户所输密码）
    params_dict = request.json
    mobile, smscode, password = params_dict["mobile"], params_dict["smscode"], params_dict["password"]

    # 2. 校验参数是否为空（手机号格式之前已校验过，此处可略）
    if not all([mobile, smscode, password]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    # 3. 读取redis中真实的短信验证码内容
    try:
        real_smscode = redis_store.get("SMS_"+mobile)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据查询失败")
    if not real_smscode:
        return jsonify(errno=RET.NODATA, errmsg="验证码已过期")

    # 4. 校验用户输入验证码是否正确
    if real_smscode != smscode:
        return jsonify(errno=RET.DATAERR, errmsg="验证码输入错误")

    # 5. 如果正确，初始化User模型，并且赋值属性
    user = User()
    user.mobile = mobile
    user.nick_name = mobile  # 暂时没有昵称，用手机号代替
    user.last_login = datetime.now()  # 用时间戳记录用户最近一次登陆时间
    # 对密码进行加密处理，用property装饰器，把password方法伪装成password属性。
    user.password = password  # 在password.setter中将加密后的密码赋值给user.password_hash。

    # 6. 添加到数据库
    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="数据保存失败")

    # 7. 往session中保存数据表示当前已经登录
    session["user_id"] = user.id
    session["mobile"] = user.mobile
    session["nick_name"] = user.nick_name

    # 8. 返回响应
    return jsonify(errno=RET.OK, errmsg="注册成功")


@passport_blu.route('/sms_code', methods=['POST'])
def send_sms_code():

    # return jsonify(errno=RET.OK, errmsg="发送成功")  # 打开此行，测试手机验证码发送后填写时间倒计时功能是否奏效。

    # 1. 获取参数：用户手机号、用户输入的图片验证码、图片验证码的id
    params_dict = request.json  # 等价于 josn.loads(request.data)
    mobile, image_code, image_code_id = params_dict["mobile"], params_dict["image_code"], params_dict["image_code_id"]

    # 2. 校验是否有空值，以及可能的手机号格式错误
    if not all ([mobile, image_code, image_code_id]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数有误")
    if not re.match("^1[35678][0-9]{9}$", mobile):
        return jsonify(errno=RET.PARAMERR, errmsg="手机号格式不正确")

    # 3. 从redis中取出真实验证码内容
    try:
        real_image_code = redis_store.get("ImageCodeId_" + image_code_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据查询失败")
    if not real_image_code:
        return jsonify(errno=RET.NODATA, errmsg="图片验证码已过期")

    # 4. 与用户所输入的验证码对比，如果不一致，返回验证码输入错误
    if real_image_code.upper() != image_code.upper():
        return jsonify(errno=RET.DATAERR, errmsg="验证码输入错误")

    # 5. 生成短信验证码内容，随机6位数字符串
    sms_code_str = "%06d" % random.randint(0, 999999)
    # print(sms_code_str)  # 确保容联云代码无误后，开发时用这三行，可跳过容联云仅能给指定手机发短信的限制，测试注册成功后自动跳转
    # redis_store.set('SMS_' + mobile, sms_code_str, constants.SMS_CODE_REDIS_EXPIRES)
    # return jsonify(errno=RET.OK, errmsg="发送成功")

    # 6. 发送短信验证码
    result = CCP().send_template_sms(mobile, [sms_code_str, constants.SMS_CODE_REDIS_EXPIRES//60], 1)
    if result != 0:
        return jsonify(errno=RET.THIRDERR, errmsg="发送短信失败")

    # 7. 保存验证码内容到redis
    try:
        redis_store.set('SMS_' + mobile, sms_code_str, constants.SMS_CODE_REDIS_EXPIRES)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据保存失败")

    # 8. 告知结果
    return jsonify(errno=RET.OK, errmsg="发送成功")


@passport_blu.route('/image_code')
def get_image_code():

    # 1.取出imageCodeId
    image_code_id = request.args.get("imageCodeId", None)  # args取到url中？后面的参数

    # 2.判断imageCodeId是否为空，空则abort出错
    if not image_code_id:
        return abort(403)

    # 3.生成验证码，得到text和image
    name, text, image = captcha.generate_captcha()  # generate返回长度为3的tuple，第一个参数可忽略

    # 4.将imageCodeId和text存入redis
    try:
        redis_store.set('ImageCodeId_'+image_code_id, text, ex=constants.IMAGE_CODE_REDIS_EXPIRES)
    except Exception as e:
        current_app.logger.error(e)  # 将错误信息写入日志文件
        abort(500)  # 按照约定俗成自定义错误码：一般5开头的都是服务器出错

    # 5.返回image。如果直接return image，返回数据类型默认text/html，Chrome较智能可以解析出来，但其他浏览器会失败
    response = make_response(image)
    response.headers["Content-Type"] = "image/jpg"
    return response

