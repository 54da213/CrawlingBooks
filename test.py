# -*- coding: utf-8 -*-

import redis
import json
import os
import requests
from bs4 import BeautifulSoup
from utils import IO
from selenium import webdriver
from selenium.webdriver.firefox.options import Options



def app():
    '''
    项目实验使用
    :return:
    '''

    url="https://www.baidu.com"
    options=Options()
    options.add_argument('-headless')
    driver = webdriver.Firefox(firefox_options=options)
    driver.get(url)
    driver.save_screenshot("baidu.png")

if __name__ == '__main__':
    app()