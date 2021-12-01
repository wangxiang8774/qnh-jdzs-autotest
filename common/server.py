# !/usr/bin python3
# encoding: utf-8 -*-
# @author: 王翔
# @Time: 2021/11/5 19:10
import os
import platform
import subprocess

from setting import DIR_NAME


class AppiumServer:

    # appium服务启动
    def start(self, port=4723, chromedriver_port=8000):
        # 模拟命令行动作
        appium_log_file = DIR_NAME + f'/logs/appium{port}.log'
        command = f'appium -p {port} --chromedriver-port {chromedriver_port} -g {appium_log_file}'
        # 调用命令行执行操作
        subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True).communicate()
    # 停止服务

    def stop(self, port=4723):
        # 先查询对应端口占用的进程号，然后再杀死该进程，那么服务就停掉了
        system_name = platform.system()  # 获取系统名称
        if system_name.lower() == 'windows':
            res = os.popen(f'netstat -ano|findstr {port}')
            res_str = res.read().strip()  # 读取结果转换成字符串
            if 'LISTENING' in res_str:
                all_line = res_str.split('\n')
                for line in all_line:
                    # TCP    0.0.0.0:4723           0.0.0.0:0
                    # LISTENING       9048
                    if 'LISTENING' in line:
                        process_id = line.split('LISTENING')[1].strip()
                        os.popen(f'taskkill -f -pid {process_id}')
        else:
            # 按照mac的方式去执行
            res = os.popen('lsof -i:{}'.format(port))
            res_str = res.read().strip()
            # print(res_str)
            if res_str != '' and 'LISTEN' in res_str:
                all_line = res_str.split('\n')
                for line in all_line:
                    print(line)
                    if 'LISTEN' in line:
                        process_id = res_str.split('LISTEN')[1].strip()[0:5]
                        break
                os.popen('kill {}'.format(process_id))


if __name__ == '__main__':
    AppiumServer().start()
