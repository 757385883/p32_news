from . import passport_blue
from flask import request,jsonify,current_app,make_response
# 13.导入自定义状态码
from info.utls.response_code import RET
# 13.2导入captcha
from info.utls.captcha.captcha import captcha
# 13.8 导入redis对象
from info import redis_store
# 13.9导入常量constants
from info import constants
#13.10 导入re
import re,random

# 13.11 导入云通讯
from info.libs.yuntongxun import sms

# 13.导入用户模型类
from info.models import User
@passport_blue.route('/image.code')
def gentate_image_code():
   """
   生成图片验证码：写接口步骤：获取参数，校验参数，业务处理，返回结果
   1.获取参数，uuid。使用查询字符串形式，requst.args
   2.校验参数uuid是否存在，不存在，直接return
   3.调用第三方接口captcha生成图片验证码：name,text,img
   4.在服务器redis数据库存储图片验证码
   5.返回图片本身，使用响应对象
   response = make_response(img)
   :return = response
   6.修改返回数据格式

   :return:
   """
   # 1.获取前端生成并传入的uuid，作为图片验证码名称的后缀名保存到redis中
   image_code_id = request.args.get('image_code-id')
   # 2.判断获取结果，不存在的化，返回json数据，使用jsonify和自定义的状态码，
   # 实现前后端的数据交互
   if not image_code_id:
       return jsonify(errno=RET.PARAMERR,errmsg='参数确实')
   # 3.使用captcha工具生成图片验证码
   name,text,img = captcha.generate_captcha()
   print(text)
   # 4.将图片验证码存储在redis中，必须现在实例化redis对象13.5
   # 在对数据库操作是，都需要异常处理，try，在数据库中保存，并设置有效时间
   try:
       redis_store.setex('ImageCode_'+ image_code_id,constants.IMAGE_CODE_REDIS_EXPIRES,text)
   except Exception as e: # 如果保存发生异常，执行
       current_app.logger.error(e) # 使用current_app 保存日志中的错误信息

       return jsonify(error=RET.DBERR,errmsg='保存图片验证码，失败')

   else: # 这是不发生异常需要执行的
       # 返回图片给前端
       response = make_response(img)
       # 修改响应数据类型
       response.headers['Content-Type']= 'image/jpg'
       return response

# 14.定义视图函数，用来处理短信验证,需要在表单中提交数据，请求方式post
@passport_blue.route('/sms_code',methods=['POST'])
def send_sms_code():
    """
    发送短信：1.获取参数，2.检查参数3.业务处理4.返回结果
    1.获取三个参数，手机号，uuid，输入验证码
    2.判断参数是否齐全
    3.校验手机号格式，是否正确
    4.获取本地的redis数据库中存储真实图片验证码；只能取一次，无论用户输入是否正确，都需要删除图片验证码
    5.判断获取结果，如果不存在，直接中止程序的执行，图片验证码过期
    6.删除内存中图片验证码
    7.比较图片验证码是否一致，因为图片验证码只能比较一次
    8.判断手机号是否注册
    9.比较一致，构造短信验证码，随机数六位，random。randint（）
    11.在redis数据库中存储短信验证码
    12.调用云通讯发送短信
    13.判断是否发送成功

    :return:
    """
    # 获取post请求的参数
    mobile = request.json.get('mobile')
    image_code = request.json.get('image_code')
    image_code_id = request.json.get('image_code_id')
    # 判断参数的完整性
    if not all([mobile,image_code,image_code_id]):
        return jsonify(erron=RET.PARAMERR,errmsg='参数不完整')
    # 检查手机号的格式
    if not re.match(r'^1[3456789]\d{9}$',mobile):
        return jsonify(erron=RET.PARAMERR,errmsg='手机号格式错误')
    # 从redis根据uuid获取图片验证码内容，查询依然使用try
    try:
        text_img = redis_store.get('ImageCode' + image_code_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(erron=RET.DBERR,errmsg='获取图片验证码失败')
    # 判断获取结果是否存在
    if not text_img:
        return jsonify(erron=RET.NODATA,errmsg='图片验证码过期')
    #删除图片验证码，因为图片验证码只能get一次
    try:
        redis_store.delete('ImageCode' + image_code_id)
    except Exception as e:
        current_app.logger.error(e)

    #比较图片验证码是否一致，lower 忽略大小写
    if text_img.lower() != image_code.lower():
        return jsonify(erron=RET.DATAERR, errmsg='图片验证码错误')
    # 判断手机是否已经注册
    try:
        user = User.query.filter(User.mobile==mobile).first()
    except Exception as a:
        current_app.logger.error(e)
        return jsonify(erron=RET.DBERR, errmsg='查询数据库异常')
    else:
        #判断查询结果是否有数据
        if user:
            return jsonify(erron=RET.DATAERR, errmsg='注册用户已存在')







    # 随机生成六位数，%06d 占位符，必须六位，前面为用0
    sms_code = '%06d' % random.randint(0,999999)
    # 将随机的生成的验证码，保存到redis中，为了比较验证码
    try:
        redis_store.setex('SMScode_' + mobile,constants.SMS_CODE_REDIS_EXPIRES,sms_code)
    except Exception as e:
        current_app.logger.error(e)# 将错误信息保存在日志里
        return jsonify(erron=RET.DBERR, errmsg='保存短信验证码失败')
    # 调运第三方接口云通讯发送信息，有网络连接的地方也用try
    try:
        # 实例化云通信对象
        ccp = sms.CCP()
        # 调用云通讯的模板方法发送短息
        result = ccp.send_template_sms(mobile,[sms_code,constants.SMS_CODE_REDIS_EXPIRES/60],1)
    except Exception as e:
        return jsonify(erron=RET.THIRDERR, errmsg='发送短信异常')
    # 判断发送结果
    if result == 0:
        return jsonify(erron=RET.OK, errmsg='发送成功')
    else:
        return jsonify(erron=RET.THIRDERR, errmsg='发送失败')


