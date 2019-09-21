function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}


$(function () {
    $(".pass_info").submit(function (e) {
        e.preventDefault();
        var params = {};  // 用x遍历所有input元素，生成params
        // 比如首个x = {"name": "old_password", "value": "12345678"}
        $(this).serializeArray().map(function (x) {
            params[x.name] = x.value;
        });
        var new_password = params["new_password"];
        var new_password2 = params["new_password2"];
        if (new_password != new_password2) {  // 判断两次新密码是否相同
            alert('两次新密码输入不一致');
            return
        }
        $.ajax({
            url: "/user/pass_info",
            type: "post",
            contentType: "application/json",
            data: JSON.stringify(params),
            headers: {
                "X-CSRFToken": getCookie("csrf_token")
            },
            success: function (resp) {
                if (resp.errno == "0") {
                    alert("修改成功");
                    window.location.reload()  // 刷新页面
                }else {
                    alert(resp.errmsg)
                }
            }
        })
    })
});

