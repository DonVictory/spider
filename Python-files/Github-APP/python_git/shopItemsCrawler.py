# coding=UTF-8
import json

import mysqlmodel
import taoBaoCrawler
import time

host = '192.168.1.168'
user = 'demo'
passwd = '123456'
dbName = 'tkadmin'

connObj = mysqlmodel.mysqlmodel(host=host,user=user,passwd=passwd,dbname='tkadmin')
tab = "tk_market_items"
insField = "`content_id`, `item_id`, `user_id`, `account_name`, `item_current_price`, `item_trade_num`, `item_title`, `item_url`, `read_count`, `title`, `used`, `craete_at`"
apiUrl = 'https://h5api.m.taobao.com/h5/mtop.taobao.beehive.detail.contentrecommendservice/1.0/?'
conf = {
    "jsv":"2.4.11",
    "appKey":"12574478",
    "t":"1520232544799",
    "sign":"2a8994578e47516dbcfc61f6b6117bed",
    "api":"mtop.taobao.beehive.detail.contentrecommendservice",
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

while True:
    tbItmes = connObj.select(tab,"content_id","used='0'")
    if not tbItmes:
        print("done")
        time.sleep(2)
        continue
    else:
        for contentId in tbItmes:
            print("position:%s" % contentId[0])
            try:
                referer = "https://market.m.taobao.com/apps/market/content/index.html?wh_weex=true&wx_navbar_transparent=true&data_prefetch=true&contentId="+contentId[0]+"&source=youhh_h5&params=%7B%22csid%22%3A%227074d46e5ce8c18701ec01ff71d9037d%22%7D&sourceType=other&suid=bbea486b-439c-400c-b03b-3d40f64cbaa3&ut_sk=1.WOoFcw8ePFsDAPKQhVRdBmrh_21646297_1519982862490.Copy.33&un=718f4e8fe7dffe5d6eba67e1da5a29c3&share_crt_v=1&cpp=1&shareurl=true&spm=a313p.22.cb.935306423180&short_name=h.WuhoN4d&app=chrome"
                data = "{\"contentId\":\"%s\",\"type\":\"weex\",\"source\":\"youhh_h5\",\"frontModuleName\":\"recommendContent\",\"params\":\"{\\\"csid\\\":\\\"7074d46e5ce8c18701ec01ff71d9037d\\\"}\"}" % contentId[0]
                headers['Referer'] = referer
                conf['data'] = data
                tbObj = taoBaoCrawler.taoBaoCrawler(apiUrl,conf,headers)
                token, cookie = tbObj.forToken('','',contentId[0])
                crawlerInfo = tbObj.crawler(token, cookie)
                itemsList = json.loads(crawlerInfo.strip()[10:-1])
                now = str(int(time.time()))

                if 'ret' in itemsList.keys() and str(itemsList).find("内容不存在") != -1: # 内容不存在
                    print(itemsList)
                    continue
                for item in itemsList['data']['result']:
                    sel = connObj.select(tab,'id',"content_id='%s'" % item['id'])
                    if sel:
                        print("%s in %s" % (item['id'],tab))
                        continue
                    pos = item['account']['accountLink'].find("id=")+3
                    userId = str(item['account']['accountLink'][pos:])
                    price = item['item']['itemPriceDTO']['price']['item_current_price']
                    sold = item['item']['itemQualityDTO']['item_trade_num']
                    itemTitle = item['item']['itemTitle']
                    if itemTitle.find("'"): # 处理字符 '
                        itemTitle = itemTitle.replace("'","’")
                    if 'itemUrl' in item['item'].keys():
                        itemUrl = item['item']['itemUrl']
                    else:
                        itemUrl = '0'
                    insV = "('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')" % \
                           (item['id'],item['item']['itemId'],userId,item['account']['accountName'],price,sold,itemTitle,itemUrl,item['readCount'],item['title'],'0',now)
                    ins = connObj.insert(tab,insField,insV)
                    print(ins)
                connObj.update({"used":'1'},tab,"content_id='%s'" % contentId[0])
                time.sleep(0.2)
            except Exception as e:
                print(e)
                time.sleep(3)
                tbItmes.append((contentId['0'],))
                continue