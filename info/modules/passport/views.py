import random, re
from flask import abort, current_app, request, make_response, jsonify
from info import constants, redis_store
from info.libs.yuntongxun.sms import CCP
from info.utils.captcha.captcha import captcha
from info.utils.response_code import RET
from . import passport_blu


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

