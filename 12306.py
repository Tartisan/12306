#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
__author__ = 'Tartisan'

import urllib.request
import urllib.parse
import ssl
import http.cookiejar
import re
import json
from time import sleep

# 打开配置参数文件
with open("initPar.json") as initPar:
    data = json.load(initPar)
    userName = data['userName']
    pwd = data['pwd']
    station_names = data['station_names']

stationDict = {}
for i in station_names.split('@')[1:]:
    stationList = i.split('|')
    stationDict[stationList[1]] = stationList[2]

train_date = '2018-04-20'  # 出发世间
fromStation = '成都'
toStation = '长沙'
from_station = stationDict[fromStation]  # 出发地
to_station = stationDict[toStation]  # 目的地

# 生成一个存储 cookie 的对象
c = http.cookiejar.LWPCookieJar()
cookie = urllib.request.HTTPCookieProcessor(c)
# 把对象绑定到 opener 里面
opener = urllib.request.build_opener(cookie)
urllib.request.install_opener(opener)

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'
}

# # 网址
# imgCode_url = 'https://kyfw.12306.cn/passport/captcha/captcha-image?login_site=E&module=login&rand=sjrand&0.9004386406168825'
# captcha_check_url = 'https://kyfw.12306.cn/passport/captcha/captcha-check'
# webLogin_url = 'https://kyfw.12306.cn/passport/web/login'
# userLogin_url = 'https://kyfw.12306.cn/otn/login/userLogin'
# leftTicket_url = 'https://kyfw.12306.cn/otn/leftTicket/queryO?leftTicketDTO.train_date=%s&leftTicketDTO.from_station=%s&leftTicketDTO.to_station=%s&purpose_codes=ADULT' % (train_date, from_station, to_station)
# checkUser_url = 'https://kyfw.12306.cn/otn/login/checkUser'
# submitOrderRequest_url = 'https://kyfw.12306.cn/otn/leftTicket/submitOrderRequest'

# ssl
ssl._create_default_https_context = ssl._create_unverified_context

# 登陆
def login():
    # 获取验证码图片
    print('正在获取验证码')
    req = urllib.request.Request(
        'https://kyfw.12306.cn/passport/captcha/captcha-image?login_site=E&module=login&rand=sjrand&0.9004386406168825'
        )
    req.headers = headers
    imgCode = opener.open(req).read()
    with open('code.png', 'wb') as fn:
        fn.write(imgCode)

    # 验证码请求
    req = urllib.request.Request(
        'https://kyfw.12306.cn/passport/captcha/captcha-check'
    )
    req.headers = headers
    code = input('请输入验证码： ')
    print('正在识别验证码')
    data = {
        'answer': code,
        'login_site': 'E',
        'rand': 'sjrand'
    }
    data = urllib.parse.urlencode(data).encode('utf-8')  # 转化为查询字符串
    html = opener.open(req, data=data).read().decode('utf-8')
    # 用户名、密码请求
    req = urllib.request.Request(
        'https://kyfw.12306.cn/passport/web/login'
        )
    req.headers = headers
    data = {
        'username': userName,
        'password': pwd,
        'appid': 'otn'
    }
    data = urllib.parse.urlencode(data).encode('utf-8')
    html = opener.open(req, data=data).read().decode('utf-8')
    result = json.loads(html)
    if result['result_code'] == 0:
        # 继续POST请求
        req = urllib.request.Request(
            'https://kyfw.12306.cn/otn/login/userLogin'
            )
        req.headers = headers
        data = {
            '_json_att': ''
        }
        data = urllib.parse.urlencode(data).encode('utf-8')
        html = opener.open(req, data=data).read().decode('utf-8')
        
        # 继续GET请求
        req = urllib.request.Request(
            'https://kyfw.12306.cn/otn/passport?redirect=/otn/login/userLogin'
            )
        req.headers = headers
        html = opener.open(req)

        # 继续POST请求
        req = urllib.request.Request(
            'https://kyfw.12306.cn/passport/web/auth/uamtk'
            )
        req.headers = headers
        data = {
            'appid': 'otn'
        }
        data = urllib.parse.urlencode(data).encode('utf-8')
        html = opener.open(req, data=data).read().decode('utf-8')
        result = json.loads(html)
        tk = result['newapptk']
        # 继续POST请求
        req = urllib.request.Request(
            'https://kyfw.12306.cn/otn/uamauthclient'
            )
        req.headers = headers
        data = {
            'tk': tk
        }
        data = urllib.parse.urlencode(data).encode('utf-8')
        html = opener.open(req, data=data).read().decode('utf-8')
        print('1001', html)
        return True
    else:
        print('登陆失败，正在重新登陆')
        sleep(5)
        login()

# 余票查询
def leftTicket():
    req = urllib.request.Request(
        'https://kyfw.12306.cn/otn/leftTicket/queryO?leftTicketDTO.train_date=%s&leftTicketDTO.from_station=%s&leftTicketDTO.to_station=%s&purpose_codes=ADULT' % (train_date, from_station, to_station)
    )
    req.headers = headers
    html = opener.open(req).read().decode('utf-8')
    result = json.loads(html)
    # print('1002', result)
    return result['data']['result']

# 买票
def buyTicket():
    # 下单第一个请求
    req = urllib.request.Request(
        'https://kyfw.12306.cn/otn/login/checkUser'
    )
    req.headers = headers
    data = {
        '_json_att':''
    }
    data = urllib.parse.urlencode(data).encode('utf-8')
    html = opener.open(req, data=data).read().decode('utf-8')
    # print('1003', html)
    
    # 下单第二个请求
    req = urllib.request.Request(
        'https://kyfw.12306.cn/otn/leftTicket/submitOrderRequest'
        )
    req.headers = headers
    data = {
        'secretStr': urllib.parse.unquote(tempList[0]),
        'train_date': train_date,
        'back_train_date': train_date,
        'tour_flag': 'dc',
        'purpose_codes': 'ADULT',
        'query_from_station_name': fromStation,
        'query_to_station_name': toStation,
        'undefined': ''
    }
    data = urllib.parse.urlencode(data).encode('utf-8')
    html = opener.open(req, data=data).read().decode('utf-8')
    # print('1004', html)

    # 下单第三个请求
    req = urllib.request.Request(
        'https://kyfw.12306.cn/otn/confirmPassenger/initDc'
        )
    req.headers = headers
    data = {
        '_json_att': ''
    }
    data = urllib.parse.urlencode(data).encode('utf-8')
    html = opener.open(req, data=data).read().decode('utf-8')
    globalRepeatSubmitToken = re.findall(r"globalRepeatSubmitToken = '(.*?)'", html)[0]
    key_check_isChange = re.findall(r"'key_check_isChange':'(.*?)'", html)[0]
    leftTicketStr = re.findall(r"'leftTicketStr':'(.*?)'", html)[0]
    # print('1005', globalRepeatSubmitToken)
    
    # 下单第四个请求
    req = urllib.request.Request(
        'https://kyfw.12306.cn/otn/confirmPassenger/getPassengerDTOs'
        )
    req.headers = headers
    data = {
        '_json_att': '',
        'REPEAT_SUBMIT_TOKEN': globalRepeatSubmitToken
    }
    data = urllib.parse.urlencode(data).encode('utf-8')
    html = opener.open(req, data=data).read().decode('utf-8')
    # print('1005', html)

    # 下单第五个请求
    req = urllib.request.Request(
        'https://kyfw.12306.cn/otn/confirmPassenger/checkOrderInfo'
        )
    req.headers = headers
    data = {
        'cancel_flag': '2',
        'bed_level_order_num': '000000000000000000000000000000',
        'passengerTicketStr': '3,0,1,汪涛,1,420703199207086371,15801862464,N', # 3代表硬卧
        'oldPassengerStr': '汪涛,1,420703199207086371,1_',
        'tour_flag': 'dc',
        'randCode': '',
        'whatsSelect': '1',
        '_json_att': '',
        'REPEAT_SUBMIT_TOKEN': globalRepeatSubmitToken
    }
    data = urllib.parse.urlencode(data).encode('utf-8')
    html = opener.open(req, data=data).read().decode('utf-8')
    print('1006', html)

    # 下单第六个请求
    req = urllib.request.Request(
        'https://kyfw.12306.cn/otn/confirmPassenger/confirmSingleForQueue'
    )
    data = {
        'passengerTicketStr': '3,0,1,汪涛,1,420703199207086371,15801862464,N',
        'oldPassengerStr': '汪涛,1,420703199207086371,1_',
        'randCode': '',
        'purpose_codes': '00',
        'key_check_isChange': key_check_isChange,
        'leftTicketStr': leftTicketStr,
        'train_location': 'W2',
        'choose_seats': '',
        'seatDetailType': '000',
        'whatsSelect': '1',
        'roomType': '00',
        'dwAll': 'N',
        '_json_att': '',
        'REPEAT_SUBMIT_TOKEN': globalRepeatSubmitToken
    }
    data = urllib.parse.urlencode(data).encode('utf-8')
    html = opener.open(req, data=data).read().decode('utf-8')
    print('1007', html)

if __name__ == '__main__':
    login()
    '''
    [3] = 车次
    [8] = 出发世间
    [9] = 到达世间
    [10] = 历时
    [23] = 软卧
    [28] = 硬卧
    [29] = 硬座
    '''
    index = 0
    for i in leftTicket():
        tempList = i.split('|')
        # print(tempList)
        # for n in tempList:
        #     print(index, n)
        #     index += 1
        try:
            if tempList[23] == u'有' or int(tempList[23]) > 0:
                print('''
                该车次有票：
                车次：%s
                出发世间：%s
                到达时间：%s
                历时：%s
                余票：%s
                ''' % (tempList[3], tempList[8], tempList[9], tempList[10], tempList[23]))
                break
        except:
            continue
    buyTicket()
