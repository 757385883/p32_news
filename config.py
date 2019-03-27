class Config:
    DEBUG = True


# 开发模式下的配置信息
class developmentConfig(Config):
    DEBUG = True

#   生产模式下的配置信息
class productionConfig(Config):
    DEBUG =False

# 定义一个字典，用来存储 配置模式的键值对，便于被导入，不同的模式

config ={
    'development' : developmentConfig,
    'production' : developmentConfig
}