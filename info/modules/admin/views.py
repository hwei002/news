import time
from flask import current_app, redirect, render_template, request, session, g, jsonify
from datetime import datetime, timedelta
from info import constants
from info.models import User, News, Category
from info.utils.common import user_login_data
from info.utils.image_storage import storage
from info.utils.response_code import RET
from . import admin_blu


@admin_blu.route("/news_edit_detail", methods=["GET", "POST"])
def news_edit_detail():
    if request.method == "GET":  # 点击【编辑】按钮打开页面是GET请求，此时需将该条新闻内容返回前端供渲染显示！！！
        news_id = request.args.get("news_id", None)
        if not news_id:
            return render_template("admin/news_edit_detail.html", data={"errmsg": "news_id不能为空"})
        try:
            news_id = int(news_id)
        except Exception as e:
            current_app.logger.error(e)
            return render_template("admin/news_edit_detail.html", data={"errmsg": "news_id必须为整数"})
        try:
            news = News.query.get(news_id)
        except Exception as e:
            current_app.logger.error(e)
            return render_template("admin/news_edit_detail.html", data={"errmsg": "数据库查询失败"})
        if not news:
            return render_template("admin/news_edit_detail.html", data={"errmsg": "该id对应的新闻不存在"})
        try:
            categories = Category.query.all()  # 需将所有类别都返回供渲染，因管理员需要看到类别下拉框中的所有类别！
        except Exception as e:
            current_app.logger.error(e)
            return render_template("admin/news_edit_detail.html", data={"errmsg": "数据库查询失败"})
        categories_filtered = []
        for category in categories[1:]:  # 【最新】类别无需返回给前端
            category_dict = category.to_dict()
            category_dict["is_selected"] = False
            if category.id == news.category_id:  # 遍历类别时，如果某类别恰是该新闻所属类别，则为其标示【选中】
                category_dict["is_selected"] = True  # 前端渲染该新闻时，类别下拉框应默认显示该新闻当前所属类别！
            categories_filtered.append(category_dict)
        data = {
            "news": news.to_dict(),
            "categories": categories_filtered
        }
        return render_template("admin/news_edit_detail.html", data=data)
    else:  # 当管理员完成该新闻版式编辑，点击【提交】按钮是POST请求，此时需从前端取出各改后参数，并更新数据库中该新闻各属性！
        news_id = request.form.get("news_id", None)
        title = request.form.get("title", None)
        category_id = request.form.get("category_id", None)
        digest = request.form.get("digest", None)
        index_image = request.files.get("index_image", None)  # 此参数可以为空，表示仍使用原图片
        content = request.form.get("content", None)
        if not all([news_id, title, category_id, digest, content]):
            return jsonify(errno=RET.PARAMERR, errmsg="参数有误")
        try:
            news_id = int(news_id)
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.PARAMERR, errmsg="news_id必须为整数")
        try:
            news = News.query.get(news_id)
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR, errmsg="数据库查询失败")
        if not news:
            return jsonify(errno=RET.NODATA, errmsg="该id对应的新闻不存在")
        news.title = title
        news.category_id = category_id
        news.digest = digest
        news.content = content
        if index_image:  # 如果此参数有值，说明需要更换图片
            try:
                index_image = index_image.read()  # 先尝试读取图片
            except Exception as e:
                current_app.logger.error(e)
                return jsonify(errno=RET.PARAMERR, errmsg="参数有误")
            try:
                key = storage(index_image)  # 再将图片上传到七牛云
            except Exception as e:
                current_app.logger.error(e)
                return jsonify(errno=RET.THIRDERR, errmsg="上传图片失败")
            news.index_image_url = constants.QINIU_DOMIN_PREFIX + key
        return jsonify(errno=RET.OK, errmsg="新闻版式编辑成功")


@admin_blu.route("/news_edit")  # 除【url/视图函数名/filter内容/basic_dict/模板名】外，和news_review视图函数完全一样
def news_edit():
    page = request.args.get("page", 1)
    keywords = request.args.get("keywords", None)
    try:
        page = int(page)
    except Exception as e:
        current_app.logger.error(e)
        page = 1
    filters = [News.status == 0]  # 仅显示【审核通过】的新闻
    if keywords:
        filters.append(News.title.contains(keywords))
    try:
        paginate = News.query.filter(*filters).order_by(News.create_time.desc())\
                             .paginate(page, constants.ADMIN_NEWS_PAGE_MAX_COUNT, False)
        current_page = paginate.page
        total_page = paginate.pages
        current_page_news = paginate.items
    except Exception as e:
        current_app.logger.error(e)
        current_page = 1
        total_page = 1
        current_page_news = []
    context = {
        "current_page": current_page,
        "total_page": total_page,
        "current_page_news": [news.to_basic_dict() for news in current_page_news]
    }
    return render_template("admin/news_edit.html", data=context)


@admin_blu.route('/news_review_action', methods=["POST"])  # 两视图函数可合并，通过GET/POST区分彼此
def news_review_action():
    news_id = request.json.get("news_id", None)
    action = request.json.get("action", None)
    if not news_id or action not in ["accept", "reject"]:
        return jsonify(errno=RET.PARAMERR, errmsg="参数格式错误")
    try:
        news_id = int(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="news_id必须为整数")
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库查询失败")
    if not news:
        return jsonify(errno=RET.NODATA, errmsg="未查询到该id对应新闻")
    if action == "accept":
        news.status = 0
    else:
        reason = request.json.get("reason", None)
        if not reason:
            return jsonify(errno=RET.PARAMERR, errmsg="请输入审核未通过原因")
        news.status = -1
        news.reason = reason
    return jsonify(errno=RET.OK, errmsg="新闻审核完成")


@admin_blu.route('/news_review_detail/<int:news_id>')
def news_review_detail(news_id):
    try:
        news_id = int(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return render_template("admin/news_review_detail.html", data={"errmsg": "参数必须为整数"})
    news = None
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
    if not news:
        return render_template("admin/news_review_detail.html", data={"errmsg": "未查询到此新闻"})
    return render_template("admin/news_review_detail.html", data={"news": news.to_dict()})


@admin_blu.route("/news_review")
def news_review():
    page = request.args.get("page", 1)
    keywords = request.args.get("keywords", None)
    try:
        page = int(page)
    except Exception as e:
        current_app.logger.error(e)
        page = 1
    filters = [News.status != 0]  # 仅显示【审核中】和【审核未通过】的新闻
    if keywords:
        filters.append(News.title.contains(keywords))
    try:
        paginate = News.query.filter(*filters).order_by(News.create_time.desc())\
                             .paginate(page, constants.ADMIN_NEWS_PAGE_MAX_COUNT, False)
        current_page = paginate.page
        total_page = paginate.pages
        current_page_news = paginate.items
    except Exception as e:
        current_app.logger.error(e)
        current_page = 1
        total_page = 1
        current_page_news = []
    context = {
        "current_page": current_page,
        "total_page": total_page,
        "current_page_news": [news.to_review_dict() for news in current_page_news]
    }
    return render_template("admin/news_review.html", data=context)


@admin_blu.route("/user_list")
def user_list():
    page = request.args.get("page", 1)  # 对于用url传入参数的GET请求，使用args去获取参数
    try:
        page = int(page)
    except Exception as e:
        current_app.logger.error(e)
        page = 1
    try:
        paginate = User.query.filter(User.is_admin == False).order_by(User.last_login.desc())\
                             .paginate(page, constants.ADMIN_USER_PAGE_MAX_COUNT, False)
        current_page = paginate.page
        total_page = paginate.pages
        current_page_users = paginate.items
    except Exception as e:
        current_app.logger.error(e)
        current_page = 1
        total_page = 1
        current_page_users = []
    data = {
        "current_page": current_page,
        "total_page": total_page,
        "current_page_users": [user.to_admin_dict() for user in current_page_users]
    }
    return render_template("admin/user_list.html", data=data)


@admin_blu.route('/user_count')
def user_count():

    total_count = 0  # 总用户数
    try:
        total_count = User.query.filter(User.is_admin == False).count()
    except Exception as e:
        current_app.logger.error(e)

    t = time.localtime()  # 时间对象，内含t.tm_year=2019、t.tm_mon=9、t.tm_mday=25等信息
    month_count = 0  # 当月新增用户数
    month_begin_time = datetime.strptime(("%d-%02d-01" % (t.tm_year, t.tm_mon)), "%Y-%m-%d")  # 拼接成当月起点
    try:
        month_count = User.query.filter(User.is_admin == False, User.create_time > month_begin_time).count()
    except Exception as e:
        current_app.logger.error(e)

    day_count = 0  # 当日新增用户数。根据时间对象 t 中的年月日，拼接出当日起点
    day_begin_time = datetime.strptime(("%d-%02d-%02d" % (t.tm_year, t.tm_mon, t.tm_mday)), "%Y-%m-%d")
    try:
        day_count = User.query.filter(User.is_admin == False, User.create_time > day_begin_time).count()
    except Exception as e:
        current_app.logger.error(e)

    active_time = []  # 计算过去30天（算上今天共计 31 天），每天的活跃人数（0点～24点）
    active_count = []
    today_begin = datetime.strptime(("%d-%02d-%02d" % (t.tm_year, t.tm_mon, t.tm_mday)), "%Y-%m-%d")
    today_end = today_begin + timedelta(days=1)  # 取出今天的开始时刻和今天的结束时刻（即明天的开始时刻），区间前闭后开
    for i in range(31):  # i 是从today开始往前数的第几天
        current_begin = today_begin - timedelta(days=i)
        current_end = today_end - timedelta(days=i)
        current_count = 0
        try:
            current_count = User.query.filter(User.is_admin == False, User.last_login < current_end,
                                              User.last_login >= current_begin).count()
        except Exception as e:
            current_app.logger.error(e)
        active_time.append(current_begin.strftime("%Y-%m-%d"))  # append前，需转格式
        active_count.append(current_count)

    data = {
        "total_count": total_count,
        "month_count": month_count,
        "day_count": day_count,
        "active_time": active_time[::-1],
        "active_count": active_count[::-1]
    }
    return render_template("admin/user_count.html", data=data)


@admin_blu.route('/index')
@user_login_data
def index():  # 访问任一后台管理页面，均需查验is_admin。每个视图函数都查验，不如统一写进before_request钩子
    user = g.user
    return render_template("admin/index.html", user=user.to_dict())


@admin_blu.route('/login', methods=["GET", "POST"])
def login():
    if request.method=="GET":
        user_id = session.get("user_id", None)
        is_admin = session.get("is_admin", None)
        if user_id and is_admin:  # 如果已登录且是管理员，自动跳转到管理员首页
            return redirect("/admin/index")
        else:
            return render_template("admin/login.html", errmsg=None)
    else:
        username = request.form.get("username", None)
        password = request.form.get("password", None)
        if not all([username, password]):
            return render_template("admin/login.html", errmsg="参数不能为空")
        try:
            user = User.query.filter(User.mobile==username,
                                     User.is_admin==1).first()
        except Exception as e:
            current_app.logger.error(e)
            return render_template("admin/login.html", errmsg="数据库查询出错")
        if not user:
            return render_template("admin/login.html", errmsg="该管理员账户不存在")
        if not user.check_password(password):
            return render_template("admin/login.html", errmsg="用户名或密码错误")
        session["user_id"] = user.id   # 保存登录状态到session中
        session["mobile"] = user.mobile
        session["nick_name"] = user.nick_name
        session["is_admin"] = user.is_admin
        user.last_login = datetime.now()  # 更新用户最近一次登录时间
        return redirect("/admin/index")








