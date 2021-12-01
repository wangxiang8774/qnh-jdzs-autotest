# !/usr/bin python3
# encoding: utf-8 -*-
# @author: 王翔
# @Time: 2021/11/5 19:10
import pandas
import yaml

from setting import DIR_NAME


def load_yaml_file(yaml_file):
    """
    读取yaml文件内容
    :param yaml_file: yaml文件的路径
    :return:
    """
    with open(DIR_NAME + yaml_file, 'r', encoding='UTF-8') as stream:

        yaml_content = yaml.load(stream, Loader=yaml.FullLoader)

        return yaml_content


def read_excel(file_path, sheet_name):
    # keep_default_na参数表示读取excel时，如果碰到空单元格时返回什么？如果为True则返回nan，如果为False那么返回的是空字符串
    # 默认读取时就不包括表头
    res = pandas.read_excel(
        DIR_NAME + file_path,
        sheet_name=sheet_name,
        keep_default_na=False,
        engine='openpyxl')
    # 因为httprunner要求的参数化数据格式是列表套列表，因此我们要将读到的excel数据进行转换
    # [[1,2,3],[1,2,3],[1,2,3]]
    lines_count = res.shape[0]  # 获取数据总行数
    col_count = res.columns.size  # 获取列数
    data = []
    for l in range(lines_count):  # 遍历行
        line = []
        for c in range(col_count):  # 遍历列
            text = res.iloc[l, c]  # 行和列组合交叉定位到一个单元格
            line.append(text)
        data.append(line)
    return data


if __name__ == '__main__':
    # yaml_content = load_yaml_file('/pagefiles/buyer.yml')
    # homepage = yaml_content.get('HomePage')
    # print(homepage)
    # print(homepage.get('登录链接'))

    print(read_excel('/data/mtxshop.xlsx', '添加地址'))
