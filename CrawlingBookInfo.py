# -*- coding: utf-8 -*-
import re
import threading

import requests
from bs4 import BeautifulSoup

from utils import R


class WebCrawler(object):

    def __init__(self, url):
        print "-----------------init...---------------------"
        self.url = url
        r = requests.get(self.url)
        if r.status_code != 200:
            raise RuntimeError("init err")

        soup = BeautifulSoup(r.text, "html5lib")
        self.total = soup.select("strong")[2].string

    # 分布式 获取图书列表进入redis
    def get_book_list(self, page):
        url = "https://www.4wens.com/6/{0}.html".format(page)
        r = requests.get(url)
        if r.status_code != 200:
            raise RuntimeError("Request exception")
        soup = BeautifulSoup(r.text, "html5lib")
        # 第二页开始数据所在标签发生变化
        if page == 1:
            als = soup.select("div[class='update'] table tbody td[class='book-name'] a[target='_blank']")
        else:
            als = self.__get_als(soup)
        a_it = iter(als)
        # print "page:{0} als".format(str(als))
        for a in a_it:
            href = a["href"]
            book_num = re.findall("\d{5,6}", href)[0]
            book_name = a.string
            book_info = (book_num, (href, book_name))
            rdb = R()
            try:
                rdb.in_book_info(book_info)
            except Exception as e:
                raise RuntimeError("Redis err:{0}".format(e.message))
        print "{0} in Redis success".format(page)

    def __get_als(self, soup):
        als = []
        div = soup.select("div[class='row index-box'] div[class='col xs-6 text-hide']")
        for row in div:
            a = row.select("a")
            if not a:
                continue
            als.append(a[0])
        return als


def app():
    url = "https://www.4wens.com/6/"
    wc = WebCrawler(url)
    total = 1
    try:
        total = int(wc.total)
    except Exception as e:
        print "Err get total:{0}".format(e.message)

    for page in xrange(1, total + 1):
        t = threading.Thread(target=wc.get_book_list, args=(page,))
        t.daemon=False
        t.start()


if __name__ == '__main__':
    app()
