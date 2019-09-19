from flask import current_app, render_template, g, abort
from info import constants
from info.models import News
from info.modules.news import news_blu
from info.utils.common import user_login_data


@news_blu.route('/<int:news_id>')  # int冒号后不能加空格！！
@user_login_data
def news_detail(news_id):

    # 右上角功能区的实现：【登录/注册】or【用户头像/昵称/退出】
    user = g.user

    # 右侧新闻点击排行功能的实现
    top_click_news = []
    try:
        top_click_news = News.query.order_by(News.clicks.desc()).limit(constants.CLICK_RANK_MAX_NEWS)
    except Exception as e:
        current_app.logger.error(e)
    top_click_news = [news.to_basic_dict() for news in top_click_news]  # 每条新闻从对象转字典，方便前端调用

    # 新闻主体部分的展示
    news = None
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
    if not news:
        abort(404)  # 数据未找到有一个统一的404页面，后续再去实现此功能
    news.clicks += 1  # 更新点击次数

    # 把数据进行汇总，当参数传给模板，供渲染时使用
    data = {
        "user": user.to_dict() if user else None,  # 将user转为字典形式传给前端html模板，供 js 分支判断使用
        "top_click_news": top_click_news,
        "news": news.to_dict(),
    }
    return render_template('news/detail.html', data=data)

