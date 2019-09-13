from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from redis import StrictRedis
from flask.ext.wtf import CSRFProtect


class Config(object):
    """项目的所有配置"""
    DEBUG = True
    # 为 SQL 数据库添加配置
    SQLALCHEMY_DATABASE_URI = "mysql://root:mysql@127.0.0.1:3306/news"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # 为 redis 数据库添加配置
    REDIS_HOST = "127.0.0.1"
    REDIS_PORT = 6379

app = Flask(__name__)
# 加载配置
app.config.from_object(Config)
# 初始化 SQL 数据库
db = SQLAlchemy(app)
# 初始化 redis 存储对象
redis_store = StrictRedis(host=Config.REDIS_HOST, port=Config.REDIS_PORT)
# 开启当前项目 CSRF 保护（只做服务器验证功能，源代码显示用请求勾子before_request实现）
CSRFProtect(app)


@app.route('/')
def index():
    return 'index'


if __name__ == '__main__':
    app.run()

