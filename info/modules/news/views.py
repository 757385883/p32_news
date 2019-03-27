# 8.2从同一个目录导入蓝图对象
from . import api
from flask import session,render_template,current_app

# 8.3使用蓝图对象
@api.route('/')
def index():
    session['name'] = '2019'
    # 返回渲染数据,将template改为模板格式
    return render_template('news/index.html')

# 项目 logo图标展示
@api.route('/favicon.ico')
def favicon():
    # 使用current_app调用发送静态文件的方法，把项目logo文件发给浏览器
    return current_app.send_static_file('news/favicon.ico')