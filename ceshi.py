

from lxml import etree
import requests

headers = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.131 Safari/537.36'}
res = requests.get("https://baike.baidu.com/item/%E9%98%B5%E5%9C%B0",headers=headers)
res.encoding = 'UTF-8'
doc = etree.HTML(res.text)
content = doc.xpath("//div[@class='lemma-summary']/div[@class='para']//text()")
print(''.join(content).replace(' ','').replace('\t','').replace('\n','').replace('\r',''))
