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

    // 对新闻进行评论
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
                    if (comment.user.avatar_url) {
                        comment_html += '<img src="' + comment.user.avatar_url + '" alt="用户图标">'
                    }else {
                        comment_html += '<img src="../../static/news/images/person01.png" alt="用户图标">'
                    }
                    comment_html += '</div>';
                    comment_html += '<div class="user_name fl">' + comment.user.nick_name + '</div>';
                    comment_html += '<div class="comment_text fl">';
                    comment_html += comment.content;
                    comment_html += '</div>';
                    comment_html += '<div class="comment_time fl">' + comment.create_time + '</div>';
                    comment_html += '<a href="javascript:;" class="comment_up fr" data-commentid="' + comment.id + '" data-newsid="' + comment.news_id + '">赞</a>';
                    comment_html += '<a href="javascript:;" class="comment_reply fr">回复</a>';
                    comment_html += '<form class="reply_form fl" data-commentid="' + comment.id + '" data-newsid="' + params["news_id"] + '">';
                    comment_html += '<textarea class="reply_input"></textarea>';
                    comment_html += '<input type="button" value="回复" class="reply_sub fr">';
                    comment_html += '<input type="reset" name="" value="取消" class="reply_cancel fr">';
                    comment_html += '</form>';
                    comment_html += '</div>';
                    $(".comment_list_con").prepend(comment_html);  // 把新评论加到评论列表的最前端
                    $('.comment_sub').blur();  // 让 comment 的 submit 按钮，失去焦点
                    $(".comment_input").val(""); // 清空输入框
                    updateCommentCount();  // 更新该新闻的总评论数
                }else {
                    alert(resp.errmsg)
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

        // 点赞与取消点赞的切换
        if(sHandler.indexOf('comment_up') >= 0)
        {
            var $this = $(this);
            var action = "add";  // 默认处于【未被赞】状态，故点击的默认触发是【未被赞-->被赞】
            if(sHandler.indexOf('has_comment_up') >= 0)  // 表示【已经有赞】
            {
                action = "remove";  // 如果当前已是被赞状态，点击应触发【被赞-->未被赞】，即取消点赞
            }
            var params = {
                "comment_id": $this.attr("data-commentid"),
                "action": action
            };
            $.ajax({
                url: "/news/like_comment",
                type: "post",
                contentType: "application/json",
                data: JSON.stringify(params),
                headers: {
                    "X-CSRFToken": getCookie("csrf_token")
                },
                success: function (resp) {
                    if (resp.errno == "0") {  // 更新点赞按钮图标
                        if (action == "add") {  // 点赞操作，让其新增【已经有赞】类标签
                            $this.addClass('has_comment_up');
                        }else {  // 取消点赞操作，让其失去【已经有赞】类标签
                            $this.removeClass('has_comment_up')
                        }
                    }else if (resp.errno == "4101"){
                        $('.login_form_con').show();  // 如果用户未登录，则弹出登录框
                    }else {
                        alert(resp.errmsg)
                    }
                }
            })
        }
        // 对父评论进行子评论
        if(sHandler.indexOf('reply_sub') >= 0)
        {
            var $this = $(this);  // 本段代码结尾处需清空$(this)中内容，但结尾处$(this)所指对象并非起始处$(this)所指对象！！故必须定义一个首尾指代一致的var！！
            var params = {
                "news_id": $this.parent().attr('data-newsid'),
                "comment": $this.prev().val(),
                "parent_id": $this.parent().attr('data-commentid')
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
                    if (resp.errno == "0") {  // 如果ajax请求成功，则拼接字符串把评论显示出来
                        var comment = resp.comment;  // 从后端返回的response中取出comment对象
                        var comment_html = "";  // 开始拼接字符串
                        comment_html += '<div class="comment_list">';
                        comment_html += '<div class="person_pic fl">';
                        if (comment.user.avatar_url) {
                            comment_html += '<img src="' + comment.user.avatar_url + '" alt="用户图标">'
                        }else {
                            comment_html += '<img src="../../static/news/images/person01.png" alt="用户图标">'
                        }
                        comment_html += '</div>';
                        comment_html += '<div class="user_name fl">' + comment.user.nick_name + '</div>';
                        comment_html += '<div class="comment_text fl">';
                        comment_html += comment.content;
                        comment_html += '</div>';
                        comment_html += '<div class="reply_text_con fl">';
                        comment_html += '<div class="user_name2">' + comment.parent.user.nick_name + '</div>';
                        comment_html += '<div class="reply_text">';
                        comment_html += comment.parent.content;
                        comment_html += '</div>';
                        comment_html += '</div>';
                        comment_html += '<div class="comment_time fl">' + comment.create_time + '</div>';
                        comment_html += '<a href="javascript:;" class="comment_up fr" data-commentid="' + comment.id + '" data-newsid="' + comment.news_id + '">赞</a>';
                        comment_html += '<a href="javascript:;" class="comment_reply fr">回复</a>';
                        comment_html += '<form class="reply_form fl" data-commentid="' + comment.id + '" data-newsid="' + params["news_id"] + '">';
                        comment_html += '<textarea class="reply_input"></textarea>';
                        comment_html += '<input type="button" value="回复" class="reply_sub fr">';
                        comment_html += '<input type="reset" name="" value="取消" class="reply_cancel fr">';
                        comment_html += '</form>';
                        comment_html += '</div>';
                        $(".comment_list_con").prepend(comment_html);
                        $this.prev().val("");  // 清空输入框
                        $this.parent().hide();  // 隐藏【点击“回复”按钮所弹出的输入子评论】模块
                        updateCommentCount();  // 更新该新闻的总评论数
                    }else {
                        alert(resp.errmsg);
                    }
                }
            })
        }
    });

        // 关注当前新闻作者
    $(".focus").click(function () {

    });

    // 取消关注当前新闻作者
    $(".focused").click(function () {

    })
});


function updateCommentCount(){  // for循环中每条评论class=“comment_list”，用$取出的是评论元素的列表
    var count = $(".comment_list").length;
    $(".comment_count").html(count+"条评论");
}
