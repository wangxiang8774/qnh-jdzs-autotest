# !/usr/bin python3
# encoding: utf-8 -*-
# @author: 王翔
# @Time: 2021/11/5 19:10
import time

from appium import webdriver
from appium.webdriver.common.mobileby import MobileBy
from appium.webdriver.common.touch_action import TouchAction
from appium.webdriver.extensions.android.nativekey import AndroidKey
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait

from common.file_load import load_yaml_file
from common.logger import GetLogger


class GlobalDriver:
    driver = None


class InitDriver:

    def __init__(self, deviceinfo):
        """
        :param deviceinfo: 设备信息，从config/devices.yml中解析出来的
        """
        self.logger = GetLogger().get_logger()
        self.platform = deviceinfo['platform']
        self.udid = deviceinfo['udid']
        self.appiumserver = deviceinfo['appiumserver']
        self.port = deviceinfo['port']
        self.caps = {}
        # self.caps['udid']=self.udid
        if self.platform == 'android':
            self.systemPort = deviceinfo['systemPort']
            self.chromedriverPort = deviceinfo['chromedriverPort']
            self.caps = load_yaml_file('/config/android.yml')
            self.caps['systemPort'] = self.systemPort
            self.caps['chromedriverPort'] = self.chromedriverPort
        elif self.platform == 'ios':
            self.caps = load_yaml_file('/config/ios.yml')
        else:
            raise Exception('platform：{}不支持'.format(self.platform))
        self.caps['udid'] = self.udid
        self.driver = webdriver.Remote(
            f'{self.appiumserver}:{self.port}/wd/hub', self.caps)
        # self.driver.maximize_window() #最大化窗口
        self.logger.info('初始化成功')

    def get(self, url):
        self.driver.get(url)

    # 需要封装相关的各种操作
    # 自定义查找元素的基本信息是{'name':'登录按钮','type':'linktext','value':'登录','timeout':5}
    def find_element(self, ele_info):
        # 通过解析ele_info，拿到元素的相关信息以后，再使用显式等待针对元素进行查找，并且记录相关日志
        name = ele_info['name']
        timeout = ele_info['timeout']
        value = ele_info['value']
        locator = self.getBy(ele_info)
        try:
            wait = WebDriverWait(driver=self.driver, timeout=timeout)
            element = wait.until(
                expected_conditions.presence_of_element_located(locator))
            self.logger.info('查找【{}】使用【{},{}】定位成功'.format(name, type, value))
        except Exception as e:
            self.logger.error(
                '查找【{}】使用【{},{}】定位失败,失败原因：{}'.format(
                    name, type, value, e))
            raise Exception(
                '查找【{}】使用【{},{}】定位失败,失败原因：{}'.format(
                    name, type, value, e))
        return element

    def getBy(self, ele_info):
        name = ele_info['name']
        type = ele_info['type'].lower()
        value = ele_info['value']
        timeout = ele_info['timeout']
        if type == 'id':
            locator = (By.ID, value)
        elif type == 'name':
            locator = (By.NAME, value)
        elif type == 'classname':
            locator = (By.CLASS_NAME, value)
        elif type == 'linktext':
            locator = (By.LINK_TEXT, value)
        elif type == 'partiallinktext':
            locator = (By.PARTIAL_LINK_TEXT, value)
        elif type == 'tagname':
            locator = (By.TAG_NAME, value)
        elif type == 'css' or type == 'cssselector':
            locator = (By.CSS_SELECTOR, value)
        elif type == 'xpath':
            locator = (By.XPATH, value)
        elif type == 'uiautomator':
            locator = (MobileBy.ANDROID_UIAUTOMATOR, value)
        elif type == 'accessbilityid':
            locator = (MobileBy.ACCESSIBILITY_ID, value)
        elif type == 'predicate':
            locator = (MobileBy.IOS_PREDICATE, value)
        else:
            raise Exception(f'{type}不支持这种定位方式')
        return locator

    def click(self, ele_info):
        name = ele_info['name']
        timeout = ele_info['timeout']
        # element = self.find_element(ele_info)
        locator = self.getBy(ele_info)
        try:
            # element.click()
            wait = WebDriverWait(driver=self.driver, timeout=timeout)
            wait.until(element_click_success(locator))
            self.logger.info('点击【{}】成功'.format(name))
        except Exception as e:
            self.logger.error('点击【{}】发生了异常{}'.format(name, e))
            raise Exception('点击【{}】发生了异常{}'.format(name, e))

    def send_keys(self, ele_info, text):
        name = ele_info['name']
        element = self.find_element(ele_info)
        try:
            element.send_keys(text)
            self.logger.info('向【{}】输入【{}】成功'.format(name, text))
        except Exception as e:
            self.logger.error('向【{}】输入【{}】发生了异常{}'.format(name, text, e))
            raise Exception('向【{}】输入【{}】发生了异常{}'.format(name, text, e))

    def clear(self, ele_info):
        name = ele_info['name']
        element = self.find_element(ele_info)
        try:
            element.clear()
            self.logger.info('清除【{}】的内容成功'.format(name))
        except Exception as e:
            self.logger.error('清除【{}】的内容失败'.format(name))
            raise Exception('清除【{}】的内容失败'.format(name))
    # 鼠标悬浮

    def move_to_element(self, ele_info):
        element = self.find_element(ele_info)
        action = ActionChains(self.driver)
        action.move_to_element(element).release().perform()

    # window切换
    def switch_to_window(self, index=1):
        window_list = self.driver.window_handles
        self.driver.switch_to.window(window_list[index])
        self.logger.info('切换window成功')
    # 增加页面是否包含某段文字的方法

    def page_contains(self, text):
        # 在这里实现页面资源判断的自定义显式等待
        try:
            wait = WebDriverWait(driver=self.driver, timeout=5)
            wait.until(lambda x: text in x.page_source)
            self.logger.info('判断页面包含【{}】成功'.format(text))
            return True
        except Exception as e:
            self.logger.debug('判断页面包含【{}】失败:{}'.format(text, e))
            return False
    # 判断元素是否存在

    def is_element_exist(self, ele_info):
        try:
            self.find_element(ele_info)
            return True
        except BaseException:
            return False
    # 获取元素某个属性值的方法

    def get_attribute(self, ele_info, attr_name):
        element = self.find_element(ele_info)
        return element.get_attribute(attr_name)
    # 获取元素的文本内容

    def get_text(self, ele_info):
        element = self.find_element(ele_info)
        self.logger.info(
            '获取元素【{}】的文本是:{}'.format(
                ele_info['name'],
                element.text))
        return element.text

    def refresh(self):
        self.driver.refresh()
    # 封装一个截图方法，返回结果是二进制对象

    def get_screenshot_as_png(self):
        return self.driver.get_screenshot_as_png()

    def find_elements(self, ele_info):
        locator = self.getBy(ele_info)
        try:
            # element = self.driver.find_element(*locator)
            wait = WebDriverWait(self.driver, timeout=5)
            elements = wait.until(
                expected_conditions.presence_of_all_elements_located(locator))
            self.logger.info('查找【{}】元素成功'.format(ele_info))
        except Exception as e:
            self.logger.error('查找【{}】元素时5秒出现异常{}'.format(ele_info, e))
            raise Exception('查找【{}】元素时5秒出现异常{}'.format(ele_info, e))
        return elements
    # 截图方法，存储成文件

    def get_screenshot_as_file(self, filename):
        self.driver.get_screenshot_as_file(filename)
    # quit方法，断开session，关闭浏览器

    def quit(self):
        self.driver.quit()

    # 增加移动端也有的一些方法
    # 整屏滑动
    def swipe(self, direction: str, duration=500):
        time.sleep(1)
        x = self.driver.get_window_size()['width']
        y = self.driver.get_window_size()['height']
        if direction.lower() == 'up':
            self.driver.swipe(x / 2, 0.8 * y, x / 2, 0.2 * y, duration)
        elif direction.lower() == 'down':
            self.driver.swipe(x / 2, 0.2 * y, x / 2, 0.8 * y, duration)
        elif direction.lower() == 'left':
            self.driver.swipe(0.8 * x, y / 2, 0.2 * x, y / 2, duration)
        elif direction.lower() == 'right':
            self.driver.swipe(0.2 * x, y / 2, 0.8 * x, y / 2, duration)
        else:
            raise Exception('方向错误')

    # 元素上的滑动
    def swipe_on_element(self, ele_info, direction, duration=500):
        element = self.find_element(ele_info)
        start_x = element.location.get('x')  # 元素的起始点的x坐标
        start_y = element.location.get('y')  # 元素的起始点的y坐标
        w = element.size.get('width')  # 元素的宽
        h = element.size.get('height')  # 元素的高
        if direction.lower() == 'up':
            self.driver.swipe(
                start_x + w / 2,
                start_y + 0.8 * h,
                start_x + w / 2,
                start_y + 0.2 * h,
                duration)
        elif direction.lower() == 'down':
            self.driver.swipe(
                start_x + w / 2,
                start_y + 0.2 * h,
                start_x + w / 2,
                start_y + 0.8 * h,
                duration)
        elif direction.lower() == 'left':
            self.driver.swipe(
                start_x + 0.8 * w,
                start_y + h / 2,
                start_x + 0.2 * w,
                start_y + h / 2,
                duration)
        elif direction.lower() == 'right':
            self.driver.swipe(
                start_x + 0.2 * w,
                start_y + h / 2,
                start_x + 0.8 * w,
                start_y + h / 2,
                duration)
        else:
            raise Exception('方向错误')
    # 九宫格手势解锁

    def action_swipe(self, ele_info, pwd):
        element = self.find_element(ele_info)
        # lockPattern = driver.find_element(By.ID,'com.android.settings:id/lockPattern')
        start_x = element.location.get('x')  # 元素的起始点的x坐标
        start_y = element.location.get('y')  # 元素的起始点的y坐标
        w = element.size.get('width')  # 元素的宽
        h = element.size.get('height')  # 元素的高
        gesture_list = [
            {'x': start_x + w / 6, 'y': start_y + h / 6}, {'x': start_x + 3 * w / 6, 'y': start_y + h / 6},
            {'x': start_x + 5 * w / 6, 'y': start_y + h / 6},
            {'x': start_x + w / 6, 'y': start_y + 3 * h / 6}, {'x': start_x + 3 * w / 6, 'y': start_y + 3 * h / 6},
            {'x': start_x + 5 * w / 6, 'y': start_y + 3 * h / 6},
            {'x': start_x + w / 6, 'y': start_y + 5 * h / 6}, {'x': start_x + 3 * w / 6, 'y': start_y + 5 * h / 6},
            {'x': start_x + 5 * w / 6, 'y': start_y + 5 * h / 6}
        ]
        # pwd=0458723
        action = TouchAction(self.driver)
        action.press(x=gesture_list[int(pwd[0])].get(
            'x'), y=gesture_list[int(pwd[0])].get('y'))
        for i in range(1, len(pwd)):
            action.move_to(x=gesture_list[int(pwd[i])].get(
                'x'), y=gesture_list[int(pwd[i])].get('y'))
        action.release().perform()
    # 启动app，启动自己或者第三方app都可以

    def start_activity(self, app_package, app_activity):
        self.driver.start_activity(app_package, app_activity)
    # 清除app数据并且重新启动

    def reset_app(self):
        self.driver.reset()
    # 长按某元素

    def long_press(self, ele_info):
        element = self.find_element(ele_info)
        TouchAction(self.driver).long_press(el=element).release().perform()
    # 长按某坐标

    def long_press_cor(self, x, y):
        TouchAction(self.driver).long_press(x=x, y=y).release().perform()
    # 点手机上的返回键，只支持安卓

    def press_back(self):
        self.driver.press_keycode(AndroidKey.BACK)
    # 点击手机上的home键，只支持安卓

    def press_home(self):
        self.driver.press_keycode(AndroidKey.HOME)
        self.logger.info('点击手机Home键成功')


# def aa(driver):
#     return driver.page_source.contains('xxx')

# 自定义的一个点击直到成功的显式等待条件
class element_click_success(object):
    """ An Expectation for checking an element is visible and enabled such that
    you can click it."""

    def __init__(self, locator):
        self.locator = locator

    def __call__(self, driver):
        # 先定位元素,由于外部传入的locator是一个元组(By.CSS_SELECTOR,'.gl-item')，那么在这里使用*self.locator将其拆开
        element = driver.find_element(
            *self.locator)  # find_element(By.ID,'xxx')
        # 然后点击,做一个异常处理，如果有异常就返回False，等待下一次轮询执行
        try:
            element.click()
            return True
        except BaseException:
            # print('执行点击报错了，等待下一次轮询')
            return False
