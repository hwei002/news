import logging
from flask import session, current_app
from flask.ext.script import Manager
from flask.ext.migrate import Migrate, MigrateCommand
# app/sql/redis/csrf/session属业务逻辑，放info包。
# 后续static/js/css以及其他代码都放info，而manage仅当程序入口
from info import create_app, db


app = create_app("development")
# 设置Flask-Script，用命令行运行【python manage.py runserver】
manager = Manager(app)
# 设置Migrate数据库迁移功能：关联 app 与 db，并把迁移命令添加到Script
Migrate(app, db)
manager.add_command('db', MigrateCommand)


@app.route('/')
def index():
    session["name"] = "laowang"
    # 测试打印日志
    logging.debug('测试debug')
    logging.info('测试info')
    logging.warning('测试warning')
    logging.error('测试error')
    logging.fatal('测试fatal')
    # Flask框架封装logging --> 美化输出 & logger能根据app是否debug自动调整日志等级
    current_app.logger.debug('测试debug')
    current_app.logger.info('测试info')
    current_app.logger.warning('测试warning')
    current_app.logger.error('测试error')
    current_app.logger.fatal('测试fatal')
    return 'index'


if __name__ == '__main__':
    manager.run()

