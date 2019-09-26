function decodeQuery(){  // 解析url中的查询字符串
    var search = decodeURI(document.location.search);
    return search.replace(/(^\?)/, '').split('&').reduce(function(result, item){
        values = item.split('=');
        result[values[0]] = values[1];
        return result;
    }, {});
}

$(function(){
    getNewsList(1);  // 页面加载完毕后，默认显示发布的所有新闻的第1页，故首次调用新闻页加载函数

    $(".focus").click(function () { // 关注当前作者
        var user_id = $(this).attr('data-userid');
        var params = {
            "action": "follow",
            "user_id": user_id
        };
        $.ajax({
            url: "/news/followed_user",
            type: "post",
            contentType: "application/json",
            data: JSON.stringify(params),
            headers: {
                "X-CSRFToken": getCookie("csrf_token")
            },
            success: function (resp) {
                if (resp.errno == "0") {  // 关注成功
                    var count = parseInt($(".follows b").html());
                    count++;
                    $(".follows b").html(count + "");
                    $(".focus").hide();
                    $(".focused").show()
                }else if (resp.errno == "4101"){
                    $('.login_form_con').show(); // 未登录，弹登录框
                }else {
                    alert(resp.errmsg); // 关注失败，弹错误信息
                }
            }
        })
    });

    $(".focused").click(function () {  // 取消关注当前作者
        var user_id = $(this).attr('data-userid');
        var params = {
            "action": "unfollow",
            "user_id": user_id
        };
        $.ajax({
            url: "/news/followed_user",
            type: "post",
            contentType: "application/json",
            data: JSON.stringify(params),
            headers: {
                "X-CSRFToken": getCookie("csrf_token")
            },
            success: function (resp) {
                if (resp.errno == "0") {  // 取消关注成功
                    var count = parseInt($(".follows b").html());
                    count--;
                    $(".follows b").html(count + "");
                    $(".focus").show();
                    $(".focused").hide()
                }else if (resp.errno == "4101"){
                    $('.login_form_con').show(); // 未登录，弹登录框
                }else {
                    alert(resp.errmsg); // 取消关注失败
                }
            }
        })
    })
});

function getNewsList(page) {  // 获取指定页码中的新闻列表【刚打开页面时进行首次调用，后续点击第x页也会调用此函数】
    var query = decodeQuery();  // 调用解码函数，解析出url传入的若干参数键值对
    var params = {
        "page": page,
        "other_id": query["other_id"]
    };
    $.get("/user/other_news_list", params, function (resp) {
        if (resp.errno == "0") {
            $(".article_list").html("");  // 先清空原有的数据
            for (var i = 0; i < resp.data.news_list.length; i++) {  // 拼接每条新闻数据对应的<li></li>
                var news = resp.data.news_list[i];
                var html = '<li><a href="/news/' + news.id +'" target="_blank">'
                                                 + news.title + '</a><span>'
                                                 + news.create_time + '</span></li>';
                $(".article_list").append(html);  // 添加数据
            }  // 下一行，设置当前页数和总页数
            $("#pagination").pagination("setPage", resp.data.current_page, resp.data.total_page);
        }else {
            alert(resp.errmsg)
        }
    })
}

