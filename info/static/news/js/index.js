var currentCid = 1; // 当前分类 id
var cur_page = 1; // 当前页
var total_page = 1;  // 总页数
var data_querying = false;   // 是否正在向后台获取数据


$(function () {
    // 界面加载完成之后，去加载新闻数据
    updateNewsData();

    // 首页分类切换
    $('.menu li').click(function () {
        var clickCid = $(this).attr('data-cid');
        $('.menu li').each(function () {
            $(this).removeClass('active')
        });
        $(this).addClass('active');

        if (clickCid != currentCid) {
            // 记录当前分类id
            currentCid = clickCid;

            // 重置分页参数
            cur_page = 1;
            total_page = 1;
            updateNewsData()
        }
    });

    //页面滚动加载相关
    $(window).scroll(function () {

        // 浏览器窗口高度
        var showHeight = $(window).height();

        // 整个网页的高度
        var pageHeight = $(document).height();

        // 页面可以滚动的距离
        var canScrollHeight = pageHeight - showHeight;

        // 页面滚动了多少,这个是随着页面滚动实时变化的
        var nowScroll = $(document).scrollTop();

        if ((canScrollHeight - nowScroll) < 100) {
            // 判断页数，去更新新闻数据
            if (data_querying == false & cur_page < total_page) {  // 只有当眼下未做query且后面还有页数供query时，才update
                data_querying = true;
                cur_page += 1;
                updateNewsData();
            }
        }
    })
});

function updateNewsData() {
    // 更新新闻数据
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
