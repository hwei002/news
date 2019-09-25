function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}
$(function () {
    $(".release_form").submit(function (e) {
        e.preventDefault();  // 发布新闻
        $(this).ajaxSubmit({  // ajaxSubmit自动带上含有name属性的元素当params
            beforeSubmit: function (request) { // 在提交之前，对参数进行处理
                for(var i=0; i<request.length; i++) {
                    var item = request[i];
                    if (item["name"] == "content") {  // tinymce中的输入内容，需用特殊方法提取！！
                        item["value"] = tinyMCE.activeEditor.getContent()
                    }
                }
            },
            url: "/user/news_release",
            type: "POST",
            headers: {
                "X-CSRFToken": getCookie('csrf_token')
            },
            success: function (resp) {
                if (resp.errno == "0") {  // 发布完毕后，自动跳转到该用户所发新闻列表
                    window.parent.fnChangeMenu(6); // 选中索引为6的左边单菜单
                    window.parent.scrollTo(0, 0);  // 滚动到顶部
                }else {
                    alert(resp.errmsg)
                }
            }
        });
    })
});

