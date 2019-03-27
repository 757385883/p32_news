from redis import StrictRedis
# 2.2定义配置信息类
class Config:
    DEBUG = True
# 4.3配置数据库的连接和动态追踪
    SQLACHEMY_DATABASE_URI = 'mysql://root"mysql@lacalhost/info'
    SQLACHEMY_TRACK_MODIFYCATIONS = False

    # 5.2 配置状态保持存储的session信息
    SESSION_TYPE = 'redis'
#     5.3 配置session签名
    SESSION_USE_SIGNER =True
    #5.4构造redis实例
    SESSION_REDIS = StrictRedis(host='127.0.0.1',port=6379)

    #5.5配置session 的有效时间
    PERMANENT_SESSION_LIFETIME = 86400

    #5.6设置密钥
    SECRET_KEY = 'SDSAFGFFHSADWQ354I325HHEHWQOHAOD;FP'








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