from flask import current_app
from qiniu import Auth, put_data

access_key = 'xxxxxxxx'
secret_key = 'xxxxxxxx'
bucket_name = 'xxxxxx'  # 七牛云空间参数（需实名认证才可申请空间）


def storage(data):
    """七牛云存储上传文件接口，data不为空，传进来前已验证"""
    try:
        q = Auth(access_key, secret_key) # 构建鉴权对象
        token = q.upload_token(bucket_name)  # 生成上传 Token，可以指定过期时间等
        ret, info = put_data(token, None, data) # 上传文件
    except Exception as e:
        current_app.logger.error(e)
        raise e
    if not info or info.status_code != 200:
        raise Exception("上传文件到七牛云失败")
    return ret["key"]  # 返回七牛云中该图片对应的key，访问七牛云获取图片需用对应的key


if __name__ == '__main__':
    path = input("请提供需上传的本地文件路径：")
    with open(path, "rb") as f:
        storage(f.read())

