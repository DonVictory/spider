# -*- coding = utf8 -*-
# version = 2.7
# pymysqlModel:insert del update select

import time
import pymysql
__author__ = 'Drw'

class mysqlmodel(object):
    # init
    def __init__(self,host,user,passwd,dbname,port = 3306,charset = 'utf8'):
        self.conn = pymysql.Connect(
            host = host,
            port= port,
            user = user,
            passwd = passwd,
            db = dbname,
            charset = charset
        )
        self.cursor = self.conn.cursor()

    # insert
    def insert(self,tbName,field,values):
        insSql = "insert into %s(%s)values %s"  % (tbName,field,values)
        return self.excute(insSql)

    # select
    def select(self,tbName,field = '*',where = ''):
        if where:
            where = " where "+where
        selSql = "select %s from %s %s" % (field,tbName,where)
        return self.excute(selSql)
    # update
    def update(self, keyValues,tbName, where):
        setValue = ''
        for k,v in keyValues.items():
            setValue += '`%s`="%s",' % (k,v)
        if where:
            where = " where "+where
        updateSql = "update %s set %s %s" % (tbName,setValue[:-1],where)
        return self.excute(updateSql)
    # delete
    def delete(self,tbName, where):
        if where:
            where = " where "+where
        delSql = "delete from %s %s" % (tbName,where)
        return self.excute(delSql)



    # execute
    def excute(self, sql):
        try:
            if sql.find('select') != -1:
                self.cursor.execute(sql)
                return self.cursor.fetchall()
            elif sql.find('insert') != -1 or sql.find('update') != -1 or sql.find('delete') != -1:
                self.cursor.execute(sql)
                self.conn.commit()
                return True
            else:
                return False
        except Exception as e:
            print(str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())) + '--' + str(e))
            return False

    # __del__
    def __del__(self):
        self.cursor.close()
        self.conn.close()
