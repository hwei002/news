function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}
$(function(){
    $(".news_edit").submit(function (e) {
        e.preventDefault();  // 阻止默认提交行为，以下进行新闻版式的编辑提交操作
        $(this).ajaxSubmit({
            beforeSubmit: function (request) { // 在提交之前，对参数进行处理
                for(var i=0; i<request.length; i++) {
                    var item = request[i];
                    if (item["name"] == "content") {  // tinymce中的输入内容，需用特殊方法提取！！
                        item["value"] = tinyMCE.activeEditor.getContent()
                    }
                }
            },
            url: "/admin/news_edit_detail",
            type: "POST",
            headers: {
                "X-CSRFToken": getCookie('csrf_token')
            },
            success: function (resp) {
                if (resp.errno == "0") {
                    location.href = document.referrer;  // 返回上一页，哪来回哪去
                } else {
                    alert(resp.errmsg);
                }
            }
        })
    })
});
function cancel() {
    history.go(-1);  // 点击取消，返回上一页
}

