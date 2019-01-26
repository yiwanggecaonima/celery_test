# celery_test

一个测试celery这个玩意的小脚本，celery的官称是分布式队列，那就试试到底是如何工作的吧
首先感谢这篇文章的博主　https://blog.csdn.net/suwenkun1126/article/details/78355953　　深度优先的简单例子
所谓的深度优先，就是你要爬取网站的深度，这个一般都是以实际情况来定义的
深度优先容易实现的地方是可以用递归来写，只要定义好阀值，写好逻辑判断等等

urls.py  是爬取url列表的文件，一个简易的深度优先的实现，带有简单的去重，url集合保存在url.txt文件里,应该有好几百万条吧
haha.py  是简单的解析文件，简简单单抓了一些简介，存在了mongodb
run_haha　就是celery调度的主文件了，中间人选用的是redis，呵呵，因为简单，也可以用官方推荐的MQ队列
这里并没有用到自定义的配置文件，消费队列，以及一些定时爬取，监控爬取，这只是个小测试
只用了10个线程　　命令　　celery -A haha worker -l info -P gevent -c 10　
gevent可以自己指定　　比如更为thread 等等



