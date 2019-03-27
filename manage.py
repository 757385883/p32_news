from flask import Flask
# 1.导入扩展 flask_script ,使用管理器
from flask_script import Manager
# 2.导入配置文件中的字典，
from config import config
# 3.导入sqlachmy ，实例化对象，定义模型类
from flask_sqlalchemy import SQLAlchemy
# 4.导入数据迁移
from flask_migrate import Migrate,MigrateCommand

# 5.导入falsk_session,用来设置session信息，状态保持
from flask_session import Session
app =Flask(__name__)

# 1.1实例化管理器对象
manage = Manager(app)

# 2.1使用配置信息
app.config.from_object(config['development'])
# 3.1实例化sqlachemy 对象
db = SQLAlchemy(app)
# 4.1使用迁移框架
Migrate(app,db)
# 4.2添加迁移命令
manage.add_command('db',MigrateCommand)

# 5.1实例话session对象
Session(app)
@app.route('/')
def index():
    return 'index2018'

if __name__ == '__main__':
    # app.run(debug=True)
    manage.run()