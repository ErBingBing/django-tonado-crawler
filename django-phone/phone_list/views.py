# -*-coding:utf-8 -*-
# from django.shortcuts import render
from django.http import HttpResponse
from django.db import connection
from collections import deque


def index(request):
    front_three = request.GET.get('front')  # 前三位
    after_four = request.GET.get('after')  # 后三位
    province_city = request.GET.get('city')  # 城市

    sql = "select _id from haoba where _id like '" + \
        front_three + "%'" "and city='" + province_city + "'"
    phone_list = deque([])

    return HttpResponse(is_two_four(after_four, sql, phone_list))


# 创建游标
def sql_connection(sql, phone_list, after_four):

    cursor = connection.cursor()
    cursor.execute(sql)
    raw = cursor.fetchall()
    print raw
    cursor.close()

    if len(after_four) == 2:
        for i in raw:
            phone_list.append(str(i[0]))
        return phone_list

    if len(after_four) == 4:
        for i in raw:
            phone_list.append(str(i[0]) + after_four)
        return phone_list


# 版本号
def version(request):
    return HttpResponse('1.0')


# 判断三位还是四位
def is_two_four(after_four, sql, phone_list):
    if len(after_four) == 2:
        data = sql_connection(sql, phone_list, after_four)
        if len(data) == 0:
            return '0'
        return ','.join(data)

    if len(after_four) == 4:
        data = sql_connection(sql, phone_list, after_four)

        if len(data) == 0:
            return '0'
        return ','.join(data)

# # 添加后四位
# def add_after_four(raw, after_four):
#     phone_list = []
#     new_phone_list = []

#     if len(after_four) == 4:
#         for i in raw:
#             phone_list.append(str(i[0]) + after_four)
#         return phone_list

#     if len(after_four) == 2:
#         an = add_two_number()
#         for i in raw:
#             phone_list.append(str(i[0]))
#             for i in phone_list:
#                 for j in an:
#                     new_phone_list.append(str(i) + str(j) + after_four)
#         return new_phone_list


# # 添加倒数第三位和第四位
# def add_two_number():
#     add_list = []
#     for i in range(1, 100):
#         add_list.append(str(i).zfill(2))
#     return add_list
