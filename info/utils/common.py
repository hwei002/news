# 公用的自定义工具类


def do_index_class(index):
    """为点击排行class自定义过滤器"""
    if index == 1:
        return "first"
    elif index == 2:
        return "second"
    elif index == 3:
        return "third"
    else:
        return ""
