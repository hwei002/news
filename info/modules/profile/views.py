from flask import abort
from flask import current_app, g, redirect, render_template, request, jsonify
from info import constants, db
from info.models import Category, News, User
from info.modules.profile import profile_blu
from info.utils.common import user_login_data
from info.utils.image_storage import storage
from info.utils.response_code import RET


@profile_blu.route('/other_news_list')
@user_login_data
def other_news_list():
    other_id = request.args.get("other_id", None)
    page = request.args.get("page", 1)
    if not other_id:
        return jsonify(errno=RET.PARAMERR, errmsg="other_id不能为空")
    try:
        other_id = int(other_id)
        page = int(page)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="参数必须为整数")
    try:
        other = User.query.get(other_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库查询失败")
    if not other:
        return jsonify(errno=RET.NODATA, errmsg="指定id对应的新闻不存在")
    try:
        paginate = other.news_list.paginate(page, constants.USER_COLLECTION_MAX_NEWS, False)
        current_page = paginate.page
        total_page = paginate.pages
        news_list = paginate.items
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据查询错误")  # user.news_list是dynamic=lazy
    data = {
        "current_page": current_page,
        "total_page": total_page,
        "news_list": [news.to_basic_dict() for news in news_list]
    }
    return jsonify(errno=RET.OK, errmsg="OK", data=data)


@profile_blu.route("/other_info")
@user_login_data
def other_info():
    other_id = request.args.get("other_id", None)
    if not other_id:
        abort(404)
    try:
        other_id = int(other_id)
    except Exception as e:
        current_app.logger.error(e)
        abort(404)

    other = None
    try:
        other = User.query.get(other_id)
    except Exception as e:
        current_app.logger.error(e)
        abort(404)
    if not other:
        abort(404)

    user = g.user
    is_followed = False
    if user in other.followers:
        is_followed = True  # 当前登录user（如果存在），在other粉丝列表中，则【已关注】
    data = {
        "user": user.to_dict() if user else None,
        "other": other.to_dict(),
        "is_followed": is_followed
    }
    return render_template("news/other.html", data=data)


@profile_blu.route("/user_follow")
@user_login_data
def user_follow():
    page = request.args.get("page", 1)
    try:
        page = int(page)
    except Exception as e:
        current_app.logger.error(e)
        page = 1
    try:
        paginate = g.user.followed.paginate(page, constants.USER_FOLLOWED_MAX_COUNT, False)
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
        "current_page_users": [user.to_dict() for user in current_page_users]
    }
    return render_template("news/user_follow.html", data=data)


@profile_blu.route('/news_list')
@user_login_data
def news_list():
    page = request.args.get("p", "1")  # 获取url中传入的“?p=xxx”页码参数
    try:
        page = int(page)
    except Exception as e:
        page = 1  # 如果page取整失败，则默认显示第 1 页
        current_app.logger.error(e)
    try:
        page_obj = News.query.filter(News.user_id == g.user.id).order_by(News.create_time.desc())\
                       .paginate(page, constants.USER_COLLECTION_MAX_NEWS, False)
        current_page = page_obj.page
        total_page = page_obj.pages
        current_page_news = page_obj.items
        current_page_news = [news.to_review_dict() for news in current_page_news]
    except Exception as e:
        current_page = 1
        total_page = 1
        current_page_news = []  # 查询出错，则默认显示 1/1 页，且当页为空数据
        current_app.logger.error(e)
    data = {
        "current_page_news": current_page_news,
        "total_page": total_page,
        "current_page": current_page
    }
    return render_template("news/user_news_list.html", data=data)  # GET/POST 返 render_template/jsonify


@profile_blu.route('/news_release', methods=["GET", "POST"])
@user_login_data
def news_release():
    if request.method == "GET":
        categories = []  # 在渲染时，需把【所有新闻分类】传回前端，供用户发布新闻时选择相应分类
        try:
            categories = Category.query.all()
        except Exception as e:
            current_app.logger.error(e)
        categories = [category.to_dict() for index, category in enumerate(categories) if index > 0]
        data = {
            "categories": categories  # 传回前端时，去掉分类“最新”（index=0）
        }
        return render_template("news/user_news_release.html", data=data)
    else:
        title = request.form.get("title", None)
        category_id = request.form.get("category_id", None)
        digest = request.form.get("digest", None)
        index_image = request.files.get("index_image", None)
        content = request.form.get("content", None)  # 课堂所用tinymce的html编辑器，content永远是默认值，不知为啥
        source = "个人发布"
        if not all([title, category_id, digest, index_image, content, source]):
            return jsonify(errno=RET.PARAMERR, errmsg="参数错误")
        try:
            category_id = int(category_id)
            index_image = index_image.read()  # 尝试读取图片
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.PARAMERR, errmsg="参数错误")
        try:
            image_key = storage(index_image)
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.THIRDERR, errmsg="图片上传七牛云失败")
        news = News()
        news.title = title
        news.category_id = category_id
        news.digest = digest
        news.index_image_url = constants.QINIU_DOMIN_PREFIX + image_key
        news.content = content
        news.source = source
        news.user_id = g.user.id
        news.status = 1  # 当前新闻状态：0审核通过，1审核中，-1审核不通过
        try:
            db.session.add(news)
            db.session.commit()
        except Exception as e:
            current_app.logger.error(e)
            db.session.rollback()
            return jsonify(errno=RET.DBERR, errmsg="新闻保存数据库失败")
        return jsonify(errno=RET.OK, errmsg="新闻发布成功，等待审核")


@profile_blu.route('/collection')
@user_login_data
def user_collection():
    page = request.args.get("p", 1)
    try:
        page = int(page)
    except Exception as e:
        current_app.logger.error(e)
        page = 1  # 如果浏览器传入的page不能转为int型，则默认显示第 1 页
    try:  # paginate方法需传入三个参数：请求页码、每页允许的条数、是否报错
        page_obj = g.user.collection_news.paginate(page, constants.USER_COLLECTION_MAX_NEWS, False)
        current_page = page_obj.page  # 当前页码
        total_page = page_obj.pages  # 总页数
        current_page_news = page_obj.items  # 当前页的所有条目对象
        current_page_news = [news.to_basic_dict() for news in current_page_news]  # 对象转为字典再返回
    except Exception as e:
        current_app.logger.error(e)
        current_page = 1  # 出错时，为三个变量设定默认值
        total_page = 1
        current_page_news = []
    data = {
        "current_page": current_page,
        "total_page": total_page,
        "collection": current_page_news
    }
    return render_template("news/user_collection.html", data=data)


@profile_blu.route('/pass_info', methods=["GET", "POST"])
@user_login_data
def pass_info():
    if request.method == "GET":
        return render_template("news/user_pass_info.html")
    elif request.method == "POST":
        old_password = request.json.get("old_password", None)
        new_password = request.json.get("new_password", None)
        if not all([old_password, new_password]):
            return jsonify(errno=RET.PARAMERR, errmsg="参数错误")
        if old_password == new_password:
            return jsonify(errno=RET.PARAMERR, errmsg="新旧密码相同")
        user = g.user
        if not user.check_password(old_password):
            return jsonify(errno=RET.PWDERR, errmsg="原密码校验失败")
        user.password = new_password
        return jsonify(errno=RET.OK, errmsg="密码修改成功")


@profile_blu.route('/pic_info', methods=["GET", "POST"])
@user_login_data
def pic_info():
    user = g.user
    if request.method == "GET":
        return render_template("news/user_pic_info.html", data={"user":user.to_dict()})
    elif request.method == "POST":
        # 1. 获取图片
        try:
            avatar = request.files.get("avatar").read()  # 修改头像页面，点击保存按钮触发post请求，通过request获得用户上传的图片
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.PARAMERR, errmsg="参数错误")
        # 2. 上传图片
        try:
            key = storage(avatar)
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.THIRDERR, errmsg="文件上传七牛云失败")
        # 3. 更新当前用户avatar_url字段为相对路径，返回绝对路径供前端使用（更新多处头像）
        user.avatar_url = key
        data = {
            "avatar_url": constants.QINIU_DOMIN_PREFIX + key
        }
        return jsonify(errno=RET.OK, errmsg="文件上传成功", data=data)


@profile_blu.route('/base_info', methods=["GET", "POST"])
@user_login_data
def base_info():
    user = g.user
    if request.method == "GET":
        return render_template("news/user_base_info.html", data={"user": user.to_dict()})
    elif request.method == "POST":
        nick_name = request.json.get("nick_name", None)
        signature = request.json.get("signature", None)
        gender = request.json.get("gender", None)
        if not all([nick_name, signature]) or gender not in ["MAN", "WOMAN"]:
            return jsonify(errno=RET.PARAMERR, errmsg="参数错误")
        user.nick_name = nick_name
        user.signature = signature
        user.gender = gender
        return jsonify(errno=RET.OK, errmsg="个人基本信息修改成功")


@profile_blu.route('/info')
@user_login_data
def user_info():
    user = g.user
    if not user:
        return redirect("/")  # 用户未登录，重定向到主页
    data = {
        "user": user.to_dict()
    }
    return render_template("news/user.html", data=data)

