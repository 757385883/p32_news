# 8.2从同一个目录导入蓝图对象
from info import db
from . import api
from flask import session, render_template, current_app, jsonify, request, g
from info.models import User, News, Category
from info.utls.response_code import RET
from info.utls.commons import login_required
# 8.3使用蓝图对象，项目首页展示
@api.route('/')
@login_required
def index():
    """首页用户信息的展示
    1.尝试从redis中获取用户id
    2.如果user_id存在，查询mysql，把用户信息传给模板
    """
    # 因为user的用户信息已经存储在g对象中，想要拿到usr信息，
    # 所以在把g.user赋值给user
    user = g.user
    # user_id = session.get('user_id')
    # # 如果数据查询失败，返回None，避免date没有被定义
    # date= None # 如果数据查询失败，返回None，避免date没有被定义
    # user = None
    #
    #
    #
    # if user_id:
    #     try:
    #         # 通过id查用户信息
    #         user = User.query.get('user_id')
    #     except Exception as  e:
    #         current_app.logger.error(e)
    #         return jsonify(error=RET.DBERR,errmsg='查询数据失败')
    # 17.新闻点击排行，默认按照新闻的点击次数倒叙排序
    try:
        news_list =News.query.filter().order_by(News.clicks.desc()).limit(6)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg='查询数据异常')
    # 判断查询结果是否存在
    if not news_list:
        return jsonify(errno= RET.NODATA,errmsg='无新闻数据')


    # 定义容器列表用来存储遍历后的数据
    news_dict_list = []
    # 遍历查询结果，把查询到的对象转成可读字符串
    for news in news_list:
        news_dict_list.append(news.to_dict())
    # 返回数据
    # 首页显示分类信息,查询数据使用try，然后返回查询一次数据，
    # 然后一定要判段查询结果，数据不存在，返回错误信息
    try:
        categories= Category.query,all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBEER,errmsg='查询分类异常')
    # 判断查询结果
    if not categories:
        return jsonify(errno= RET.NODATA,errmsg='无分类数据')
# 定义容器存储查询结果
    category_list = []
    # 遍历查询结果
    for category in categories:
        category_list.append(category.to_dict())


    # data作为一个字典传参，冒号左边类似三元式
    data={
        #设置用户信息的键  user的方法：是拿到user所有的键值对
        'user_Info':user.to_dict()if user else None,
        'news_dict_list':news_dict_list,
        'category_list':category_list
    }
    # 返回渲染数据,将template改为模板格式
    return render_template('news/index.html',data= data)

# 项目 logo图标展示
@api.route('/favicon.ico')
def favicon():
    # 使用current_app调用发送静态文件的方法，把项目logo文件发给浏览器
    return current_app.send_static_file('news/favicon.ico')


# 首页新闻列表，这部分为局部刷新，所以通过ajax局部请求，所以定义相应的接口
@api.route('/news_list')
def get_news_list():
    """
    首页新闻列表数据展示
    1.获取参数，cid新闻分类id、page总页数、per_page每页的条目数
    2.检查参数，把参数转成int类型
    3、判断分类id 是否大于1
    4.根据新闻分类id查询数据库，按照新闻的发布时间排序，对排序结果进行分页
    5.获取分页后，的新闻数据：总页数，当前页数，数据
    6.返回结果

    重要提示：新闻列表的展示，可能会有参数传入，也可能没有，所以需要有默认值，而且请求方式
    是get，
    :return:
    """
    # 获取参数，请求方式是get，使用查询字符串获取参数，参数可有可无，s
    # 所以1、1、10是默认数据，不传参数默认就是1、1、10
    cid = request.args.get('cid','1')
    page = request.args.get('page','1')
    per_page = request.args.get('per_page','10')
    # 检查参数，需要不参数转成int，转变数据类型，也要使用try
    try:
        cid,page,per_page = int(cid),int(page),int(per_page)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR,errmsg='参数格式错误')
    # 定义过滤条件
    filters = []
    # 判断分类id是否是最新，就是是否大于1
    if cid > 1:
        filters.append(News.category_id == cid)
    # =根据分类查询数据库
    try:
        #对过滤查询执行排序，堆排序结果进行分页
        # *filters的作用就是传参，如果cid大于1，里面添加的就是具体参数
        # 如果不大于1就是空值，就是显示最新的，所有的新闻列表按时间排序
        # paginate 是返回分页后的一个对象，而不是具体数据
        paginate = News.query.filter(*filters).order_by(News.create_time.desc()).paginate(page,per_page,False)
    except Exception as  e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg= '查询新闻列表数据异常')
    # 获取分页后的新闻数据，通过items、pages‘page，
    news_list = paginate.items # 获取新闻数据，依旧是个对象
    total_page = paginate.pages # 获取总页数
    current_page = paginate.page #@ 获取当前页数
    # 定义列表 ，用来存储 遍历news_list对象后的数据
    news_dict_list = []
    # 遍历分页后的新闻数据
    # 怎样确定是否要遍历对象，看最后拿到的是否是具体的数据，而不是一个包含多条数据的对象
    # 首先news_list 是一个包含多条新闻的对象，所以遍历它，
    # 拿到每一条新闻的对象，然后通过to_dict拿到每一条的具体数据，
    # 添加给news_dict_list 的空列表，
    # 然后news_dict_list就是一个包含多个新闻对象的具体数据的列表
    # 然后把多条数据 放到一个字典中返回
    for news in news_list:
        news_dict_list.append(news.to_dict())
    # 定义data 字典
    data= {
        'news_dict_list':news_dict_list,
        'totalpage': total_page,
        'current_page':current_page
    }
    # 返回结果,把data返回给前端
    return jsonify(errno= RET.OK,errmsg= 'ok',data=data)
# 新闻详情页面展示
@api.route('/<int:news_id>')
@login_required
def get_news_detail(news_id):
    """
    新闻详情页面
    1.尝试获取用户信息
    2.根据news_Id查询mysql
    3.判断查询数据结果
    4.进入某一个新闻详情，需要修改该新闻的点击次数clicks + 1
    5.构造字典直接，返回结果
    :return:
    """
    # 尝试获取用户信息，可能有，可能是空
    user = g.user
    # 根据news_id查询数据库
    try:
        # news = News.query.filter().first()
        news = News.query.get(news_id)
    except Exception  as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg= '数据库查询异常')
    # 判断结果
    if not news:
        return jsonify(errno=RET.NODATA,errmsg='该条新闻不存在')

    # 让新闻 的点击次数加1
    news.clicks += 1
    # 提交数据
    try:
        db.session.add(news)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg= '保存数据失败')
    # 构造字典
    data={
        'user': user.to_dict() if user else None,
        'news_detail': news.to_dict()
    }
    # 返回数据到模板
    return render_template('news/index.html',data=data)

# 实现取消和收藏
@api.route('/news_collect',methods=['POST'])
@ login_required
def news_collect():
    """
    # 收藏和取消收藏
    1.因为收藏必须是在用户登录的情况下，所以先尝试获取用户的信息
    2.如果我未登录，直接返回
    3.获取参数，news_id 和 action
    4.检查参数
    5.把news_id 转成int ，因为接受的json是字符串，所以要转成int，方便查询
    6.判断action参数必须为collect和 cancel_collect
        收藏和取消

    7根据news_id 查询收藏列表中是否存在该新闻，存在返回
    8.判断查询结果
    9.判断用户选择的是收藏还是取消
    10.返回结果
    """
    # 尝试获取用户信息
    user = g.user
    # 判断用户是否存
    if not user:
        return jsonify(errno=RET.SESSIONERR,errmsg='用户未登录')
    # 获取参数
    news_id = request.json.get('news_id')
    action = request.json.get('action')
    # 检查完整性
    if not all([news_id,action]):
        return jsonify(errno=RET.PARAMERR,errmsg='参数不完整')
    # 检查news_id格式 int
    try:
        news_id = int(news_id)
    except Exception as e:
        current_app.logger.erron(e)
        return jsonify(errno=RET.PARAMERR,errmsg='参数格式错误')
    # 检查action 是否是collect 或者 cancel_collect
    if action not in ['collect','cancel_collect']
        return jsonify(errno=RET.PARAMERR,errmsg='参数错误')
    # 查询数据库根据news_id
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DATAERR,errmsg='查询数据库异常')
    # 判断结果是否存在
    if not news:
        return jsonify(errno=RET.NODATA,errmsg='该新闻不存在')
    # 判断用户选择的是收藏还是取消收藏
    if action == 'collect':
        # 判断用户之前未收藏过该新闻,则添加
        if news not in user.collection_news:
            user.collection_news.append(news)
        else:
            return user.collection_news.remove(news)
    # 提交数据到数据库中
    try:
        db.session.add(user)
        db.session.commit() # commit会提交所有对user数据的操作
    except Exception as e :
        current_app.logger.error(e)
        # 提交数据不成功，记得要回滚到原来的数据
        db.session.rollback()
        return jsonify(errno=RET.DATAERR,errmsg='保存数据异常')
    return jsonify(errno=RET.OK,errmsg='收藏成功')