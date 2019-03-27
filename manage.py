from flask import Flask
# 1.导入扩展 flask_script ,使用管理器
from flask_script import Manager
# 2.导入配置文件中的字典，
from config import config

app =Flask(__name__)

# 1.1实例化管理器对象
manage = Manager(app)

# 2.1使用配置信息
app.config.from_object(config['development'])

@app.route('/')
def index():
    return 'index2018'

if __name__ == '__main__':
    # app.run(debug=True)
    manage.run()