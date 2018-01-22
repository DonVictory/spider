# -*- coding: utf-8 -*-
# py-verson = 3.6
__author__ = 'Drw'
import time
import json
import hashlib
import pymysql
import socket
import urllib.parse
from urllib import request
from http import cookiejar

def getCookie(url,cId):
    cookie = cookiejar.CookieJar()
    handler=request.HTTPCookieProcessor(cookie)
    opener = request.build_opener(handler)
    response = opener.open(url)
    if len(cookie._cookies.values()) > 0:
        return cookie
    else:
        return ''

def parse_jsonp(jsonp_str):
    try:
        import re
        return re.search('^[^(]*?\((.*)\)[^)]*$', jsonp_str).group(1)
    except:
        raise ValueError('Invalid JSONP')

def getModel(cId,token='',cookieInfo=''):
    t = str(int(time.time()))
    appKey = '12574478'
    api = 'mtop.taobao.beehive.detail.contentdetailservice'
    v = '1.0'
    type = 'jsonp'
    dataType = 'jsonp'
    callback = 'mtopjsonp1'
    data = "{\"contentId\":\"" + cId + "\",\"source\":\"darenhome\",\"type\":\"h5\"}"
    signMd5 = hashlib.md5()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 5.1.1; Nexus 6 Build/LYZ28E) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.23 Mobile Safari/537.36',
        'Referer': "http://market.m.taobao.com/apps/market/content/index.html?contentId=" + cId + "&source=darenhome",
        'Host': 'acs.m.taobao.com',
        'Accept': '*/*',
        'Connection': 'Keep-Alive',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.8',
        'Content-type': 'application/json'
    }
    data2 = token + '&' + t + '&' + appKey + '&' + data
    signMd5.update(data2.encode(encoding='utf-8'))
    sign = signMd5.hexdigest()
    parm = {'appKey': appKey, 't': t, 'sign': sign, 'api': api, 'v': v, 'type': type, 'dataType': dataType,'callback': callback, 'data': data}
    url = 'http://acs.m.taobao.com/h5/mtop.taobao.beehive.detail.contentdetailservice/1.0/?' + urllib.parse.urlencode(parm)
    socket.setdefaulttimeout(10)
    if cookieInfo is '':
        cookie = getCookie(url, cId)
        cookieInfo = ''
        for item in cookie:
            tmp = item.name + '=' + item.value + ';'
            cookieInfo += tmp
            if item.name == '_m_h5_tk':
                token = item.value
        token = token.split('_')[0]
        headers['Cookie'] = cookieInfo
        return getModel(cId=cId,token=token,cookieInfo=cookieInfo)
    else:
        try:
            headers['Cookie'] = cookieInfo
            req = urllib.request.Request(url=url, headers=headers)
            response = urllib.request.urlopen(req)
            tmp = response.read()
            res = str(tmp)
            if res.find('FAIL_SYS_TOKEN_EMPTY')!=-1 or  res.find('TOKEN_EXPIRED')!=-1 \
                    or res.find('FAIL_SYS_ILLEGAL_ACCESS')!=-1 or res.find('SESSION_EXPIRED')!=-1 \
                    :
                cookie = getCookie(url,cId)
                cookieInfo = ''
                for item in cookie:
                    tmp = item.name+'='+item.value+';'
                    cookieInfo += tmp
                    if item.name == '_m_h5_tk':
                        token = item.value
                token = token.split('_')[0]
                headers['Cookie'] = cookieInfo
                return getModel(cId=cId, token=token, cookieInfo=cookieInfo)
            elif res.find('503 Service Unavailable')!=-1 or len(res) == 0:
                time.time(0.5)
                cookie = getCookie(url, cId)
                cookieInfo = ''
                for item in cookie:
                    tmp = item.name + '=' + item.value + ';'
                    cookieInfo += tmp
                    if item.name == '_m_h5_tk':
                        token = item.value
                token = token.split('_')[0]
                headers['Cookie'] = cookieInfo
                return getModel(cId=cId, token=token, cookieInfo=cookieInfo)
            else:
                import gzip
                dataInfo = gzip.decompress(tmp).decode("utf-8")
                return dataInfo
        except Exception as e:
            time.time(0.5)
            cookie = getCookie(url, cId)
            cookieInfo = ''
            for item in cookie:
                tmp = item.name + '=' + item.value + ';'
                cookieInfo += tmp
                if item.name == '_m_h5_tk':
                    token = item.value
            token = token.split('_')[0]
            headers['Cookie'] = cookieInfo
            return getModel(cId=cId, token=token, cookieInfo=cookieInfo)

#连接数据库，取数据
conn = pymysql.Connect(
    host = 'rm-uf6l2i400pxdeb8eyo.mysql.rds.aliyuncs.com',
    port = 3306,
    user = 'taoke',
    passwd = 'mc9x8VgSUi',
    db = 'taoke',
    charset = 'utf8'
)

#配置信息
cursor = conn.cursor()
cursor.execute('select count(a.feedId) as num from  t_taobao_feed_info a INNER JOIN entrym_author_id b on a.accountId=b.author_id')
allCount = cursor.fetchone()
pageMax = allCount[0]//500
modData = allCount[0]%500
n = 0
page = 0
a = time.strftime("%b %d %Y", time.localtime())
insertTime = int(time.mktime(time.strptime(a,"%b %d %Y")))
length = allCount[0]
manyData = ''

while page <= pageMax :
    offset = page*500
    joinSql = 'select a.feedId from  t_taobao_feed_info a INNER JOIN entrym_author_id b on a.accountId=b.author_id limit 500 offset ' + str(offset)
    cursor.execute(joinSql)
    result = cursor.fetchall()
    for row in result:
        try:
            token = ''
            viewCount = json.loads(str(parse_jsonp(getModel(cId=row[0], token=token))))['data']['models']['content']['readCount']
            tmp = "('" + row[0] + "'," + viewCount + ',"0","0"' + ",'" + str(insertTime) + "'),"
            n = n + 1
            print('items:'+str(n))
            manyData = manyData + tmp
        except Exception as e:
            time.sleep(0.5)
            continue
        if n % 500 == 0 or length <= n  or (n % 500 == modData and page==pageMax):#500次提交数据或者遍历完成提交数据
            try:
                insSql = "insert into t_taobao_count_taoke(feedId,viewCount,commentCount,praiseCount,insertTime)values" + manyData[:-1]
                cursor.execute(insSql)
                conn.commit()
                insSql = ''
                manyData = ''
                print('page:' + str(page))
                page = page + 1
            except Exception as e:
                print(insSql)
                conn.rollback()
                continue