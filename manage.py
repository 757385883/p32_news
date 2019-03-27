from flask import Flask,session
# 1.导入扩展 flask_script ,使用管理器
from flask_script import Manager

# 4.导入数据迁移
from flask_migrate import Migrate,MigrateCommand

# 6.从info导入creat_app，创建的info包，就是用于真正的业务处理
from info import creat_app,db

app = creat_app('development')
# 1.1实例化管理器对象
manage = Manager(app)
# 4.1使用迁移框架
Migrate(app,db)
# 4.2添加迁移命令
manage.add_command('db',MigrateCommand)

# 8.创建modules包，用来添加业务处理中的视图函数



if __name__ == '__main__':
    # app.run(debug=True)
    manage.run()