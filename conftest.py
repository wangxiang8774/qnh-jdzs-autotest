# !/usr/bin python3
# encoding: utf-8 -*-
# @author: 王翔
# @Time: 2021/11/5 19:10
import os
import threading
import time
from concurrent.futures.thread import ThreadPoolExecutor
from typing import List

import allure
import pytest
from PIL import ImageFile, Image

import setting
from common.driver import InitDriver, GlobalDriver

# shot_flag = True
from common.file_load import load_yaml_file
from common.server import AppiumServer


def pytest_collection_modifyitems(
        session: "Session", config: "Config", items: List["Item"]
) -> None:
    # item表示每个测试用例，解决用例名称中文显示问题
    for item in items:
        item.name = item.name.encode("utf-8").decode("unicode-escape")
        item._nodeid = item._nodeid.encode("utf-8").decode("unicode-escape")


@pytest.fixture(scope='session', autouse=True)
def init_driver(deviceinfo, worker_id):
    # 先启动启动appium server
    # 由于appium server启动后会阻塞代码执行，因此我们需要使用多线程的方式来执行自动启动server的方法
    port = deviceinfo['port']
    chromedriver_port = deviceinfo['chromedriverPort']
    tpe = ThreadPoolExecutor()
    # submit里边放得是你的要在线程里执行的函数，一定注意这个函数不要加()
    tpe.submit(AppiumServer().start, port, chromedriver_port)
    GlobalDriver.driver = InitDriver(deviceinfo)
    yield
    GlobalDriver.driver.quit()
    AppiumServer().stop(port)
    # 执行完之后清除截的图以及gif
    img_list = os.listdir('video')  # 获取video目录的所有文件
    for img_name in img_list:
        if img_name.startswith(worker_id):
            os.remove('video/' + img_name)


@pytest.fixture(scope='function', autouse=True)
def case_setup_teardown(worker_id):
    global shot_flag  # 增加全局变量shot_flag表示是否截图
    shot_flag = True
    ImageFile.LOAD_TRUNCATED_IMAGES = True
    # 每条用例一开始就截图，启动一个线程，来执行截图操作,后边的target参数表示你要执行的方法是哪个，args表示目标方法需要的参数
    t = threading.Thread(
        target=shot,
        args=(
            GlobalDriver.driver,
            worker_id))  # 创建一个线程对象，target表示线程里要执行的方法
    t.start()

    yield
    shot_flag = False
    # 实现当前用例图片的拼接，形成gif动态图，并将其放入测试报告中
    # 1.得到当前进程下所有的图片
    img_list = []  # 用来存储图片名称，gw00.png、gw01.png、gw02.png...gw0100.png
    for img_name in os.listdir('video'):  # 遍历video目录下所有的文件
        if img_name.startswith(worker_id) and img_name.endswith('.png'):
            img_list.append(img_name)
    # 针对img_list里的图片进行排序，因为拼接gif图时必须按照顺序去拼
    # 由于图片名称本身是一个字符串，排序时不好处理，所以我们选择将图片名称进行切片处理，得到图片的顺序数字
    # 然后以顺序数字作为排序的依据，那么key就是排序的依据
    if worker_id == 'master':
        img_list.sort(key=lambda x: int(x[6:-4]))
    else:
        img_list.sort(key=lambda x: int(x[3:-4]))

    # 开始拼接gif动态图
    # 先拿到第一张图，然后按照顺序依次追加到第一张图上
    first_img = Image.open(os.path.join('video', img_list[0]))  # 得到第一张图
    # 使用列表推导式，得到剩下的图片对象列表
    ele_imgs = [Image.open(os.path.join('video', img)) for img in img_list[1:]]
    first_img.save(setting.DIR_NAME + f'/video/{worker_id}record.gif',
                   append_images=ele_imgs,
                   duration=300,  # 每隔多久播放一个图片
                   save_all=True,
                   loop=0  # 自动播放，0是自动播放，1是不自动播放
                   )
    # 生成完成后将gif图放入测试报告中
    with open(setting.DIR_NAME + f'/video/{worker_id}record.gif', 'rb') as f:
        allure.attach(
            f.read(),
            '执行回放',
            attachment_type=allure.attachment_type.GIF)

    # 后置处理，每条用例执行完成都回到首页
    # GlobalDriver.driver.reset_app()
    GlobalDriver.driver.start_activity(
        'com.douban.frodo',
        'com.douban.frodo.activity.SplashActivity')
    time.sleep(5)
# 下面这个是pytest自带的一个钩子函数，我们在他们里边实现我们的业务


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    # 在测试用例执行失败时进行截图，并将截图放在报告上
    outcome = yield
    rep = outcome.get_result()
    # 如果当前用例正在执行并且结果是失败，那么就进行截图
    if rep.when == "call" and rep.failed:
        # 这里完成截图
        img = GlobalDriver.driver.get_screenshot_as_png()
        # 咱们的测试报告是allure
        allure.attach(img, '失败截图', attachment_type=allure.attachment_type.PNG)

# 多台设备同时执行，需要分配设备到不同的进程上，因此我们封装一个函数来实现


@pytest.fixture(scope='session', autouse=True)
def deviceinfo(worker_id):  # worker_id必须在安装了pytest-xdist以后才能用
    # 读取devices.yml,得到一个多设备的列表
    devices_list = load_yaml_file('/config/devices.yml')
    if worker_id == 'master':
        return devices_list[0]
    else:
        index = int(worker_id[2:])
        return devices_list[index]

# 该方法是用来不断截图的


def shot(dr, worker_id):
    # 截图之前先清除原来的用例图片
    img_list = os.listdir('video')  # 获取video目录的所有文件
    for img_name in img_list:
        if img_name.startswith(worker_id):
            os.remove('video/' + img_name)
    # 调用截图方法存储文件，在driver.py中补充方法后，在这里引用
    i = 0
    while shot_flag:
        try:
            dr.get_screenshot_as_file(f'video/{worker_id}{i}.png')
        except BaseException:
            return
        i += 1
        time.sleep(0.3)  # 每隔0.3秒截图


if __name__ == '__main__':
    s = 'gw018.png'
    print(s[3:-4])
    s = 'master18.png'
    print(s[6:-4])
