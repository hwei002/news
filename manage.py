from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy


class Config(object):
    """项目的所有配置"""
    DEBUG = True
    # 为SQL数据库添加配置
    SQLALCHEMY_DATABASE_URI = "mysql://root:mysql@127.0.0.1:3306/news"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

app = Flask(__name__)
app.config.from_object(Config)  # 加载配置
db = SQLAlchemy(app)  # 初始化数据库


@app.route('/')
def index():
    return 'index'


if __name__ == '__main__':
    app.run()

