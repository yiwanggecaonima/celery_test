import json
import re
import threading

from enheng import parse_urls
from redis import Redis
# import sys
# sys.stdout.detach()
from celery import app

r = Redis(host='47.107.137.63', port=6379, db=11,password='caonima',decode_responses=True)

def task_manager(url):
    string = str(datas, encoding="utf8")
    string = re.sub("\'", '\"', datas)
    print(string)
    data = json.loads(string)
    url = data['link']
    app.send_task('aqicn.crawl', args=(url[0],url[1],))


if __name__ == '__main__':
    # print (len(URLS))
    run()
