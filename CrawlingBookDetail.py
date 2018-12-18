# -*- coding: utf-8 -*-

import json
import re
import time
import threading
import logging

import requests
from bs4 import BeautifulSoup

from utils import R, IO, dr

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    filename="web_crawler_log.log")


class WebCrawler(object):
    def init_page(self, url, prefix):
        '''
        初始化 获取总章节 开始章节url等信息
        :param url:
        :param prefix:
        :return:
        '''
        chapter_start_url, total_zhangjie = None, None
        r = requests.get(url)
        if r.status_code != 200:
            return chapter_start_url, total_zhangjie
        soup = BeautifulSoup(r.text, "html5lib")
        href = soup.select("a[class='submit-button-red']")[0]["href"]
        chapter_start_url = "{0}{1}".format(prefix, href)
        total_zhangjie = re.findall("\d{2,4}", soup.select("div[class='panel-name']")[0].get_text())[0]
        return chapter_start_url, total_zhangjie

    def __get_text(self, chapter_start_url, book_name, topic):
        '''
        小说正文爬取并写入磁盘
        :param chapter_start_url:
        :param book_name:
        :param topic:
        :return:
        '''
        # 文章正文部分是js 用selenium模拟浏览器获取html页面
        driver = dr()
        driver.get(chapter_start_url)
        # 网络时整个页面没有加载外全会导致抓取内容错误
        # 直接调用sheep对整个线程不安全 故采用 ▲t1-▲t2的方式拖延程序
        start_time = int(time.time())
        while True:
            end_time = int(time.time())
            if end_time - start_time >= 1:
                break
        soup = BeautifulSoup(driver.page_source, "html5lib")
        ps = soup.select("#chapter-content p")
        text_list = ["{0}\n".format(p.string.encode("utf-8")) for p in ps if p.string]
        driver.quit()
        io = IO()
        io.write(text_list, book_name, topic)
        logging.info("--------------------{0}{1} ..下载完成--------------------".format(book_name.encode("utf-8"), topic))

    def __get_chapter(self, chapter_start_url, book_name, total_zhangjie):
        '''
        逐章爬取
        :param chapter_start_url:
        :param book_name:
        :param total_zhangjie:
        :return:
        '''
        urls = chapter_start_url.split('/')
        url = "https://{0}".format('/'.join(urls[2:-1]))
        threads = []
        for i in xrange(1, total_zhangjie):
            topic = "第{0}章".format(i)
            chapter_url = "{0}/{1}.html".format(url, i)
            t = threading.Thread(target=self.__get_text, args=(chapter_url, book_name, topic))
            threads.append(t)
        for t in threads:
            t.daemon = False
            t.start()
            while True:
                if (len(threading.enumerate()) < 10):
                    break

    def download_book(self, chapter_start_url, book_name, total_zhangjie):
        total_zhangjie = total_zhangjie + 1
        self.__get_chapter(chapter_start_url, book_name, total_zhangjie)


def app():
    '''
    业务函数
    数据采集由另一脚本爬取完成并存入redis
    :return:
    '''
    r = R()
    keys_it = iter(r.r.hkeys("bookshelf")[0:2])
    prefix = "https://www.4wens.com"
    for key in keys_it:
        book_info = json.loads(r.r.hget("bookshelf", key))
        uri = book_info[0]
        book_name = book_info[1]
        logging.info("{0} init...".format(book_name.encode("utf-8")))
        url = "{0}{1}".format(prefix, uri)
        wc = WebCrawler()
        # 获取每本书第一章节url
        chapter_start_url, total_zhangjie = wc.init_page(url, prefix)
        if not (chapter_start_url and total_zhangjie):
            logging.warning("{0}------>init..失败".format(book_name))
            continue
        logging.info("{0} init 完成 download..".format(book_name.encode("utf-8")))
        wc.download_book(chapter_start_url, book_name, int(total_zhangjie))
        logging.info("--------------------{0}-----------------下载完成..".format(book_name.encode("utf-8")))
        r.r.hdel("bookshelf", key)


if __name__ == '__main__':
    app()
