var currentCid = 1; // 当前分类 id
var cur_page = 1; // 当前页
var total_page = 1;  // 总页数
var data_querying = false;   // 是否正在向后台获取数据

$(function () {
    updateNewsData();  // 首页index界面加载完成后，第一次加载新闻列表

    // 首页新闻分类之间的切换功能
    $('.menu li').click(function () {
        var clickCid = $(this).attr('data-cid');
        $('.menu li').each(function () {
            $(this).removeClass('active')
        });
        $(this).addClass('active');
        if (clickCid != currentCid) {  // 仅当【被点击分类，不是当前active分类】时，才去加载被点击分类
            currentCid = clickCid;  // 记录当前分类id
            cur_page = 1; // 重置分页参数
            total_page = 1;
            updateNewsData();
        }
    });

    //页面滚动触发自动加载的功能
    $(window).scroll(function () {
        var showHeight = $(window).height(); // 浏览器窗口高度
        var pageHeight = $(document).height(); // 整个网页的高度
        var canScrollHeight = pageHeight - showHeight;  // 页面可以滚动的距离
        var nowScroll = $(document).scrollTop();  // 页面已经滚动了多少（该数值是随页面滚动实时变化的）
        if ((canScrollHeight - nowScroll) < 100) {  // 滚动触发自动加载的条件
            if (data_querying == false & cur_page < total_page) {  // 只有【眼下无未完成query & 后面还有页数供query】时，才继续
                data_querying = true;
                cur_page += 1;
                updateNewsData();
            }
        }
    })
});

function updateNewsData() {  // 更新新闻数据
    var params = {  // 需要通过url传递给route视图函数的参数
        "cid": currentCid,
        "page": cur_page
    };
    $.get("/news_list", params, function(resp){  // resp 就是【'/news_list'】对应的视图函数返回的json文件
        if (resp.errno=="0"){ // 代表请求成功
            data_querying = false;  // 请求成功后，将正在query的 flag 改回 false
            total_page = resp.data.total_page;  // 请求成功后，更新total_page（默认为1，首次query后更新total_page为正确的值）
            if (cur_page == 1) {
                $(".list_con").html(""); // 仅当载入第一页操作前，才需清除旧数据（滚动载入非第一页的请求，无需清除旧数据！！）
            }
            for (var i=0; i<resp.data.current_page_news.length; i++) {  // 用拼接字符串的方式，添加请求返回的新数据
                var news = resp.data.current_page_news[i];
                var content = '<li>';
                content += '<a href="#" class="news_pic fl"><img src="' + news.index_image_url + '?imageView2/1/w/170/h/170"></a>';
                content += '<a href="#" class="news_title fl">' + news.title + '</a>';
                content += '<a href="#" class="news_detail fl">' + news.digest + '</a>';
                content += '<div class="author_info fl">';
                content += '<div class="source fl">来源：' + news.source + '</div>';
                content += '<div class="time fl">' + news.create_time + '</div>';
                content += '</div>';
                content += '</li>';
                $(".list_con").append(content)
            }
        }else{
            alert(resp.errmsg); // 代表请求失败
        }
    })
}
