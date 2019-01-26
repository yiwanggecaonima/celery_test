from celery import Celery
import requests
from lxml import etree
import pymongo
app = Celery('tasks', broker='redis://localhost:6379/2')
client = pymongo.MongoClient('localhost',27017)
db = client['baike']
@app.task
def get_url(link):
    item = {}
    headers = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.131 Safari/537.36'}
    res = requests.get(link,headers=headers)
    res.encoding = 'UTF-8'
    doc = etree.HTML(res.text)
    content = doc.xpath("//div[@class='lemma-summary']/div[@class='para']//text()")
    print(res.status_code)
    print(link,'\t','++++++++++++++++++++')
    item['link'] = link
    data = ''.join(content).replace(' ', '').replace('\t', '').replace('\n', '').replace('\r', '')
    item['data'] = data
    if db['Baike'].insert(dict(item)):
        print("is OK ...")
    else:
        print('No Mongo')

