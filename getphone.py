# coding:utf-8

import tornado.web
import tornado.ioloop
import pymysql
from collections import deque


class IndexHandler(tornado.web.RequestHandler):

    def get(self):
        front_three = self.get_argument('front')  # 前三位
        province_city = self.get_argument('city')  # 城市
        self.write(sql_data(front_three, province_city))


class IndexVersion(tornado.web.RequestHandler):

    def get(self):
        self.write('1.0')


def sql_data(front_three, province_city):

    sql = "select _id from haoba where _id like '" + \
        front_three + "%'" " and city='" + province_city + "'"

    data = sql_connection(sql)
    phone_list = deque([str(i[0]) for i in data])

    if phone_list:
        return ','.join(phone_list)
    return '0'


def sql_connection(sql):
    try:
        conn = pymysql.connect(host='10.3.0.42',
                               user='root',
                               passwd='38,5BtC8.pkS2XX9',
                               db='phone_ali',
                               port=3306,
                               charset='utf8')
        cursor = conn.cursor()
        cursor.execute(sql)
        raw = cursor.fetchall()
        return raw

    finally:
        conn.close()


if __name__ == '__main__':
    app = tornado.web.Application(
        [(r'/getnumber', IndexHandler), (r'/version', IndexVersion)])
    app.listen(8080)
    tornado.ioloop.IOLoop.current().start()
