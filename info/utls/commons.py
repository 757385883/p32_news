# 自定义装饰器，检查用户登录状态
# 定义装饰器，方便每个页面显示登录状态，不用重复写代码
import functools

from flask import session, current_app, g

from info.models import User

""" functools重要作用：
    装饰器会改变被装饰函数的名称，修改为装饰器的内函数重名
    易导致在路由映射中，视图函数的重名，从而发生根据路由找到多个相同的视图函数
    所以使用functools.wraps(f),这样就不会修改是视图函数的名称了
    """



def login_required(f):

    @functools.wraps(f)

    def wrappr(*args,**kwargs):
        user_id = session.get('user_id')
        # 用户也可以是空值，因为详情页面即使不登录也可以访问
        # 一般收藏，关注，这些必须登录，所以user可以是空值
        user= None

        # 判断id是否存在，存在则查询数据库
        if user_id:
            try:
                user = User.query.filter(id = user_id).first()
            except Exception as e:
                current_app.logger.error(e)
        # 使用g对象存储user信息，临时
        g.user = user
        return f(*args,**kwargs)
    return wrappr