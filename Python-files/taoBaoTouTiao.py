# -*- coding:UTF-8 -*-
import time
import json
import hashlib
import pymysql
import socket
import urllib.parse
from urllib import request
from http import cookiejar

class taoBaoTouTiao(object):
    def __init__(self):
        pass

def md5(var):
    try:
        md5Var = hashlib.md5()
        md5Var.update(var.encode(encoding='utf-8'))
        return  md5Var.hexdigest()
    except Exception as e:
        return e

def cookie(url):
    try:
        cookie = cookiejar.CookieJar()
        handler = request.HTTPCookieProcessor(cookie)
        opener = request.build_opener(handler)
        response = opener.open(url)
        if len(cookie._cookies.values()) > 0:
            return cookie
        else:
            return ''
    except Exception as e:
        return e

def tokenFunc(cookies):
    try:
        cookieKeyValue = ''
        token = ''
        if len(cookies)!=0:
            for cookie in cookies:
                cookieKeyValue += cookie.name + '=' + cookie.value + ';'
                if cookie.name == '_m_h5_tk':
                    token = cookie.value.split('_')[0]
                else:
                    continue
            if not token:
                return None,None
            else:
                return token,cookieKeyValue
        return None, None
    except Exception as e:
        return e,None

def printLog(log):
    now = str(time.strftime("%Y-%m-%d %H:%M:%S",time.localtime()))
    print(now+', error:'+log)
    exit(0)

url = 'https://h5api.m.taobao.com/h5/mtop.taobao.hlservice.feed.list/1.0/?'
def touTiao(indexUrl,tokenValue = None,cookiesValue = None):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 5.1.1; Nexus 6 Build/LYZ28E) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.23 Mobile Safari/537.36',
        'Referer': 'https://market.m.taobao.com/apps/market/toutiao/portal.html?wh_weex=true&data_perfetch=true',
        'Host': 'h5api.m.taobao.com',
        'Accept': '*/*',
        'Connection': 'Keep-Alive',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.8',
        'Content-type': 'application/json'
    }
    data = "{\"app\":\"tbc\",\"version\":\"17.0\",\"userType\":1,\"action\":\"1\",\"columnId\":\"0\"}" #get中的data
    token = str(tokenValue)
    timestamp = str(int(round(time.time()*1000)))
    appKey = '12574478'
    jsv = '2.4.2'
    signData = token + '&' + timestamp + '&' + appKey + '&' + data
    sign = md5(var=signData)
    urlParms = {}
    urlParms['jsv'] = jsv
    urlParms['appKey'] = appKey
    urlParms['t'] = timestamp
    urlParms['sign'] = sign
    urlParms['api'] = 'mtop.taobao.hlservice.feed.list'
    urlParms['v'] = '1.0'
    urlParms['AntiCreep'] = 'true'
    urlParms['timeout'] = 5000
    urlParms['type'] = 'jsonp'
    urlParms['dataType'] = 'jsonp'
    urlParms['callback'] = 'mtopjsonp'
    urlParms['data'] = data
    urlQuery = urllib.parse.urlencode(urlParms)
    url = "https://h5api.m.taobao.com/h5/mtop.taobao.hlservice.feed.list/1.0/?%s" % urlQuery
    print(url)
    cookies = cookie(url=url)
    tokenValue, cookieKeyValue = tokenFunc(cookies=cookies)
    print(cookieKeyValue)
    # printLog(log='获取token出错')
    if not cookieKeyValue:
        cookies = cookie(url=url)
        tokenValue, cookieKeyValue = tokenFunc(cookies=cookies)
        return touTiao(indexUrl=indexUrl,tokenValue=token,cookiesValue=cookieKeyValue)
    else:
        try:
            headers['Cookie'] = cookieKeyValue
            req = urllib.request.Request(url=url, headers=headers)
            response = urllib.request.urlopen(req)
            responseInfo = response.read()
            responseStr = str(responseInfo)
            print(responseStr)
            if responseStr.find('FAIL_SYS_TOKEN_EMPTY')!=-1 or responseStr.find('TOKEN_EXPIRED') != -1 or \
                    responseStr.find('FAIL_SYS_ILLEGAL_ACCESS') != -1 or responseStr.find('SESSION_EXPIRED') != -1:
                time.sleep(0.2)
                cookies = cookie(url=url)
                tokenValue, cookieKeyValue = tokenFunc(cookies=cookies)
                return touTiao(indexUrl=indexUrl, tokenValue=tokenValue, cookiesValue=cookieKeyValue)
            else:
                import gzip
                dataInfo = gzip.decompress(responseInfo).decode("utf-8")
                print(dataInfo)
                return dataInfo
        except Exception as e:
            import sys
            s = sys.exc_info()
            print("Error '%s' happened on line %d" % (s[1],s[2].tb_lineno))
            return e

indexUrl = 'https://h5api.m.taobao.com/h5/mtop.taobao.hlservice.feed.list/1.0/?'
resVar = touTiao(indexUrl=indexUrl,tokenValue='',cookiesValue='')
print(resVar)