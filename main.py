# 主进程
import random
import pandas as pd
import time
import ssl
import requests
import urllib3
from lxml import etree
import threading

def threadingFunction(thr, flag):
    # 线程函数
    try:
        thr.run()
        print("[{}]".format(time.strftime("%H:%M:%S", time.localtime())) + "[INFO]Threading {} finished.".format(thr.id))
        flag[thr.id] = 1
    except Exception as e:
        # 异常处理
        text = "[{}]".format(time.strftime("%H:%M:%S", time.localtime())) + "[ERROR]" + e.__str__()
        print(text)
        with open("./log/threadingErrorLog.txt", 'a', encoding='utf8') as logFile:
            logFile.write(text + '\n')


class thread:
    def __init__(self, id):
        self.id = id
        self.urlList = self.readURL()
        print("[{}]".format(time.strftime("%H:%M:%S", time.localtime())) + "[INFO]Threading {} gets started.".format(self.id))

    def readURL(self):
        # 读取该线程需要爬取的url
        path = "./res/url{}.txt".format(self.id)
        urlList = []
        with open(path, 'r', encoding='utf8') as urlFile:
            for line in urlFile:
                line = line.replace("\n", "")
                if line == "":
                    pass
                urlList.append(line)
            return urlList

    def run(self):
        # 遍历需要爬取的url, 依次爬取并存入文件
        n = 1
        Length = len(self.urlList)
        for str in self.urlList:
            if n % 50 == 0:
                # 进度提示
                print("[{}]".format(time.strftime("%H:%M:%S", time.localtime())) + "[INFO]Threading {} finished {}/{} urls.".format(self.id, n, Length))
            urlObject = URL(str, self.id)
            try:
                urlObject.get()
            except Exception as e:
                # 异常处理
                text = "[{}]".format(time.strftime("%H:%M:%S", time.localtime())) + "[WARNING]" + e.__str__()
                print(text)
                with open("./log/networkErrorLog.txt", 'a', encoding='utf8') as logFile:
                    logFile.write(text + '\n')
            urlObject.write()
            n = n + 1

class URL:
    def __init__(self, url, id):
        self.url = url
        self.len = 0
        self.title = "0"
        self.IsOK = 0
        self.state = 404
        my_headers = [
            "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.153 Safari/537.36",
            "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:30.0) Gecko/20100101 Firefox/30.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.75.14 (KHTML, like Gecko) Version/7.0.3 Safari/537.75.14",
            "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; Win64; x64; Trident/6.0)",
            'Mozilla/5.0 (Windows; U; Windows NT 5.1; it; rv:1.8.1.11) Gecko/20071127 Firefox/2.0.0.11',
            'Opera/9.25 (Windows NT 5.1; U; en)',
            'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)',
            'Mozilla/5.0 (compatible; Konqueror/3.5; Linux) KHTML/3.5.5 (like Gecko) (Kubuntu)',
            'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.0.12) Gecko/20070731 Ubuntu/dapper-security Firefox/1.5.0.12',
            'Lynx/2.8.5rel.1 libwww-FM/2.14 SSL-MM/1.4.1 GNUTLS/1.2.9',
            "Mozilla/5.0 (X11; Linux i686) AppleWebKit/535.7 (KHTML, like Gecko) Ubuntu/11.04 Chromium/16.0.912.77 Chrome/16.0.912.77 Safari/535.7",
            "Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:10.0) Gecko/20100101 Firefox/10.0 ",
            "Mozilla/5.0(WindowsNT6.1;rv:2.0.1)Gecko/20100101Firefox/4.0.1"
        ]
        ref = self.url.split('/')
        refURL = ref[0] + "//" + ref[2]
        self.headers = {
            'User-Agent': random.choice(my_headers),
            'Connection': 'close',
            "Referer": refURL,
            'X-Requested-With': 'XMLHttpRequest',
        }
        self.id = id
        ssl._create_default_https_context = ssl._create_unverified_context

    def get(self):
        # 对指定的url进行爬取
        self.len = len(self.url)
        requests.adapters.DEFAULT_RETRIES = 5
        s = requests.session()
        s.keep_alive = False
        time.sleep(3)
        res = requests.get(self.url, headers=self.headers, timeout=10, verify=False)
        html = etree.HTML(res.text)
        try:
            self.title = html.xpath('//title/text()')[0]
        except Exception:
            self.title = ""
        self.state = res.status_code
        if self.state == 200:
            self.IsOK = 1
            print("[{}]".format(time.strftime("%H:%M:%S", time.localtime())) + "[INFO]Successfully!({})".format(self.url))
            # 正常工作, 写入日志
            with open("./log/runningLog/log{}.txt".format(self.id), "a") as log:
                log.write(self.url + '\n')

    def write(self):
        # 将爬取的信息写入文件中
        writeCSV(self.url, self.IsOK, self.len, self.title, self.state, self.id)

def writeCSV(url, IsOK, len, title, state, num):
    # 将一个线程的结果写入临时的csv文件
    data = {
        'URL': [url],
        '能否访问': [IsOK],
        'URL长度': [len],
        '网页标题': [title],
        '响应状态码': [state],
    }
    dataFrame = pd.DataFrame(data)
    path = "./csvResult/result{}.csv".format(num)
    dataFrame.to_csv(path, mode='a', header=False)

def main():
    # 主进程
    n = 0
    flag = [0] * 50
    for i in range(50):
        t = threading.Thread(target=threadingFunction, args=(thread(i), flag))
        t.start()
        # 防止炸内存
        if n % 3 == 0:
            time.sleep(10)
        elif n % 3 == 1:
            time.sleep(40)
        else:
            time.sleep(20)
        n = n + 1
    while True:
        # 每3分钟输出一下进度
        time.sleep(180)
        s = sum(flag)
        print("[{}]".format(time.strftime("%H:%M:%S", time.localtime())) + "[INFO]There are {} threadings has been done".format(s))
        if s == 50:
            break
    print("[{}]".format(time.strftime("%H:%M:%S", time.localtime())) + "[INFO]DONE!")

if __name__ == '__main__':
    urllib3.disable_warnings()
    main()

