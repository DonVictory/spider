# coding = UTF-8
import json

import taoBaoCrawler
import mysqlmodel
import time

apiUrl = "https://h5api.m.taobao.com/h5/mtop.taobao.beehive.detail.contentservicenewv2/1.0/?"
api = "mtop.taobao.beehive.detail.contentservicenewv2"
contentId = "200412492147"
conf = {
    "jsv":"2.4.11",
    "appKey":"12574478",
    "t":"1520232544799",
    "sign":"2a8994578e47516dbcfc61f6b6117bed",
    "api":api,
    "v":"1.0",
    "AntiCreep":"true",
    "AntiFlood":"true",
    "type":"jsonp",
    "dataType":"jsonp",
    "callback":"mtopjsonp",
    "data": ""
}
headers = {
    "Accept":"*/*",
    "Accept-Encoding":"gzip, deflate, br",
    "Accept-Language":"zh-CN,zh;q=0.9,en;q=0.8",
    "Connection":"keep-alive",
    "Host":"h5api.m.taobao.com",
    "Referer":"",
    "User-Agent":"Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Mobile Safari/537.36"
}
startId = 200412492300
endId = 0
insField = "`content_id`, `account_id`, `account_name`, `account_type`, `account_desc`, `account_link`, `account_funs_count`, `account_tagname`, `config_appkey`, `config_biztype`, `config`,`modules`,`namespace`, `platform`, `content_detailurl`, `gmt_create`, `cotnent_item`,`read_count`, `content_summary`, `content_title`, `create_at`"
host = 'localhost'
user = 'demo'
passwd = '123456'
dbName = 'tkadmin'
insT = "tk_border_items"
insR = "tk_border_items_record"
connObj = mysqlmodel.mysqlmodel(host=host,user=user,passwd=passwd,dbname='tkadmin')
while True:
    print("%s" % str(startId))
    now = str(int(time.time()))
    try:
        crawlerInfo = taoBaoCrawler.taoBaoCrawler(apiUrl=apiUrl,conf=conf,headers=headers,contentId=str(startId),proxy = False)
        mtopJsonp = crawlerInfo.crawler('','').strip()
        data = json.loads(mtopJsonp[10:-1])
        if str(data).find("107::内容不存在") != -1:
            startId += 1
            raise Exception("content-error")
        if 'account' in data['data']['models'].keys() and data['data']['models']['account'] != None:
            accountId = data['data']['models']['account']['id']
            accountName = data['data']['models']['account']['name']
            if 'accountType' in data['data']['models']['account'].keys():
                accountType = data['data']['models']['account']['accountType']
            else:
                accountType = '0'
            accountDesc = data['data']['models']['account']['accountDesc']
            accountLink = data['data']['models']['account']['accountLink']
            accountFansCount = data['data']['models']['account']['fansCount']

            if 'accountTag' in data['data']['models']['account'].keys():
                accountTagName = data['data']['models']['account']['accountTag'][0]['tagName']
            else:
                accountTagName = '0'
        else:
            accountId = '0'
            accountName = '0'
            accountType = '0'
            accountDesc = '0'
            accountLink = '0'
            accountFansCount = '0'
            accountTagName = '0'
        if "appKey" in data['data']['models']['config'].keys():
            configAppkey = data['data']['models']['config']['appKey']
        else:
            configAppkey = 0
        bizType = data['data']['models']['config']['bizType']
        config = data['data']['models']['config']
        config = str(config).replace("'", "\\'")
        modules = data['data']['modules']
        modules = str(modules).replace("'","\\'")
        modulesNamespace = data['data']['models']['config']['namespace']
        modulesPlatform = data['data']['models']['config']['platform']
        contentDetailUrl = data['data']['models']['content']['detailUrl']
        gmtCreate = data['data']['models']['content']['gmtCreate'][0:10]
        contentItem = data['data']['models']['content']['id']
        readCount = data['data']['models']['content']['readCount']
        contentSummary = data['data']['models']['content']['summary']
        contentTitle = data['data']['models']['content']['title']
        contentTitle = contentTitle.replace("'","\\'")
        value = "('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s','%s','%s', '%s', '%s', '%s', '%s','%s', '%s', '%s', '%s')" % \
                (str(startId),accountId,accountName,accountType,accountDesc,accountLink,accountFansCount,accountTagName,configAppkey,bizType,
                 config,modules,modulesNamespace,modulesPlatform,contentDetailUrl,gmtCreate,contentItem,readCount,contentSummary,contentTitle,now)
        rs = connObj.insert(insT,insField,value)
        startId += 1
    except Exception as e:
        import sys
        s = sys.exc_info()
        print("Error '%s' happened on line %d" % (s[1], s[2].tb_lineno))
        print(e)
        data = str(data).replace('"','\\"')
        data = '"'+data.replace("'","’")+'"'
        connObj.insert(insR,'content_id,content','(%s,%s)' % (str(startId),data))
        time.sleep(0.2)
        continue
'''
12492299
Proccess loading...
200412492300
Proccess loading...
2018-03-06 17:59:15--(1064, "You have an error in your SQL syntax; check the manual that corresponds to your MySQL server version for the right syntax to use near 's Bees 唇彩/唇蜜', '1520330354')' at line 1")
200412492301
Proccess loading...
200412492302
'''