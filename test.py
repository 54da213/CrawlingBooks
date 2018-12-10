# -*- coding: utf-8 -*-

import redis
import json
import os
import requests
from bs4 import BeautifulSoup
from utils import IO

def bar(i):
    #是一个规则
    return i%2==0


def app():
    ls = xrange(0, 100)
    #生成器推导
    foo=(i for i in ls if bar(i))

    #for i in foo:print i

    for i in foo:
        if i == 11:
          break
    else:
        print ("------>开关关闭")

    # url="https://www.4wens.com/book/6/101585/1.html"
    # headers = {
    #     'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6',}
    # r=requests.get(url,headers=headers)
    # soup = BeautifulSoup(r.text, "html5lib")
    # print r.text
    # ps = soup.select("p")
    # print ps[0].string
    # for p in ps:
    #     print p.text
    # io=IO()
    # book_dir="{0}/{1}/{2}".format(os.path.dirname(io.dir),"books","乱伦我的母亲")
    # if not os.path.exists(book_dir):
    #     os.makedirs(book_dir)
    #
    # path="{0}/{1}".format(book_dir,"第一章")
    # print path
    # text_list=["锄禾日当午\n","汗滴禾下土\n","谁之盘中餐\n","粒粒皆辛苦\n"]
    # with open(path, 'w') as f:
    #     f.writelines(text_list)
    # r=redis.Redis(host='127.0.0.1', port=6379, db=0)
    # keys = r.hkeys("bookshelf")
    # # print (len(keys))
    # for k in keys:
    #     print json.loads(r.hget("bookshelf", k))[1]
    #r.hdel("bookshelf","108801")
    # r.hset("h1","Liu",100)

if __name__ == '__main__':
    app()