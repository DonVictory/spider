# -*- coding: utf8 -*-
# Tools Class
# CreateTime: 2017/12/28
__author__ = 'drw'

import urllib
import gzip
import time
import json
#from cStringIO import StringIO TODO:PY2.7-Supported

class tools(object):

    # __init__
    def __init__(self):
        pass

    # Cookie conversion dictionary type
    def cookieToDict(self,cookies,mode=None):
        try:
            dictVar = {}
            cookiesList = urllib.unquote(cookies).split(';')
            for cookieItem in cookiesList:
                key = cookieItem.split('=')[0].strip()
                value = cookieItem.split('=')[1].strip()
                dictVar[key] = value
            return dictVar
        except Exception as e:
            return False

    # Truncate string by label
    def subString(self,data, startTag, endTag, startMove=0, endMove=0):
        try:
            startPos = data.find(startTag) + startMove
            endPos = data.find(endTag) + endMove
            subRes = data[startPos:endPos]
            return subRes, startPos, endPos
        except Exception as e:
            return e,0,0

    # Unzip the gzip file
    def unzipFiles(self,gzipData):
        try:
            buffer = StringIO(gzipData)
            unGzipData = gzip.GzipFile(mode='rb',fileobj=buffer)
            return unGzipData.read(),'Unzip Successful.'
        except Exception as e:
            return e,'Thorw Error'

    # Is gzip format
    def isGzip(self,response):
        try:
            contentEncoding =  response.getheaders()
            for itme in contentEncoding:
                if itme[0] == 'content-encoding':
                    if itme[1].find('gzip') != -1:
                        return True, 'The Gzip File Is Gzip Format.'
                    else:
                        continue
                return False,'The Gzip File Is Not Gzip Format.'
        except:
            return False,'Response Error.'

    # Log
    def log(self, logInfo):
        now = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime())
        jsonStr = 'Log-info__Time:'+now+'  Info:'+logInfo+"\n"
        with open("F:\\Python\\logging\\log.txt",'a') as f:
            f.write(jsonStr)
        f.close()

    # time,date,now
    def timeFormat(self,timeValue='',type='now',append=''):
        import time
        try:
            if type == 'now':
                return (int(time.time()),time.strftime('%Y-%m-%d '+append,time.localtime()),time.strftime('%Y-%m-%d %H:%M:%S',time.localtime())),True
            elif type== 'timestamp':
                return (time.strftime('%Y-%m-%d',time.localtime(timeValue)),time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(timeValue))),True
            elif type == 'dateTime':
                if not append:
                    timeValue += ' 00:00:00'
                else:
                    timeValue += " "+append
                return (int(time.mktime(time.strptime(timeValue, "%Y-%m-%d %H:%M:%S")))),True
            else:
                return 0,False
        except Exception as e:
            return  e,False

if __name__ == '__main__':
    print('Info:tools')

