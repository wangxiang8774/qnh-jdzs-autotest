# !/usr/bin python3
# encoding: utf-8 -*-
# @author: 王翔
# @Time: 2021/11/5 19:10
import string
import random


def gen_rdm(randomlength=5, con_digits=True):
    """
    生成一个指定长度的随机字符串，其中
    string.digits=0123456789
    string.ascii_letters=abcdefghigklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ

    :param randomlength: 生成随机数据的长度，默认是5
    :param con_digits: 是否允许数字
    :return:
    """
    if con_digits:
        str_list = [
            random.choice(
                string.digits +
                string.ascii_letters) for i in range(randomlength)]
    else:
        str_list = [random.choice(string.ascii_letters)
                    for i in range(randomlength)]
    random_str = ''.join(str_list)
    return random_str


def gen_str_zh(randomlength=5):
    s = '我的祖国是花园花园的花朵真鲜艳和暖的阳光照耀着我们每个人脸上都肖开颜'
    str_list = [random.choice(s) for i in range(randomlength)]
    random_str = ''.join(str_list)
    return random_str


def gen_digit(start=0, end=10):
    return random.randint(start, end)


if __name__ == '__main__':
    print(gen_rdm())
    print(gen_str_zh())
    print(gen_digit(start=2000, end=3000))
