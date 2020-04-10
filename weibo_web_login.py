import requests
import urllib
import base64
import time
import re
import json
import rsa
import binascii
from bs4 import BeautifulSoup
header = {
    "User_Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:67.0) Gecko/20100101 Firefox/67.0",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "zh-CN, zh; q=0.8, zh=TW; q=0.7, zh=HK; q=0.5, en=US; q=0.3, en; q=0.2",
    "Accept": "text/html, application/xhtml+xml, application/xml; q=0.9, */*; q=0.8",
    "Referer": "https://weibo.com/?sudaref=www.baidu.com&display=0&retcode=6102",
    "Connection": "keep-alive"
}
class Login:
    session = requests.session()
    user_name="tianshi@terpmail.umd.edu"
    pass_word="Sts660410"
    def __init__(self,user_name,pass_word):
        self.user_name=user_name
        self.pass_word=pass_word
    def get_username(self):

        #print(urllib.parse.quote(self.user_name))
        return base64.b64encode(urllib.parse.quote(self.user_name).encode("utf-8")).decode("utf-8")

    def get_pre_login(self):
        #int(time..time()*1000)
        params = {
            "entry":  "weibo",
            "callback": "sinaSSOCcontroller.preloginCallBack",
            "su": self.get_username(),
            "rsakt": "mod",
            "checkpin":  "1",
            "client":  "ssologin.js(v1.4.19)",
            "_": int(time.time()*1000)
        }
        try:
            response = self.session.post("https://login.sina.com.cn/sso/prelogin.php", params = params, headers=header, verify=False)
            return json.loads(re.search(r"\((?P<data>.*)\)", response.text).group("data"))
        except:
            print("获取公钥失败")
            return 0

    def get_password(self):
        #print(get_pre_login()["servertime"])
        public_key = rsa.PublicKey(int(self.get_pre_login()["pubkey"],16), int("10001",16))
        password_string=str(self.get_pre_login()["servertime"])+'\t' +str(self.get_pre_login()["nonce"])+'\n'+self.pass_word
        return binascii.b2a_hex(rsa.encrypt(password_string.encode("utf-8"), public_key)).decode("utf-8")

    def login(self):
        post_data={
            "entry": "weibo",
            "gateway": "1",
            "from": "",
            "savestate": "7",
            "qrcode_flag": "false",
            "useticket": "1",
            "vsnf": "1",
            "su": self.get_username(),
            "service": "miniblog",
            "servertime": self.get_pre_login()["servertime"],
            "nonce": self.get_pre_login()["nonce"],
            "pwencode":"rsa2",
            "rsakv": self.get_pre_login()["rsakv"],
            "sp": self.get_password(),
            "sr": "1536*864",
            "encoding": "UTF-8",
            "prelt": "18",
            "url": "https://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.sinaSSOController.feedBackUrlCallBack",
            "returntype": "TEXT"
        }
        login_data=self.session.post("https://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.19)",data=post_data,headers=header,verify=False)

        params={
            "ticket": login_data.json()["ticket"] ,
            "ssosavestate": int(time.time()) ,
            "callback":"sinaSSOController.doCrossDomainCallBack",
            "scriptID":"ssoscript0",
            "client": "ssologin.js(v1.4.19)",
            "_": int(time.time()*1000)
        }

        self.session.post("https://passport.weibo.com/wbsso/login",params=params,verify=False,headers=header)
        return self.session

user_name="tianshi@terpmail.umd.edu"
pass_word="Sts660410"
login=Login(user_name,pass_word)

session=login.login()
response=session.post("https://weibo.com",verify=False,headers=header)
soup=BeautifulSoup(response.text,"html.parser")
print(soup.find("title"))

'''
import os
from lxml import etree
class CollectData():
    def __init__(self, keyword, startTime, interval='50', flag=True,
                 begin_url_per="http://s.weibo.com/weibo?q="):
        self.begin_url_per = begin_url_per
        self.setKeyword(keyword)
        self.setStartTimescope(startTime)
        self.setRegion(region)
        self.setSave_dir(savedir)
        self.setInterval(interval)
        self.setFlag(flag)
        self.logger = logging.getLogger('main.CollectData')

    def setKeyword(self, keyword):
        self.keyword = keyword


    def setStartTimescope(self, startTime):
        if not (startTime == '-'):
            self.timescope = startTime + ":" + startTime
        else:
            self.timescope = '-'

    def setRegion(self, region):
        self.region = region

    def setSave_dir(self, save_dir):
        self.save_dir = save_dir
        if not os.path.exists(self.save_dir):
            os.mkdir(self.save_dir)

    def setInterval(self, interval):
        self.interval = int(interval)

    def getKeyWord(self):
       return base64.b64encode(urllib.parse.quote(self.user_name).encode("utf-8")).decode("utf-8")

    def setFlag(self, flag):
        self.flag = flag

    #https://s.weibo.com/weibo?q=%E6%AD%A6%E6%B1%89%E8%82%BA%E7%82%8E&region=custom:11:2&atten=1&hasvideo=1&timescope=custom:2020-01-01-0:2020-01-10-1&Refer=g
    #https://s.weibo.com/weibo?q=%E6%AD%A6%E6%B1%89%E8%82%BA%E7%82%8E&typeall=1&suball=1&timescope=custom:2020-01-01-0:2020-01-10-1&&page=
    #关键词:武汉肺炎 ; 类型： 关注人； 包含：含视频； 时间：2020-01-01 0时 至 2020-01-10 1时； 地点：北京 西城区
    # 不需要选择地点时，url中没有"&region=custom:11:2"，类型：全部 &typeall=1; 包含：全部 &suball=1    def getURL(self):
        return self.begin_url_per + self.getKeyWord() + "&typeall=1&suball=1" + "&timescope=custom:" + self.timescope + "&nodup=1&page="


    def download(self, url, maxTryNum=4):
        content = open(self.save_dir + os.sep + "weibo_ids.txt", "ab")
        hasMore = True
        isCaught = False
        mid_filter = set([])
        i = 1
        while hasMore and i < 51 and (not isCaught):
            source_url = url + str(i)  # 构建某页的URL
            data = ''  # 存储该页的网页数据
            goon = True  # 网络中断标记
            ##网络不好的情况，试着尝试请求三次
            for tryNum in range(maxTryNum):
                try:
                    html = urllib2.urlopen(source_url, timeout=12)
                    data = html.read()
                    break
                except:
                    if tryNum < (maxTryNum - 1):
                        time.sleep(10)
                    else:
                        print
                        'Internet Connect Error!'
                        self.logger.error('Internet Connect Error!')
                        self.logger.info('filePath: ' + savedir)
                        self.logger.info('url: ' + source_url)
                        self.logger.info('fileNum: ' + str(fileNum))
                        self.logger.info('page: ' + str(i))
                        self.flag = False
                        goon = False
                        break
            if goon:
                lines = data.splitlines()
                isCaught = True
                for line in lines:
                    ## 判断是否有微博内容，出现这一行，则说明没有被认为是机器人
                    if line.startswith('<script>STK && STK.pageletM && STK.pageletM.view({"pid":"pl_weibo_direct"'):
                        isCaught = False
                        n = line.find('html":"')
                        if n > 0:
                            j = line[n + 7: -12].encode("utf-8").decode('unicode_escape').encode("utf-8").replace("\\",
                                                                                                                  "")
                            ## 没有更多结果页面
                            if (j.find('<div class="search_noresult">') > 0):
                                hasMore = False
                                ## 有结果的页面
                            else:
                                page = etree.HTML(j)
                                dls = page.xpath(u"//dl")  # 使用xpath解析
                                for dl in dls:
                                    mid = str(dl.attrib.get('mid'))
                                    if (mid != 'None' and mid not in mid_filter):
                                        mid_filter.add(mid)
                                        content.write(mid)
                                        content.write('\n')
                        break
                lines = None
                ## 处理被认为是机器人的情况
                if isCaught:
                    print
                    'Be Caught!'
                    self.logger.error('Be Caught Error!')
                    self.logger.info('filePath: ' + savedir)
                    self.logger.info('url: ' + source_url)
                    self.logger.info('fileNum: ' + str(fileNum))
                    self.logger.info('page:' + str(i))
                    data = None
                    self.flag = False
                    break
                    ## 没有更多结果，结束该次请求，跳到下一个请求
                if not hasMore:
                    print
                    'No More Results!'
                    if i == 1:
                        time.sleep(random.randint(55, 75))
                    else:
                        time.sleep(15)
                    data = None
                    break
                i += 1
                ## 设置两个邻近URL请求之间的随机休眠时间，你懂的。目前没有模拟登陆
                sleeptime_one = random.randint(self.interval - 30, self.interval - 10)
                sleeptime_two = random.randint(self.interval + 10, self.interval + 30)
                if i % 2 == 0:
                    sleeptime = sleeptime_two
                else:
                    sleeptime = sleeptime_one
                print
                'sleeping ' + str(sleeptime) + ' seconds...'
                time.sleep(sleeptime)
            else:
                break
        content.close()
        content = None

    def getTimescope(self, perTimescope, hours):
        if not (perTimescope == '-'):
            times_list = perTimescope.split(':')
            start_datetime = datetime.datetime.fromtimestamp(time.mktime(time.strptime(times_list[-1], "%Y-%m-%d-%H")))
            start_new_datetime = start_datetime + datetime.timedelta(seconds=3600)
            end_new_datetime = start_new_datetime + datetime.timedelta(seconds=3600 * (hours - 1))
            start_str = start_new_datetime.strftime("%Y-%m-%d-%H")
            end_str = end_new_datetime.strftime("%Y-%m-%d-%H")
            return start_str + ":" + end_str
        else:
            return '-'

    def main():
        logger = logging.getLogger('main')
        logFile = './collect.log'
        logger.setLevel(logging.DEBUG)
        filehandler = logging.FileHandler(logFile)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s: %(message)s')
        filehandler.setFormatter(formatter)
        logger.addHandler(filehandler)

        while True:
            ## 接受键盘输入
            keyword = raw_input('Enter the keyword(type \'quit\' to exit ):')
            if keyword == 'quit':
                sys.exit()
            startTime = raw_input('Enter the start time(Format:YYYY-mm-dd-HH):')
            region = raw_input('Enter the region([BJ]11:1000,[SH]31:1000,[GZ]44:1,[CD]51:1):')
            savedir = raw_input('Enter the save directory(Like C://data//):')
            interval = raw_input('Enter the time interval( >30 and deafult:50):')

            ##实例化收集类，收集指定关键字和起始时间的微博
            cd = CollectData(keyword, startTime, region, savedir, interval)
            while cd.flag:
                print
                cd.timescope
                logger.info(cd.timescope)
                url = cd.getURL()
                cd.download(url)
                cd.timescope = cd.getTimescope(cd.timescope, 1)  # 改变搜索的时间，到下一个小时
            else:
                cd = None
                print
                '-----------------------------------------------------'
                print
                '-----------------------------------------------------'
        else:
            logger.removeHandler(filehandler)
            logger = None

#if __name__ == '__main__'
#    main()

if __name__ == '__main__':
    keyword = "武汉肺炎"
    startTime = "-"
    CollectData()
 
def getWeiboContent(self):
    weiboContent = ""
    try:
        req = self.session.get(self.URL, headers=self.myheader)
        if req.status_code == 200:
            print ('This session work.')
        else:
            print ('This session not work with code 200.')
            return False
    except:
        print('This session not work.')
        return False
    try:
        page = req.content

    except httplib.IncompleteRead:
        print        ('Incompleted!')
        return False

    soupPage = BeautifulSoup(page, 'lxml')
    numList = soupPage.find_all('script')
    if len(numList) == 0:
        print        ('you may need to input an access code')
        return False
    for i in range(0, len(numList)):
        IsSearch = re.search(r"\"pid\":\"pl_weibo_direct\"", str(numList[i]))
        if IsSearch == None:
            continue
        else:
            weiboContent = str(numList[i])
            break
    return weiboContent


def getWeiboHtml(self):
    weiboContent = self.getWeiboContent()
    if weiboContent == "":
        print('WeiboContents are empty. You may need to input an access code.')
        return False
    elif weiboContent == False:
        return False

    # in case some empty json element
    substr = re.compile("\[\]")
    weiboContent = substr.sub("\"NULL\"", weiboContent)

    substr1 = re.compile("^.*STK.pageletM.view\\(")
    substr2 = re.compile("\\)$")
    substr4 = re.compile(r'\[')
    substr5 = re.compile(r'\]')
    substr6 = re.compile(r'\)</script>$')
    weiboContent = substr1.sub("", weiboContent)
    weiboContent = substr2.sub("", weiboContent)
    weiboContent = substr4.sub("", weiboContent)
    weiboContent = substr5.sub("", weiboContent)
    weiboContent = substr6.sub("", weiboContent)
    try:
        weiboJson = json.loads(weiboContent)
    except:
        print       ('Json Error!')
        return -3
    if weiboJson == None:
        print        ('you may need to input an access code')
        return True
    weiboHtml = weiboJson["html"]
    return weiboHtml

soup = BeautifulSoup(weiboHtml, 'lxml')
Noresult = soup.find_all('div',{'class':'pl_noresult'})
if len(Noresult) != 0:
  print ('NO result for the current search criteria.')
WeiboItemAll =  soup.find_all('div',{'action-type':'feed_list_item'})
WeiboItemFeed = soup.find_all('ul', {'class':'feed_action_info feed_action_row4'})
WeiboItemContent = soup.find_all('p',{'class':'comment_txt'})

for i in range(0, len(WeiboItemContent)):
    soupContent = BeautifulSoup(str(WeiboItemContent[i]), "lxml")
    soupAll = BeautifulSoup(str(WeiboItemAll[i]), "lxml")
    soupFeed = BeautifulSoup(str(WeiboItemFeed[i]), "lxml")

    mid = str(soupAll.div.attrs['mid'])
    STR = ""
    for string in soupContent.strings:
        STR += string
        content = STR
        when = soupAll.find('a', {'class': 'W_textb'})
        weibotime = str(when['title'])
        WeiboItemPraised = soupFeed.ul.contents[7]
        WeiboItemComment = soupFeed.ul.contents[5]
        WeiboItemForward = soupFeed.ul.contents[3]
        praisedString = WeiboItemPraised.contents[0].contents[0].contents[1].string
        commentContent = WeiboItemComment.contents[0].contents[0].contents
        forwardString = WeiboItemForward.contents[0].contents[0].contents[1].string

        if praisedString == None:
            praised = 0
        else:
            praised = int(str(praisedString))
        if len(commentContent) == 1:
            comment = 0
        else:
            comment = int(str(commentContent[1].string))

        if forwardString == None:
            forward = 0
        else:
            forward = int(str(forwardString))

def CreateWeiboTable(db_name):
    conn = sqlite3.connect(db_name)
    try:
        create_tb_sql = 
        CREATE TABLE IF NOT EXISTS weibo
        (mid TEXT,
        content TEXT,
        time TEXT,
        praised INTEGER,
        comment INTEGER,
        forward INTEGER); 
        conn.execute(create_tb_sql)
    except:
        print
        'CREATE table failed'
        return False
    conn.commit()
    conn.close()
    
dbname = test.db
CreateWeiboTable(dbname)
conn = sqlite3.connect(dbname)
# 抓取得到的微博数据
weiboitem = (mid, content, weibotime, praised, comment, forward)
conn.execute("INSERT INTO weibo VALUES(?,?,?,?,?,?)", weiboitem)
conn.commit()'''


import datetime
import urllib
import requests

tm_start = "2020-01-01-0"
tm_delta = datetime.timedelta(days=1)
tm_end = "2020-01-01-1"
keyword = '武汉肺炎'
class SinaCrawl():
  def __init__(self,keyword,tm_start,tm_end, session):
      self.url = "http://s.weibo.com/weibo?q="
      self.URL = self.url + base64.b64encode(urllib.parse.quote(keyword).encode("utf-8")).decode("utf-8") + '&typeall=1&suball=1&timescope=custom:'+str(tm_start)+':'+str(tm_end)+'&Refer=g'
      self.myheader = {'User-Agent':"Mozilla/5.0 (hp-tablet; Linux; hpwOS/3.0.2; U; de-DE) AppleWebKit/534.6 (KHTML, like Gecko) wOSBrowser/234.40.1 Safari/534.6 TouchPad/1.0"}
      self.session=session
  def getWeiboContent(self):
      weiboContent = ""
      try:
          req = self.session.get(self.URL, headers=self.myheader)
          if req.status_code == 200:
              print('This session work.')
          else:
              print('This session not work with code 200.')
              return False
      except:
          print('This session not work.')
          return False
      try:
          page = req.content

      except httplib.IncompleteRead:
          print('Incompleted!')
          return False

      soupPage = BeautifulSoup(page, 'lxml')
      numList = soupPage.find_all('script')
      if len(numList) == 0:
          print('you may need to input an access code')
          return False
      for i in range(0, len(numList)):
          IsSearch = re.search(r"\"pid\":\"pl_weibo_direct\"", str(numList[i]))
          if IsSearch == None:
              continue
          else:
              weiboContent = str(numList[i])
              break
      print (weiboContent)

  def getWeiboHtml(self):
     weiboContent = self.getWeiboContent()
     if weiboContent == "":
        print('WeiboContents are empty. You may need to input an access code.')
        return False
     elif weiboContent == False:
        return False

    # in case some empty json element
     substr = re.compile("\[\]")
     weiboContent = substr.sub("\"NULL\"", weiboContent)

     substr1 = re.compile("^.*STK.pageletM.view\\(")
     substr2 = re.compile("\\)$")
     substr4 = re.compile(r'\[')
     substr5 = re.compile(r'\]')
     substr6 = re.compile(r'\)</script>$')
     weiboContent = substr1.sub("", weiboContent)
     weiboContent = substr2.sub("", weiboContent)
     weiboContent = substr4.sub("", weiboContent)
     weiboContent = substr5.sub("", weiboContent)
     weiboContent = substr6.sub("", weiboContent)
     try:
        weiboJson = json.loads(weiboContent)
     except:
        print       ('Json Error!')
        return -3
     if weiboJson == None:
        print        ('you may need to input an access code')
        return True
     weiboHtml = weiboJson["html"]
     return weiboHtml
  soup = BeautifulSoup(weiboHtml, 'lxml')
  print(soup)
