function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(function(){
    $(".news_review").submit(function (e) {
        e.preventDefault();  // 阻止默认提交行为后，进行新闻审核提交操作
        var params = {};
        $(this).serializeArray().map(function (x) {
            params[x.name] = x.value; // 获取到所有的参数
        });
        var action = params["action"];  // 取到参数以便判断
        var news_id = params["news_id"];
        var reason = params["reason"];
        if (action == "reject" && !reason) {
            alert('请输入拒绝原因');
            return;
        }
        params = {
            "action": action,  // 传给后端视图函数的params
            "news_id": news_id,
            "reason": reason
        };
        $.ajax({
            url: "/admin/news_review_action",
            type: "post",
            contentType: "application/json",
            data: JSON.stringify(params),
            headers: {
                "X-CSRFToken": getCookie("csrf_token")
            },
            success: function (resp) {
                if (resp.errno == "0") {
                    location.href = document.referrer; // 回上一页【哪来回哪去】
                }else {
                    alert(resp.errmsg);
                }
            }
        })
    })
});
function cancel() {  // 点击取消，返回上一页
    history.go(-1)
}

