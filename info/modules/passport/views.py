from flask import abort, current_app, request
from flask import make_response

from info import constants, redis_store
from info.utils.captcha.captcha import captcha
from . import passport_blu


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
