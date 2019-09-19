# 3.导入蓝图对象，并用它注册路由，装饰视图函数
from flask import render_template, current_app, request, jsonify, g
from info import constants
from info.models import News, Category
from info.utils.common import user_login_data
from info.utils.response_code import RET
from . import index_blu


@index_blu.route('/news_list')
def news_list():

    # 1. 获取url中？后面的参数：新闻分类cid，页码page，每页条数per_page
    cid = request.args.get("cid", "1")
    page = request.args.get("page", "1")
    per_page = request.args.get("per_page", constants.HOME_PAGE_MAX_NEWS)

    # 2. 校验参数
    try:
        cid = int(cid)
        page = int(page)
        per_page = int(per_page)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    # 3. 查询数据
    filters = [News.category_id==cid] if cid != 1 else []  # cid=1表示“最新”新闻，无需过滤。。。而cid=2,3,4……才需要过滤
    try:
        paginate = News.query.filter(*filters).order_by(News.create_time.desc()).paginate(page, per_page, False)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据查询错误")

    # 4. 通过paginate对象获取：当前页码、总页数、当前页的所有新闻列表
    current_page = paginate.page
    total_page = paginate.pages
    current_page_news = paginate.items
    current_page_news = [news.to_basic_dict() for news in current_page_news]

    # 5. 生成数据并返回
    data = {
        "current_page": current_page,
        "total_page": total_page,
        "current_page_news": current_page_news,
    }

    return jsonify(errno=RET.OK, errmsg="OK", data=data)


@index_blu.route('/')
@user_login_data
def index():
    # 右上角功能区的实现：【登录/注册】or【用户头像/昵称/退出】
    # user_id = session.get("user_id", None)  # 尝试获取当前登录用户的user_id
    # user = None  # 先定义，保证后续data中的使用不会报 undefined error
    # if user_id:
    #     try:
    #         user = User.query.get(user_id)  # 通过 user_id 获取用户信息
    #     except Exception as e:
    #         current_app.logger.error(e)
    user = g.user

    # 右侧新闻点击排行功能的实现
    top_click_news = []
    try:
        top_click_news = News.query.order_by(News.clicks.desc()).limit(constants.CLICK_RANK_MAX_NEWS)
    except Exception as e:
        current_app.logger.error(e)
    top_click_news = [news.to_basic_dict() for news in top_click_news]  # 每条新闻从对象转字典，方便前端调用

    # 左侧新闻列表的实现由【'/news_list'】路由实现
    # 顶端新闻分类功能的实现
    categories = []
    try:
        categories = Category.query.all()
    except Exception as e:
        current_app.logger.error(e)
    categories = [category.to_dict() for category in categories]

    # 把数据进行汇总，当参数传给模板，供渲染时使用
    data = {
        "user": user.to_dict() if user else None,  # 将user转为字典形式传给前端html模板，供 js 分支判断使用
        "top_click_news": top_click_news,
        "categories": categories,
    }
    return render_template('news/index.html', data=data)


# 在打开网页时，浏览器会默认去请求【根路径+favicon.ico】作为网站标签的小图标
# send_static_file是flask提供的查找指定静态文件的方法
@index_blu.route('/favicon.ico')
def favicon():
    return current_app.send_static_file('news/favicon.ico')
