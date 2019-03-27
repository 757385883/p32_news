# 7.导入日志和处理日志模块
import logging
from logging.handlers import RotatingFileHandler

# 5.导入falsk_session,用来设置session信息，状态保持
from flask_session import Session
# 2.导入配置文件中的字典，
from config import config
# 3.导入sqlachmy ，实例化对象，定义模型类
from flask_sqlalchemy import SQLAlchemy
from flask import Flask
app =Flask(__name__)


# 7.1设置日志的记录等级,创建文件夹logs用于存储日志
logging.basicConfig(level=logging.DEBUG) # 调试debug级
# 创建日志记录器，指明日志保存的路径、每个日志文件的最大大小、保存的日志文件个数上限
file_log_handler = RotatingFileHandler("logs/log", maxBytes=1024*1024*10, backupCount=10)
# 创建日志记录的格式 日志等级 输入日志信息的文件名 行数 日志信息
formatter = logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')
# 为刚创建的日志记录器设置日志记录格式
file_log_handler.setFormatter(formatter)
# 为全局的日志工具对象（flask app使用的）添加日志记录器,记录到current_app中，用来记录项目日志；
logging.getLogger().addHandler(file_log_handler)



# 6.3封装思想，工厂函数，通过参入不同的参数，生成不同模式下的app
# 3.1实例化sqlachemy 对象
db = SQLAlchemy()
def creat_app(config_name):
    # 2.1使用配置信息
    app.config.from_object(config[config_name])

    # 让db和app进行关联
    db.init_app(app)
    # 5.1实例话session对象
    Session(app)
    # 8.6导入蓝图对象，注册蓝图
    from info.modules.news import api
    app.register_blueprint(api)
    return app

