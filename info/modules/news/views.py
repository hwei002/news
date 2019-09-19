from flask import render_template
from info.modules.news import news_blu


@news_blu.route('/<int:news_id>')  # int冒号后不能加空格。。。
def news_detail(news_id):
    data = {}
    return render_template('news/detail.html', data=data)

