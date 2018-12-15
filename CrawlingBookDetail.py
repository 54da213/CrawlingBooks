# -*- coding: utf-8 -*-

import json
import re
import time

import requests
from bs4 import BeautifulSoup
from selenium import webdriver

from utils import R, IO


class WebCrawler(object):
    def init_page(self, url, prefix):
        chapter_start_url, total_zhangjie = None, None
        r = requests.get(url)
        if r.status_code != 200:
            return chapter_start_url, total_zhangjie
        soup = BeautifulSoup(r.text, "html5lib")
        href = soup.select("a[class='submit-button-red']")[0]["href"]
        chapter_start_url = "{0}{1}".format(prefix, href)
        total_zhangjie = re.findall("\d{2,4}", soup.select("div[class='panel-name']")[0].get_text())[0]
        return chapter_start_url, total_zhangjie

    def __get_text(self, chapter_start_url):
        #文章正文部分是js 用selenium模拟浏览器获取html页面
        try:
            firefox=webdriver.Firefox()
            firefox.get(chapter_start_url)
        except Exception as e:
            return [], None
        #网络时整个页面没有加载外全会导致抓取内容错误
        #直接调用sheep对整个线程不安全 故采用 ▲t1-▲t2的方式拖延程序
        start_time=int(time.time())
        while True:
            end_time=int(time.time())
            if end_time-start_time>=1:
                break
        #弃用此方案
        #r = requests.get(chapter_start_url)
        # if r.status_code != 200:
        #     return [], None
        soup = BeautifulSoup(firefox.page_source, "html5lib")
        ps = soup.select("#chapter-content p")
        chapter_next_url = soup.select("div[class='pages'] a[class='next']")[0]["href"]
        text_list = ["{0}\n".format(p.string.encode("utf-8")) for p in ps if p.string]
        firefox.quit()
        return text_list, chapter_next_url

    def book(self, chapter_start_url, book_name, total_zhangjie, prefix):
        total_zhangjie = total_zhangjie + 1
        chapter = ""
        for i in xrange(1,total_zhangjie):
            if i == 1:
                print chapter_start_url
                text_list, chapter = self.__get_text(chapter_start_url)
            else:
                chapter_url = "{0}{1}".format(prefix, chapter)
                print chapter_url
                text_list, chapter = self.__get_text(chapter_url)
            topic = "第{0}章".format(i)
            if not (text_list and chapter):
                print ("--------------------{0}{1} re failure".format(book_name.encode("utf-8"), topic))
                continue
            io = IO()
            io.write(text_list, book_name, topic)
            print ("--------------------{0}{1} ..下载完成".format(book_name.encode("utf-8"), topic))


def app():
    r = R()
    keys_it = iter(r.r.hkeys("bookshelf")[0:1])
    prefix = "https://www.4wens.com"
    for key in keys_it:
        book_info = json.loads(r.r.hget("bookshelf", key))
        uri = book_info[0]
        book_name = book_info[1]
        print "{0} init...".format(book_name.encode("utf-8"))
        url = "{0}{1}".format(prefix, uri)
        wc = WebCrawler()
        # 获取每本书第一章节url
        chapter_start_url, total_zhangjie = wc.init_page(url, prefix)
        if not (chapter_start_url and total_zhangjie):
            print "{0}------>init..失败".format(book_name)
            continue
        print "{0} init 完成 download..".format(book_name.encode("utf-8"))
        wc.book(chapter_start_url, book_name, int(total_zhangjie), prefix)
        print "--------------------{0}-----------------下载完成".format(book_name.encode("utf-8"))


if __name__ == '__main__':
    app()
