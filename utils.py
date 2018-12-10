# -*- coding: utf-8 -*-
import json
import os

import redis

class R(object):
    def __init__(self):
        self.r=redis.Redis(host='127.0.0.1', port=6379, db=0)

    def in_book_info(self, book_info):
        self.r.hset("bookshelf", book_info[0], json.dumps(book_info[1]))

    def out_book_info(self,key):
        return self.r.hget("bookshelf",key)

    def keys(self):
        return self.r.keys()

class IO(object):
    def __init__(self):
        self.path = os.path.abspath(__file__)
        self.dir = os.path.dirname(self.path)

    def write(self,text_list,book_name,topic):
        book_dir="{0}/{1}/{2}".format(os.path.dirname(self.dir),"books",book_name.encode("utf-8"))
        if not os.path.exists(book_dir):
            os.makedirs(book_dir)

        path="{0}/{1}.txt".format(book_dir,"{0}".format(topic))
        with open(path,'w') as f:
            f.writelines(text_list)

