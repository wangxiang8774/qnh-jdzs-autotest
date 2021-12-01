# !/usr/bin python3
# encoding: utf-8 -*-
# @author: 王翔
# @Time: 2021/11/5 19:10
import os

import pytest

if __name__ == '__main__':
    # 执行时会按照pytest.ini这个配置所配的相关信息进行执行
    pytest.main()
    os.system('allure generate ./report/shop -o ./report/html --clean')
