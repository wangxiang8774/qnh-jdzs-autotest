# !/usr/bin python3
# encoding: utf-8 -*-
# @author: 王翔
# @Time: 2021/11/5 19:10

import os
import platform
import random

import yaml


# 这只是一个辅助的代码，用来根据当前电脑所连接的设备自动生成devices.yml配置文件
from setting import DIR_NAME


def random_port(start=4000, end=9000):
    """
    随机生成一个未被占用的端口号
    :return:
    """
    port = random.randint(start, end)
    system_name = platform.system()  # 获取系统名称
    while(True):
        if system_name.lower() == 'windows':
            res = os.popen(
                'netstat -ano|findstr {}'.format(port)).read().strip()
            if 'LISTENING' not in res:
                break
            else:
                port = random.randint(start, end)
        else:
            res = os.popen('lsof -i:{}'.format(port)).read().strip()
            if 'LISTEN' not in res:
                break
            else:
                port = random.randint(start, end)

    return port


def get_devices():
    """
    获取当前电脑所连接的设备
    :return:
    """
    system_name = platform.system()  # 获取系统名称
    devices_list = []
    # 执行获取设备的命令 adb devices
    res = os.popen('adb devices').read().strip()
    print(res)
    # 解析res，从其中得到设备名称
    all_lines = res.split('\n')[1:]  # 得到所有的设备信息行
    for line in all_lines:
        udid = line.split()[0]
        status = line.split()[1]
        if status == 'device':
            port = random_port(end=5000)
            systemPort = random_port(start=5001, end=6000)
            chromedriverPort = random_port(start=7001, end=8000)
            # wdaPort = random_port(start=8001, end=9000)
            device_info = {
                'platform': 'android',
                'udid': udid,
                'port': port,  # 这是脚本和appium服务通信的端口
                'systemPort': systemPort,  # 这是appium服务和手机上uiautomator2通信的端口
                'chromedriverPort': chromedriverPort,  # 这是做安卓webview或者h5时chromedriver的端口
                # 'wdaPort': wdaPort #ios手机测试时appium服务和手机上wda的通信的端口
                'appiumserver': 'http://localhost'
            }
            devices_list.append(device_info)
    if platform.system().lower() != 'windows':
        res = os.popen('idevice_id -l').read().strip()
        all_lines = res.split('\n')
        for line in all_lines:
            udid = line.strip()
            port = random_port(end=5000)
            systemPort = random_port(start=5001, end=6000)
            chromedriverPort = random_port(start=7001, end=8000)
            wdaPort = random_port(start=8001, end=9000)
            device_info = {
                'platform': 'ios',
                'udid': udid,
                'port': port,
                'systemPort': systemPort,
                'chromedriverPort': chromedriverPort,
                'wdaPort': wdaPort,
                'appiumserver': 'http://localhost'
            }
            devices_list.append(device_info)
    # 拿到所有的信息后，写入yml配置文件
    with open(DIR_NAME + '/config/devices1.yml', 'w', encoding='UTF-8') as f:
        yaml.dump(devices_list, f)
    return devices_list


if __name__ == '__main__':
    print(get_devices())
