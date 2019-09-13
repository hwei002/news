from flask import Flask, session
from flask.ext.sqlalchemy import SQLAlchemy
from redis import StrictRedis
from flask.ext.wtf import CSRFProtect
from flask_session import Session
# flask中有一个大写Session，还有一个小写session，这三个各不相同
# flask中Session --- 将浏览器来的数据加密存cookie返回浏览器，浏览器下次带cookie来再解密
# flask中session --- 用于在视图函数中作为键值对的字典名，如session["name"] = "laowang"
# flask_session中Session --- 可以指定数据保存位置，如redis/sqlalchemy/mongodb/memcached等


class Config(object):
    """项目的所有配置"""
    DEBUG = True

    # 为 SQL 数据库添加配置
    SQLALCHEMY_DATABASE_URI = "mysql://root:mysql@127.0.0.1:3306/news"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # 为 redis 数据库添加配置
    REDIS_HOST = "127.0.0.1"
    REDIS_PORT = 6379

    # 指定浏览器数据保存位置为 redis，并配置所需参数
    SESSION_TYPE = "redis"
    SESSION_REDIS = StrictRedis(host=REDIS_HOST, port=REDIS_PORT)  # 指定保存用的redis对象
    SESSION_USE_SIGNER = True  # 开启session签名（session使用签名，提高加密性）
    SESSION_PERMANENT = False  # 设置session需要过期（取消其默认的永不过期）
    PERMANENT_SESSION_LIFETIME = 86400 * 2  # 设置过期时间为 2 天（默认是 31 天）
    SECRET_KEY = "HfQ/Co3pMKAlEml4wlbbBgIoGoFhQUU922Hh7dq4d51YZCislqBKyHBjTXf+74Lk"

app = Flask(__name__)
# 加载配置
app.config.from_object(Config)
# 初始化 SQL 数据库
db = SQLAlchemy(app)
# 初始化 redis 存储对象
redis_store = StrictRedis(host=Config.REDIS_HOST, port=Config.REDIS_PORT)
# 开启当前项目 CSRF 保护（只做验证，cookie中csrf_token和表单中csrf_token需要手动实现）
CSRFProtect(app)
# 设置用Session将 app 中数据保存到指定位置
Session(app)


@app.route('/')
def index():
    session["name"] = "laowang"
    return 'index'


if __name__ == '__main__':
    app.run()

