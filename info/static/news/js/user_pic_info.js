function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}


$(function () {
    $(".pic_info").submit(function (e) {
        e.preventDefault();  // 阻止表单传统提交，并开始【上传头像】操作
        $(this).ajaxSubmit({  // ajaxSubmit是用ajax的方式模拟传统form表单的提交：
            url: "/user/pic_info",  // 无需定义params，而是带上所有具有name属性的元素的（name，value）键值对
            type: "POST",
            headers: {
                "X-CSRFToken": getCookie('csrf_token')
            },
            success: function (resp) {
                if (resp.errno == "0") {  // 更新“上传头像”页面共计三处头像！！
                    $(".now_user_pic").attr("src", resp.data.avatar_url);
                    $(".user_center_pic>img", parent.document).attr("src", resp.data.avatar_url);
                    $(".user_login>img", parent.document).attr("src", resp.data.avatar_url)
                }else {
                    alert(resp.errmsg)
                }
            }
        })
    })
});

