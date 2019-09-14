from flask import Flask, session
from flask.ext.sqlalchemy import SQLAlchemy
from redis import StrictRedis
from flask.ext.wtf import CSRFProtect
from flask_session import Session
# flask中有一个大写Session，还有一个小写session，这三个各不相同
# flask中Session --- 将浏览器来的数据加密存cookie返回浏览器，浏览器下次带cookie来再解密
# flask中session --- 用于在视图函数中作为键值对的字典名，如session["name"] = "laowang"
# flask_session中Session --- 可以指定数据保存位置，如redis/sqlalchemy/mongodb/memcached等
from flask.ext.script import Manager
from flask.ext.migrate import Migrate, MigrateCommand
from config import Config


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
# 设置Flask-Script，用命令行运行【python manage.py runserver】
manager = Manager(app)
# 设置Migrate数据库迁移功能：关联 app 与 db，并把迁移命令添加到Script
Migrate(app, db)
manager.add_command('db', MigrateCommand)


@app.route('/')
def index():
    session["name"] = "laowang"
    return 'index'


if __name__ == '__main__':
    manager.run()

