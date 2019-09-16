# 3.导入蓝图对象，并用它注册路由，装饰视图函数
from . import index_blu
from info import redis_store


@index_blu.route('/')
def index():
    redis_store.set("name", "laowang")  # 直接set，保存到redis中的数据是明文
    # session["name"] = "laowang"  # 用session，保存到redis中的数据会自动加密

    # 测试打印日志
    # logging.debug('测试debug')
    # logging.info('测试info')
    # logging.warning('测试warning')
    # logging.error('测试error')
    # logging.fatal('测试fatal')

    # Flask框架封装logging --> 美化输出 & logger能根据app是否debug自动调整日志等级
    # current_app.logger.debug('测试debug')
    # current_app.logger.info('测试info')
    # current_app.logger.warning('测试warning')
    # current_app.logger.error('测试error')
    # current_app.logger.fatal('测试fatal')

    return 'index'


