# 8.1创建蓝图对象
from flask import Blueprint

#
api =Blueprint('api',__name__)

# 8.4把使用蓝图对象的文件导入到创建蓝图对象的下面
from . import views