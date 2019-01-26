# -*- coding: utf-8 -*-
import json

from celery import Celery
import sys
import codecs
# sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
# import json
import random
import re
import time
import urllib.request
from urllib.error import URLError
import requests
import requests.adapters
from redis import Redis
from lxml import etree
import pymongo
import random
from multiprocessing import Pool
from requests.exceptions import ConnectionError,SSLError,Timeout
from requests.packages import urllib3
import socks
import ssl
import socket
from socket import error as SocketError
import errno
urllib3.disable_warnings()
socket.setdefaulttimeout(8)
requests.adapters.DEFAULT_RETRIES = 2
# requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS += 'HIGH:!DH:!aNULL'
# requests.packages.urllib3.contrib.pyopenssl.DEFAULT_SSL_CIPHER_LIST += 'HIGH:!DH:!aNULL'
PROXY_POOL_URL = 'http://webapi.http.zhimacangku.com/getip?num=1&type=1&pro=0&city=0&yys=0&port=1&pack=38903&ts=0&ys=0&cs=0&lb=1&sb=0&pb=45&mr=1&regions=370000,440000'
MAX_COUNT = 5
# socks.set_default_proxy(socks.SOCKS5, '127.0.0.1',1080)
# socket.socket = socks.socksocket
app = Celery('enheng',broker='redis://127.0.0.1:6379/8')

# r = Redis(host='47.107.137.63', port=6379, db=10,password='caonima',decode_responses=True)
# print(r.keys())
proxy =None
client = pymongo.MongoClient('127.0.0.1',27017)
db = client['scrapy_hc']
headers = {'User_Agent':  "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.7 (KHTML, like Gecko) Chrome/16.0.912.36 Safari/535.7",
           'Connection': 'close'}
@app.task
def get_proxy():
    try:
        request = urllib.request.Request("http://webapi.http.zhimacangku.com/getip?num=1&type=1&pro=0&city=0&yys=100017&port=11&pack=39397&ts=0&ys=0&cs=0&lb=1&sb=0&pb=45&mr=1&regions=140000,340000,350000,360000,430000,440000,500000", headers=headers)
        response = urllib.request.urlopen(request)
        data = response.read().decode()
        response.close()
        ip_port = data.strip("\r\n")
        print(ip_port)
        if '设置为白名单' in data:
            ret = re.compile(r'请将(.*)设置为白名单')
            ip = re.findall(ret, data)[0]
            print(ip, type(ip))
            white_ip = 'http://web.http.cnapi.cc/index/index/save_white?neek=60658&appkey=c76d3c1fddc89df92151a2cfb6388a5f&white=' + ip
            result = requests.get(white_ip, headers=headers)
            if '保存成功' in result.text:
                print('白名单保存成功')
                get_proxy()
        elif '您的套餐pack传参有误' in data:
            ret = re.compile(r'请检测您现在的(.*)是否在套餐')
            ip = re.findall(ret, data)[0]
            print(ip, type(ip))
            white_ip = 'http://web.http.cnapi.cc/index/index/save_white?neek=60658&appkey=c76d3c1fddc89df92151a2cfb6388a5f&white=' + ip
            result = requests.get(white_ip, headers=headers)
            if '保存成功' in result.text:
                print('白名单保存成功')
                get_proxy()
        return ip_port

    except URLError as e:
        print("wait ......")
        exit()
        # time.sleep(150)
        # get_proxy()
@app.task
def get_html(url,count=1):
    print('Crawling', url)
    global proxy
    if count > MAX_COUNT:
        print('已超最大重试次数')
        return None
    try:
        session = requests.session()
        session.keep_alive = False
        session.verify = False
        if proxy:
            # proxies = {
            #     'http': 'http://' + proxy
            #     # 'https': 'http://' + proxy
            # }
            ip = proxy.split(':')[0]
            port = proxy.split(':')[1]
            print(ip, port)
            socks.set_default_proxy(socks.PROXY_TYPE_HTTP, ip,int(port))
            socket.socket = socks.socksocket
            response = session.get(url, allow_redirects=False, headers=headers,timeout=5)
        else:
            response = session.get(url, allow_redirects=False, headers=headers,timeout=5)

        if response.status_code == 200:
            session.close()
            return response.text
        if response.status_code in [301, 302, 304, 401, 404, 410]:
            print('页面跳转')
            time.sleep(2)
            res = requests.get(response.url,allow_redirects=False,headers=headers,timeout=5)
            if res.status_code == 404:
                pass
            elif res.status_code != 200:
                proxy = get_proxy()
                if proxy:
                    print('重新获取代理ip',proxy)
                    count += 1
                    return get_html(response.url,count)
                else:
                    print('获取代理失败')
                    return None
            else:
                return res.text
        return None
    except SSLError as e:
        print('禁止访问', e.args)
        time.sleep(random.choice([3,4, 5, 7, 8]))
        proxy = get_proxy()
        # proxy = '127.0.0.1:1080'
        return get_html(url, count)
    except ConnectionError as e:
        print('Connection Error', e.args)
        time.sleep(random.choice([3, 2, 1]))
        proxy = get_proxy()
        count += 1
        return get_html(url, count)
    except Timeout as e:
        print('Timeout Error', e.args)
        res = requests.get(url, allow_redirects=False, headers=headers, timeout=5)
        if res.status_code != 200:
            proxy = get_proxy()
            if proxy:
                print('重新获取代理ip', proxy)
                count += 1
                return get_html(url, count)
            else:
                print('获取代理失败')
                return None
        else:
            return res.text

    except SocketError as e:
        if e.errno != errno.ECONNRESET:
            raise
        time.sleep(3)
        # print('Socks Error', e.args)
        # time.sleep(random.choice([4,5,6,7,8,9,10]))
        proxy = get_proxy()
        return get_html(url, count)
    except Exception as e:
        print('xxxxxxx',e)
        time.sleep(2)
        proxy = get_proxy()
        return get_html(url, count)
@app.task
def insert_json(value):
    file = codecs.open("仪器仪表item.json", "a", encoding="utf-8")
    line = json.dumps(value, ensure_ascii=False) + "," + "\n"
    file.write(line)
    file.close()
@app.task
def insert_mongo(item):
    # if db['hc_item_家居家电'].update({'name':item['name']},{'$set': item},True):
    if db['音响灯光'].insert(dict(item)):
        print('save to mongo ',item['name'])
    else:
        print(('No to mongo'))

@app.task
def parse_urls(data):

    while True:
        try:
            result = get_html(data['link'])
            response = etree.HTML(result)
            item = {}
            item['link'] = data['link']
            item['tag'] = data['tag']
            area = response.xpath("//div[@class='proInfoAlert']/ul/li[3]/text()")
            new_area = response.xpath("//div[@class='view-con-l']/ul/li[2]/span/text()")
            if area:
                item['city'] = ''.join(''.join(area).strip('\r\n').strip('\t\r\n  ').split('\xa0'))
            elif new_area:
                item['city'] = new_area[-1]
            else:
                item['city'] = None
            fa = response.xpath("//div[@class='word1 part1']/div[@class='p name']/em/text()")
            item['contacts'] = fa[0].strip('：').split('\xa0')[0] if fa else None
            name = response.xpath("//div[@class='word1 part1']/div[@class='p sate']/em/text()")
            item['name'] = name[0].strip('：') if name else None
            tel2 = response.xpath("//div[@class='word1 part1']/div[@class='p tel2']/em/text()")
            item['tel2'] = tel2[0].strip('：') if tel2 else None
            tel1 = response.xpath("//div[@class='word1 part1']/div[@class='p tel1']/em/text()")
            item['tel1'] = tel1[0].strip('：').strip(' \xa0\xa0  ') if tel1 else None
            print(item)
            # insert_json(item)
            insert_mongo(dict(item))
            # time.sleep(random.choice([0.5,0.6,0.7,0.8,0.9,1]))

        except ValueError as e:
            print("xpath结果为空！",e.args)
            pass

        except Exception as e:
            if "j_urls" not in r.keys():
                print("爬取结束,关闭爬虫！")
                break
            else:
                print("请求发送失败",e)
                # raise
                continue
    else:
        parse_urls()


if __name__ == '__main__':
    parse_urls()