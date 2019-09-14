from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from redis import StrictRedis
from flask.ext.wtf import CSRFProtect
from flask_session import Session
# flask中有一个大写Session，还有一个小写session，这三个各不相同
# flask中Session --- 将浏览器来的数据加密存cookie返回浏览器，浏览器下次带cookie来再解密
# flask中session --- 用于在视图函数中作为键值对的字典名，如session["name"] = "laowang"
# flask_session中Session --- 可以指定数据保存位置，如redis/sqlalchemy/mongodb/memcached等
from config import config


# 初始化 SQL 数据库
# Flask中很多扩展都可以先创建扩展对象，然后等初始化所需参数出现后，再调用init_app方法完成初始化
db = SQLAlchemy()


def create_app(environment):
    app = Flask(__name__)
    # 加载配置
    app.config.from_object(config[environment])

    # 传入app当参数，完成db初始化
    db.init_app(app)

    # 初始化 redis 存储对象
    redis_store = StrictRedis(host=config[environment].REDIS_HOST,
                              port=config[environment].REDIS_PORT)
    # 开启当前项目 CSRF 保护（只做验证，cookie中csrf_token和表单中csrf_token需要手动实现）
    CSRFProtect(app)
    # 设置用Session将 app 中数据保存到指定位置
    Session(app)

    return app  # 保留db在函数内 & “return app, db” --- 同样奏效

