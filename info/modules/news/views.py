from flask import current_app, render_template, g, abort, jsonify, request
from info import constants, db
from info.models import News, Comment, CommentLike
from info.modules.news import news_blu
from info.utils.common import user_login_data
from info.utils.response_code import RET


@news_blu.route('/like_comment', methods=["POST"])
@user_login_data
def like_comment():

    # 1. 判断用户是否登录
    user = g.user
    if not user:
        return jsonify(errno=RET.SESSIONERR, errmsg="用户未登录")

    # 2. 获取参数
    comment_id = request.json.get("comment_id", None)
    action = request.json.get("action", None)

    # 3. 校验参数
    if not comment_id or action not in ["add", "remove"]:  # 参数非空且action二选一
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")
    try:
        comment_id = int(comment_id)  # comment_id 必须为整数
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")
    try:
        comment = Comment.query.get(comment_id)  # 查询comment_id对应的评论
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库查询失败")
    if not comment:  # 指定评论必须存在
        return jsonify(errno=RET.NODATA, errmsg="评论不存在")

    # 4. 完成点赞/取消点赞操作
    try:
        like_obj = CommentLike.query.filter(CommentLike.user_id==user.id, CommentLike.comment_id==comment_id).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库查询失败")
    if action == "add":
        if like_obj is None:  # 增加点赞
            like_obj = CommentLike()
            like_obj.user_id = user.id
            like_obj.comment_id = comment_id
            db.session.add(like_obj)
            comment.like_count += 1  # 更新该评论的点赞数
    else:
        if like_obj is not None:  # 取消点赞
            db.session.delete(like_obj)
            comment.like_count -= 1  # 更新该评论的点赞数
    return jsonify(errno=RET.OK, errmsg="操作成功")


@news_blu.route('/news_comment', methods=["POST"])
@user_login_data
def news_comment():

    # 1. 判断用户是否登录
    user = g.user
    if not user:
        return jsonify(errno=RET.SESSIONERR, errmsg="用户未登录")

    # 2. 获取参数
    news_id = request.json.get("news_id", None)
    comment = request.json.get("comment", None)
    parent_id = request.json.get("parent_id", None)

    # 3. 校验参数
    if not all([news_id, comment]):  # news_id 和 comment 不能为空
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")
    try:
        news_id = int(news_id)  # news_id 和 parent_id（如果存在） 必须整数
        if parent_id:
            parent_id = int(parent_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")
    try:
        news = News.query.get(news_id)  # news_id 对应的新闻必须存在
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库查询操作失败")
    if not news:
        return jsonify(errno=RET.NODATA, errmsg="新闻数据不存在")

    # 4. 创建一个comment对象
    comment_obj = Comment()
    comment_obj.user_id = user.id
    comment_obj.news_id = news_id
    comment_obj.content = comment
    if parent_id:
        comment_obj.parent_id = parent_id

    # 5. 添加comment对象进数据库：必须手动而非依赖commit_on_teardown，因视图函数需返回comment_id
    try:
        db.session.add(comment_obj)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="数据库添加失败")

    return jsonify(errno=RET.OK, errmsg="评论添加成功", comment=comment_obj.to_dict())


@news_blu.route('/news_collect', methods=["POST"])
@user_login_data
def news_collect():

    # 1. 判断用户是否登录
    user = g.user
    if not user:
        return jsonify(errno=RET.SESSIONERR, errmsg="用户不存在")

    # 2. 获取参数
    news_id = request.json.get("news_id", None)
    action = request.json.get("action", None)

    # 3. 校验参数
    if not news_id or action not in ["collect", "cancel_collect"]:
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")
    try:
        news_id = int(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    # 4. 查询新闻对象
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.NODATA, errmsg="新闻数据不存在")

    # 5. 完成收藏/取消收藏操作
    if action == "collect" and news not in user.collection_news:
        user.collection_news.append(news)
    if action == "cancel_collect" and news in user.collection_news:
        user.collection_news.remove(news)
    return jsonify(errno=RET.OK, errmsg="操作成功")


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

    # 判断用户是否收藏本条新闻
    is_collected = False
    if user and news in user.collection_news:  # User和News是多对多关系，此处collection_news在Model已定义好
        is_collected = True  # 上一行最后不用.all()表lazy模式【用的时候再去查询】，用了.all()则会立即查询，影响性能

    # 从数据库中，查询出该条新闻所有评论，返回给前端，供渲染显示
    comments_obj = []
    try:
        comments_obj = Comment.query.filter(Comment.news_id==news_id).order_by(Comment.create_time.desc()).all()
    except Exception as e:
        current_app.logger.error(e)

    # 每条评论的点赞显示（登录情况下，本用户点过赞则拇指高亮，未点过赞则拇指灰暗）
    comment_like_ids = []  # 本新闻的评论中，该用户点过赞的所有评论的id列表
    if user:
        try:
            # 获取本新闻所有评论的id
            comment_ids = [comment_obj.id for comment_obj in comments_obj]
            # 查询出本新闻的评论中，该用户点过赞的所有评论（返回的是一个CommentLike对象列表）
            comment_likes = CommentLike.query.filter(CommentLike.user_id==user.id, CommentLike.comment_id.in_(comment_ids)).all()
            # 获取该用户点过赞的所有评论的id
            comment_like_ids = [comment_like.comment_id for comment_like in comment_likes]
        except Exception as e:
            current_app.logger.error(e)

    comments_dic = []
    for comment_obj in comments_obj:
        comment_dic = comment_obj.to_dict()
        comment_dic["is_like"] = False  # 添加键值对表示是否点过赞，默认False
        if comment_obj.id in comment_like_ids:
            comment_dic["is_like"] = True  # 如果该评论的id，出现在【该用户点过赞的所有评论的id列表】中，则改为True
        comments_dic.append(comment_dic)

    # 把数据进行汇总，当参数传给模板，供渲染时使用
    data = {
        "user": user.to_dict() if user else None,  # 将user转为字典形式传给前端html模板，供 js 分支判断使用
        "top_click_news": top_click_news,
        "news": news.to_dict(),
        "is_collected": is_collected,
        "comments": comments_dic,
    }
    return render_template('news/detail.html', data=data)

