# coding=gbk

import  urllib
import gzip
import re
from urllib import request
from urllib import  parse

import time
from bs4 import BeautifulSoup
import mysqlmodel



def detail(shopId,pageNo):
    try:
        url = "https://shop%s.taobao.com/i/asynSearch.htm?" % shopId
        urlParms = {}
        urlParms['_ksTS'] = '1519610649822_238'
        urlParms['callback'] = 'jsonp'
        urlParms['mid'] = 'w-15008121124-0'
        urlParms['wid'] = '15008121124'
        urlParms['path'] = '/search.htm'
        urlParms['search'] = 'y'
        urlParms['orderType'] = 'newOn_desc'
        urlParms['pageNo'] = pageNo
        queryParms = parse.urlencode(urlParms)
        headers = {
            'authority':'shop%s.taobao.com' % shopId,
            'method':'GET',
            'scheme':'https',
            'accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'accept-encoding':'gzip, deflate, br',
            'accept-language':'zh-CN,zh;q=0.9,en;q=0.8',
            'referer':'https://www.taobao.com/',
            'user-agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36',
            'path':'/i/asynSearch.htm?_ksTS=1519610649822_238&callback=jsonp239&mid=w-15008121124-0&wid=15008121124&path=/search.htm&search=y&orderType=newOn_desc'
        }

        queryUrl = url+queryParms
        #print(queryUrl)
        req = request.Request(url=queryUrl,headers=headers)
        response = urllib.request.urlopen(req)
        readInfo = response.read()
        data = str(gzip.decompress(readInfo).decode("gbk")).strip()
        return data
    except Exception as e:
        print(e)



try:
    with open("D:\\app\\pycharm-files\\youhaohuo\\task-conf\\xiaoliang.json",'r') as f:
        import json
        conf = json.load(f)
        f.close()
except Exception as e:
        with open("D:\\app\\pycharm-files\\youhaohuo\\task-conf\\log.txt", 'a') as logFile:
            logData = 'Log-info:'+str(time.strftime("%Y-%m-%d %H:%M:%S",time.localtime()))+",Error:configuration is null,"+'Exception:'+str(e)+'\n'
            logFile.write(logData)
            logFile.close()
            exit(0)

dataInfo = conf['xiaoliang']['publicInfo']
host = dataInfo['host']
user = dataInfo['user']
passwd = dataInfo['passwd']
dbName = dataInfo['db']

connObj = mysqlmodel.mysqlmodel(host=host,user=user,passwd=passwd,dbname='tkadmin')
insField = "`shop_id`, `shop_item_id`, `shop_item_url`, `dat_gold_data`,`img_alt`, `img_url`, `c_price`, `s_price`, `sale_num`, `comments_url`, `comments_num`, `create_at`"
tbName = dataInfo['shopIdTable']
insTbD = dataInfo['shopDetailTable']
insTbR = dataInfo['shopRecordTable']

info = conf['xiaoliang']['xiaoliangTask']
page  = info['pageNo']
size = info['size']
limit = "limit %s offset %s" % (str(size),str(int(size)*int(page)))

shops = connObj.select(tbName,'distinct shopurl','status=1 order by %s %s %s' % (info['orderBy'],info['sort'],limit)) # 数据库所有店铺
shopList = list()
for i in shops:
    shopList.append(i[0])
counter = 0
for shop in shopList:
    print("=====================shopId:%s====================" % shop)
    counter += 1
    page = 1
    pageEnd = 1
    shopId = shop
    while page<=int(pageEnd):
        try:
            now = int(time.time())
            date = time.strftime("%Y-%m-%d",time.localtime(now))
            print("===========页码：%s============" % str(page))

            data = detail(str(shopId), page)
            #print(data)
            # data = data.replace("\\n","")
            # data = data.replace("\\r","")
            data = data.replace("\\", "")
            html = data[7:-2]
            soup = BeautifulSoup(html, "html.parser")
            items = soup.select(".item")
            insData = {}
            if page<=1:
                try:
                    pageInfo = soup.find(attrs={'class': "page-info"}).string
                    pageEnd = int(pageInfo.split("/")[1])  # 店铺翻页
                except:
                    pageEnd = 1 # 异常处理
            page += 1
            for item in items:
                insData['shopItemId'] = item['data-id']
                itemInData = connObj.select(insTbD,'id','shop_id="%s" and shop_item_id="%s"' % (shopId,insData['shopItemId']))
                if itemInData:
                    attribute = item.find("div", "attribute")
                    rates = item.find(attrs={'class': "rates"})
                    saleNum = attribute.find(attrs={'class': 'sale-num'}).get_text()  # 销量
                    commentsNum = rates.find(name="a").string  # 评论条数
                    valueUp = "('%s','%s','%s','%s','%s','%s')" % (shopId, insData['shopItemId'], saleNum, commentsNum, date, str(now))
                    insR = connObj.insert(insTbR,'`shop_id`,`shop_items_id`,`sale_num`,`comments_num`,`create_date`,`create_at`',valueUp)
                    print("%s existed" % insData['shopItemId'])
                    print("insert RT: %s" % str(insData['shopItemId']))
                    continue
                J_TGoldData = item.find("a", "J_TGoldData")
                insData['shopItemUrl'] = J_TGoldData.attrs['href'][2:] # 店铺URL
                insData['datGoldData'] = J_TGoldData.attrs['data-gold-data'] # go-key
                insData['imgAlt'] = J_TGoldData.find("img").attrs['alt'] # 图片说明
                insData['imgUrl'] = J_TGoldData.find("img").attrs['src'] # 图片SRC
                attribute = item.find("div", "attribute")
                insData['cPrice'] = attribute.find(attrs= {'class':'c-price'}).get_text() # 现价
                try:
                    insData['sPrice'] = attribute.find(attrs= {'class':'s-price'}).get_text() # 原价
                except:
                    insData['sPrice'] = 'null'
                insData['saleNum'] = attribute.find(attrs= {'class':'sale-num'}).get_text() # 销量
                rates = item.find(attrs={'class':"rates"})
                insData['commentsUrl'] = rates.find(name="a").attrs['href'][2:] # 评论URL
                insData['commentsNum'] = rates.find(name="a").string # 评论条数
                if insData['imgAlt'].find("'"):
                    insData['imgAlt'] = insData['imgAlt'].replace("'","’")
                valueDetail = "('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s','%s')" % \
                        (shopId,insData['shopItemId'],insData['shopItemUrl'],insData['datGoldData'],
                         insData['imgAlt'],insData['imgUrl'],insData['cPrice'],insData['sPrice'],
                         insData['saleNum'],insData['commentsUrl'],insData['commentsNum'],str(now))
                insD = connObj.insert(insTbD,insField,valueDetail)
                print("详情执行结果：%s" % insD)
                valueUp = "('%s','%s','%s','%s','%s','%s')" % (shopId,insData['shopItemId'],insData['saleNum'],insData['commentsNum'],date,str(now))
                insR = connObj.insert(insTbR, '`shop_id`,`shop_items_id`,`sale_num`,`comments_num`,`create_date`,`create_at`', valueUp)
                print("insert RT：%s" % insR)
        except Exception as e:
            print(e)
            page += 1
            time.sleep(2)
            continue

# 保存任务执行日志
with open("D:\\app\\pycharm-files\\youhaohuo\\task-conf\\log.txt", 'a') as logFile:
    logData = 'run-stat-info:' + str(time.strftime("%Y-%m-%d %H:%M:%S",time.localtime())) + ",taskNo:0"+ '\n'
    logFile.write(logData)
    logFile.close()

