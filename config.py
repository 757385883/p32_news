# 2.2定义配置信息类
class Config:
    DEBUG = True
# 4.3配置数据库的连接和动态追踪
    SQLACHEMY_DATABASE_URI = 'mysql://root"mysql@lacalhost/info'
    SQLACHEMY_TRACK_MODIFYCATIONS = False
# 2.3开发模式下的配置信息
class developmentConfig(Config):
    DEBUG = True

#   2.4生产模式下的配置信息
class productionConfig(Config):
    DEBUG =False

# 2.5定义一个字典，用来存储 配置模式的键值对，便于被导入，不同的模式

config ={
    'development' : developmentConfig,
    'production' : developmentConfig
}