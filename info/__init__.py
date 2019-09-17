import logging
from logging.handlers import RotatingFileHandler
from redis import StrictRedis
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
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
# 创建 redis 存储对象（后续在create_app函数内部，传入地址和端口，完成初始化）
redis_store = None  # type: StrictRedis  # py3.6添加新功能 --- 确保视图函数调用有智能提示！


def setup_log(environment):
    """配置日志"""
    # 设置日志的记录等级
    logging.basicConfig(level=config[environment].LOG_LEVEL)  # 调试debug级
    # 创建日志记录器，指明日志保存的路径、每个日志文件的最大大小、保存的日志文件个数上限
    file_log_handler = RotatingFileHandler("logs/log", maxBytes=1024 * 1024 * 100, backupCount=10)
    # 创建日志记录的格式 日志等级 输入日志信息的文件名 行数 日志信息
    formatter = logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')
    # 为刚创建的日志记录器设置日志记录格式
    file_log_handler.setFormatter(formatter)
    # 为全局的日志工具对象（flask app使用的）添加日志记录器
    logging.getLogger().addHandler(file_log_handler)


def create_app(environment):
    # 配置日志，传入环境名称，以便获取该环境配置中相应的日志等级
    setup_log(environment)
    # 创建Flask对象
    app = Flask(__name__)
    # 加载配置
    app.config.from_object(config[environment])
    # 传入app当参数，完成db初始化
    db.init_app(app)
    # 为redis对象指定地址和端口，完成redis对象初始化
    global redis_store
    redis_store = StrictRedis(host=config[environment].REDIS_HOST,
                              port=config[environment].REDIS_PORT)
    # 开启当前项目 CSRF 保护（只做验证，cookie中csrf_token和表单中csrf_token需要手动实现）
    CSRFProtect(app)
    # 设置用Session将 app 中数据保存到指定位置
    Session(app)
    # 注册网站首页蓝图。hint：蓝图在注册前的导入命令切勿置顶！否则会陷入import死循环！最好紧挨着注册行导入！
    from info.modules.index import index_blu
    app.register_blueprint(index_blu)
    # 注册登录注册模块的蓝图
    from info.modules.passport import passport_blu
    app.register_blueprint(passport_blu)
    return app  # 保留db在函数内 & “return app, db” --- 同样奏效

