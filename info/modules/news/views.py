from flask import current_app, render_template, session
from info import constants
from info.models import User, News
from info.modules.news import news_blu


@news_blu.route('/<int:news_id>')  # int冒号后不能加空格！！
def news_detail(news_id):
    # 右上角功能区的实现：【登录/注册】or【用户头像/昵称/退出】
    user_id = session.get("user_id", None)  # 尝试获取当前登录用户的user_id
    user = None  # 先定义，保证后续data中的使用不会报 undefined error
    if user_id:
        try:
            user = User.query.get(user_id)  # 通过 user_id 获取用户信息
        except Exception as e:
            current_app.logger.error(e)
    # 右侧新闻点击排行功能的实现
    top_click_news = []
    try:
        top_click_news = News.query.order_by(News.clicks.desc()).limit(constants.CLICK_RANK_MAX_NEWS)
    except Exception as e:
        current_app.logger.error(e)
    top_click_news = [news.to_basic_dict() for news in top_click_news]  # 每条新闻从对象转字典，方便前端调用
    # 把数据进行汇总，当参数传给模板，供渲染时使用
    data = {
        "user": user.to_dict() if user else None,  # 将user转为字典形式传给前端html模板，供 js 分支判断使用
        "top_click_news": top_click_news,
    }
    return render_template('news/detail.html', data=data)

