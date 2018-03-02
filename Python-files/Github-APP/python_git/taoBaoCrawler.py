# -*- conding = UTF-8 -*-
# author: Drw
# 2018.3.2

import time
import hashlib
from http import cookiejar
from urllib import request
from urllib import parse

class taoBaoCrawler(object):

    def __init__(self,apiUrl,conf=dict(),headers=dict(),proxy=dict()):
        if apiUrl and len(conf) and len(headers):
            print("Proccess loading..")
            self.apiUrl = apiUrl
            self.conf = conf
            self.headers = headers
            self.proxy = proxy
        else:
            print("Parms errors!")
            exit(0)
    # 代理
    def proxy(self):
        # 代理服务器
        proxyHost = "http-dyn.abuyun.com"  # ""http-pro.abuyun.com"
        proxyPort = "9020"  # "9010"
        # 代理隧道验证信息
        proxyUser = "H36BH9760325S21D"
        proxyPass = "A22EAE41B499623C"
        proxyMeta = "http://%(user)s:%(pass)s@%(host)s:%(port)s" % {
            "host": proxyHost,
            "port": proxyPort,
            "user": proxyUser,
            "pass": proxyPass,
        }
        proxy_handler = request.ProxyHandler({
            "http": proxyMeta,
            "https": proxyMeta,
        })
        openner = request.build_opener(proxy_handler)
        return openner

    # MD5
    def md5(self,var):
        try:
            md5Var = hashlib.md5()
            md5Var.update(var.encode(encoding='utf-8'))
            return md5Var.hexdigest()
        except Exception as e:
            return e

    # 获取cookie
    def cookie(self,url):
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

    # 获取token
    def token(self,cookies):
        try:
            cookieKeyValue = ''
            token = ''
            if len(cookies) != 0:
                for cookie in cookies:
                    cookieKeyValue += cookie.name + '=' + cookie.value + ';'
                    if cookie.name == '_m_h5_tk':
                        token = cookie.value.split('_')[0]
                    else:
                        continue
                if not token:
                    return None, None
                else:
                    return token, cookieKeyValue
            return None, None
        except Exception as e:
            return e, None

    # 打印错误
    def errLog(self,e):
        import sys
        s = sys.exc_info()
        print("Error '%s' happened on line %d" % (s[1], s[2].tb_lineno))
        print(e)

    # 爬虫主程序
    def crawler(self,token,cookie):
        try:
            t = str(int(time.time()*1000))
            signPre = "%s%s%s%s" % (token,t,self.conf['appKey'],self.conf['data'])
            sign = self.md5(signPre)
            self.conf['sign'] = sign
            apiUrl = self.apiUrl+parse.urlencode(self.conf)
            if not cookie:
                token,cookie = self.cookie(url=apiUrl)
                return self.crawler(token=token,cookie=cookie)
            else:
                request.install_opener(self.proxy())
                reqHandler = request.Request(url=apiUrl,headers=self.headers)
                response = request.urlopen(reqHandler)
                rs = response.read()
                checkError = str(rs)
                if checkError.find("FAIL_SYS_TOKEN_EMPTY") !=-1 or checkError.find("TOKEN_EXPIRED")!=-1 \
                        or checkError.find("FAIL_SYS_ILLEGAL_ACCESS")!=-1 or checkError.find("FAIL_SYS_ILLEGAL_ACCESS")!=-1:
                    time.sleep(0.5)
                    token, cookie = self.cookie(url=apiUrl)
                    return self.crawler(token=token, cookie=cookie)
                else:
                    try:
                        import gzip
                        data = gzip.decompress(rs).decode('utf-8')
                    except:
                        data = rs.decode('utf-8')
                    return data
        except Exception as e:
            self.errLog(e)







