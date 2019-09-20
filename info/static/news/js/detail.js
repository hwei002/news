function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}


$(function(){

    // 打开登录框
    $('.comment_form_logout').click(function () {
        $('.login_form_con').show();
    });

    // 收藏
    $(".collection").click(function () {
        var params = {
            "news_id": $(this).attr("data-newid"),  // 用属性获取id
            "action": "collect"
        };
        $.ajax({
            url: "/news/news_collect",
            type: "post",
            contentType: "application/json",
            data: JSON.stringify(params),
            headers: {
                "X-CSRFToken": getCookie("csrf_token")
            },
            success: function (resp) {  // ajax请求成功，则进行下述操作
                if (resp.errno == "0") { // 错误码为0，代表收藏成功
                    $(".collection").hide(); // 隐藏【收藏】按钮
                    $(".collected").show(); // 显示【取消收藏】按钮
                } else if (resp.errno == "4101") {  // 如果用户未登录
                    $('.login_form_con').show();  // 弹出登录框
                } else {
                    alert(resp.errmsg);
                }
            }
        })
    });

    // 取消收藏
    $(".collected").click(function () {
        var params = {
            "news_id": $(this).attr("data-newid"),  // 用属性获取id
            "action": "cancel_collect"
        };
        $.ajax({
            url: "/news/news_collect",
            type: "post",
            contentType: "application/json",
            data: JSON.stringify(params),
            headers: {
                "X-CSRFToken": getCookie("csrf_token")
            },
            success: function (resp) {
                if (resp.errno == "0") { // 错误码为0，代表取消收藏成功
                    $(".collection").show(); // 显示【收藏】按钮
                    $(".collected").hide(); // 隐藏【取消收藏】按钮
                } else {
                    alert(resp.errmsg);
                }
            }
        })
     
    });

    // 评论提交
    $(".comment_form").submit(function (e) {
        e.preventDefault();  // 使用ajax请求前，需先阻止 form 表单的传统提交
        var params = {  // 从 form 表单取出：需要传递给视图函数的参数。
            "news_id": $(this).attr('data-newsid'),  // 该新闻的id
            "comment": $(".comment_input").val()  // 用户刚刚输入的评论内容
        };
        $.ajax({
            url: "/news/news_comment",
            type: "post",
            contentType: "application/json",
            data: JSON.stringify(params),
            headers: {
                "X-CSRFToken": getCookie("csrf_token")
            },
            success: function (resp) {
                if (resp.errno == '0') {  // 如果ajax请求成功，则拼接字符串把评论显示出来
                    var comment = resp.comment;  // 从后端返回的response中取出comment对象
                    var comment_html = '';
                    comment_html += '<div class="comment_list">';
                    comment_html += '<div class="person_pic fl">';
                    if (comment.user.avatar_url){
                        comment_html += '<img src="' + comment.user.avatar_url + '" alt="用户图标">';
                    }else{
                        comment_html += '<img src="../../static/news/images/person01.png" alt="用户图标">';
                    }
                    comment_html += '</div>';
                    comment_html += '<div class="user_name fl">' + comment.user.nick_name + '</div>';
                    comment_html += '<div class="comment_text fl">';
                    comment_html += comment.content;
                    comment_html += '</div>';
                    comment_html += '<div class="comment_time fl">' + comment.create_time + '</div>';
                    comment_html += '<a href="javascript:;" class="comment_up fr" comment_id="'+comment.id+'" news_id="'+comment.news_id+'">赞</a>';
                    comment_html += '<a href="javascript:;" class="comment_reply fr">回复</a>';
                    comment_html += '<form class="reply_form fl" data-commendid="' + comment.id + '" data-newsid="' + comment.news_id + '">';
                    comment_html += '<textarea class="reply_input"></textarea>';
                    comment_html += '<input type="button" value="回复" class="reply_sub fr">';
                    comment_html += '<input type="reset" name="" value="取消" class="reply_cancel fr">';
                    comment_html += '</form>';
                    comment_html += '</div>';
                    $(".comment_list_con").prepend(comment_html);  // 把新评论加到评论列表的最前端
                    $('.comment_sub').blur();  // 让 comment 的 submit 按钮，失去焦点
                    $(".comment_input").val(""); // 清空输入框
                }else {
                    alert(resp.errmsg);
                }
            }
        })
    });

    $('.comment_list_con').delegate('a,input','click',function(){

        var sHandler = $(this).prop('class');

        if(sHandler.indexOf('comment_reply')>=0)
        {
            $(this).next().toggle();
        }

        if(sHandler.indexOf('reply_cancel')>=0)
        {
            $(this).parent().toggle();
        }

        if(sHandler.indexOf('comment_up')>=0)
        {
            var $this = $(this);
            if(sHandler.indexOf('has_comment_up')>=0)
            {
                // 如果当前该评论已经是点赞状态，再次点击会进行到此代码块内，代表要取消点赞
                $this.removeClass('has_comment_up')
            }else {
                $this.addClass('has_comment_up')
            }
        }

        if(sHandler.indexOf('reply_sub')>=0)
        {
            alert('回复评论')
        }
    })

        // 关注当前新闻作者
    $(".focus").click(function () {

    })

    // 取消关注当前新闻作者
    $(".focused").click(function () {

    })
})