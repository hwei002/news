from redis import StrictRedis


class Config(object):
    """项目的所有配置"""
    DEBUG = True

    # 为 SQL 数据库添加配置
    SQLALCHEMY_DATABASE_URI = "mysql://root:mysql@127.0.0.1:3306/news"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # 为 redis 数据库添加配置
    REDIS_HOST = "127.0.0.1"
    REDIS_PORT = 6379

    # 设置Session：指定浏览器数据保存位置为 redis，并配置所需参数
    SESSION_TYPE = "redis"
    SESSION_REDIS = StrictRedis(host=REDIS_HOST, port=REDIS_PORT)  # 指定保存用的redis对象
    SESSION_USE_SIGNER = True  # 开启session签名（session使用签名，提高加密性）
    SESSION_PERMANENT = False  # 设置session需要过期（取消其默认的永不过期）
    PERMANENT_SESSION_LIFETIME = 86400 * 2  # 设置过期时间为 2 天（默认是 31 天）
    SECRET_KEY = "HfQ/Co3pMKAlEml4wlbbBgIoGoFhQUU922Hh7dq4d51YZCislqBKyHBjTXf+74Lk"

