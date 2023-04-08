# -*- coding:utf-8 -*-
# ==========================================
#       Author: ZiChen
#        📧Mail: 1538185121@qq.com
#         ⌚Time: 2023/04/03 14:42:51
#           Django不支持Deta Base但支持SQlite3
#               该库旨在实现SQlite3和Deta Base之间的数据交换
# ==========================================
import sqlite3
from deta import Deta


class DetaINOUT:
    def __init__(self, key: str, dbname: str):
        '''
        链接数据库
        key 总数据库密钥
        dbname 需要链接的数据库名   
        '''
        self.deta = Deta(key)
        self.db = self.deta.Base(dbname)

    def Deta_GET(self):
        '''
        获取数据库数据（字典形式）
        获得到的数据如下
        [
        {
            "key": "key-1",
            "name": "Wesley",
            "age": 27,
            "hometown": "San Francisco",
        },
        {
            "key": "key-2",
            "name": "Beverly",
            "age": 51,
            "hometown": "Copernicus City",
        }
        ]
        '''
        return self.db.fetch().items

    def Deta_PUT(self, key=None, name=None, age=None, hometown=None):
        '''

        '''
        self.db.put({"name": name,
                     "age": age,
                     "key": key,
                     "hometown": hometown})


class SQL3INOUT:
    def __init__(self, SheetName: str):
        '''
        链接数据库
        SheetName 需要链接的表名   
        '''
        self.SheetName = SheetName

    def SQ_GET(self):
        '''
        返回数据格式
        [(列1,...)]
        '''
        conn = sqlite3.connect('db.sqlite3')
        cursor = conn.cursor()
        # 执行SQL语句
        cursor.execute("SELECT * FROM %s" % self.SheetName)
        # 获取所有结果
        results = cursor.fetchall()
        # 关闭连接
        conn.close()
        # 打印结果
        return results

    def SQ_CLEAR(self):
        '''
        清空表内所有数据
        '''
        conn = sqlite3.connect('db.sqlite3')
        cursor = conn.cursor()
        # 执行SQL语句
        cursor.execute("DELETE FROM %s" % self.SheetName)
        # 提交更改
        conn.commit()
        # 关闭连接
        conn.close()
        print('[debug]%s Clear' % self.SheetName)

    def SQ_PUT(self, form, content):
        '''
        form 表头内容
        content 写入内容，元组形式
        '''

        conn = sqlite3.connect('db.sqlite3')
        cursor = conn.cursor()
        # 执行插入数据的SQL语句
        cursor.execute("INSERT INTO %s %s VALUES %s" %
                       (self.SheetName,  str(form), str(content)))
        # 提交更改
        conn.commit()
        # 关闭连接
        conn.close()
