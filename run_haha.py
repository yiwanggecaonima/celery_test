from haha import get_url
from urls import url_list

def main(url):
    result = get_url.delay(url)
    return result

def run():
    with open('./url.txt', 'r') as f:
        for url in f.readlines():
            main(url.strip('\n'))

if __name__ == '__main__':
    run()