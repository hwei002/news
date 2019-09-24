from flask.ext.script import Manager
from flask.ext.migrate import Migrate, MigrateCommand

# app/sql/redis/csrf/session属业务逻辑，放info包。
# 后续static/js/css以及其他代码都放info，而manage仅当程序入口
from info import create_app, db
from info.models import User


# manage.py是程序启动入口，只关心启动的相关参数以及内容，
# 不关心具体该如何创建app或者具体该如何实现相关业务逻辑
app = create_app("development")
# 设置Flask-Script，用命令行运行【python manage.py runserver】
manager = Manager(app)
# 设置Migrate数据库迁移功能：关联 app 与 db，并把迁移命令添加到Script
Migrate(app, db)
manager.add_command('db', MigrateCommand)


# 将函数定义为命令行可用函数的方法————用装饰器指定命令行传入参数是哪个形参！！
@manager.option("-n", "-name", dest="name")  # 指定命令行传入的参数对应的形参
@manager.option("-p", "-password", dest="password")  # 同上
def createsuperuser(name, password):  # 创建管理员账号
    if not all([name, password]):
        print("参数不能为空")
    else:
        user = User()
        user.nick_name = name
        user.mobile = name
        user.password = password
        user.is_admin = True
        try:
            db.session.add(user)
            db.session.commit()
            print("添加成功")
        except Exception as e:
            db.session.rollback()
            print(e)


if __name__ == '__main__':
    manager.run()

