function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}
$(function () {
    $(".focused").click(function () {  // 取消关注
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
                if (resp.errno == "0") {  // 取消关注成功刷新当前界面
                    window.location.reload()
                }else if (resp.errno == "4101"){
                    $('.login_form_con').show(); // 未登录，弹登录框
                }else {
                    alert(resp.errmsg);  // 取消关注失败
                }
            }
        })
    })
});

