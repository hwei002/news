import logging
from logging.handlers import RotatingFileHandler
from redis import StrictRedis
from flask import Flask, g, render_template
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.wtf import CSRFProtect
from flask.ext.wtf.csrf import generate_csrf
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
                              port=config[environment].REDIS_PORT,
                              decode_responses=True)  # redis中取出的value默认binary格式，设置解码将其转换回string。

    # 添加自定义过滤器
    from info.utils.common import do_index_class
    app.add_template_filter(do_index_class, "index_class")

    # 开启当前项目 CSRF 保护（只做验证，cookie中csrf_token和表单中csrf_token需要手动实现）
    CSRFProtect(app)
    # 上一行帮我们做了：从cookie中取出随机值，从表单中取出随机值，然后校验，并响应校验结果
    # 我们还需要做：
    # 1. 在返回响应时往cookie中添加一个csrf_token。
    # 2. 在表单中添加隐藏的csrf_token。因我们现在使用的是ajax请求，而非传统表单，故需在ajax请求时，带上csrf_token随机值。

    from info.utils.common import user_login_data  # 用之前再导入，否则循环导入报错

    @app.errorhandler(404)  # 统一捕获所有404，并返回自定义404页面
    @user_login_data
    def page_not_found(e):  # e 接收报错传入的参数“404 NOT FOUND”
        user = g.user
        data = {
            "user": user.to_dict() if user else None
        }
        return render_template("news/404.html", data=data)

    @app.after_request
    def after_request(response):
        csrf_token = generate_csrf()  # flask.ext.wtf.csrf中一个模块，用于专门生成csrf_token值
        response.set_cookie("csrf_token", csrf_token)
        return response

    # 设置用Session将 app 中数据保存到指定位置
    Session(app)

    # 注册网站首页蓝图。导入蓝图小心import死循环！紧挨着注册行导入！
    from info.modules.index import index_blu
    app.register_blueprint(index_blu)

    # 注册登录注册模块的蓝图
    from info.modules.passport import passport_blu
    app.register_blueprint(passport_blu)

    # 注册新闻模块的蓝图
    from info.modules.news import news_blu
    app.register_blueprint(news_blu)

    # 注册用户profile模块的蓝图
    from info.modules.profile import profile_blu
    app.register_blueprint(profile_blu)

    # 注册后台管理admin模块的蓝图
    from info.modules.admin import admin_blu
    app.register_blueprint(admin_blu, url_prefix="/admin")

    return app

