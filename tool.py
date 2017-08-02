# coding=utf-8
import urllib
import urllib2
import re
import thread
import time
import MySQLdb
import traceback
import sys

i=1

class QSBK:

    def __init__(self):
        self.pageIndex = 1
        self.user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
        self.headers = {'User-Agent': self.user_agent}
        self.stories = []
        self.enable = False

    def getPage(self, pageIndex):
        try:
            url = 'http://www.qiushibaike.com/hot/page/' + str(pageIndex)
            request = urllib2.Request(url, headers=self.headers)
            response = urllib2.urlopen(request)
            pageCode = response.read().decode('utf-8')
            return pageCode
        except urllib2.URLError, e:
            if hasattr(e, "reason"):
                print "error", e.reason
                return None

    def getPageItems(self, pageIndex):
        pageCode = self.getPage(pageIndex)
        if not pageCode:
            print "page load error"
            return None
        pattern = re.compile(
            'h2>(.*?)</h2.*?content">(.*?)</.*?number">(.*?)</', re.S)
        items = re.findall(pattern, pageCode)
        pageStories = []
        for item in items:
            pageStories.append(
                [item[0].strip(), item[1].strip(), item[2].strip()])
        return pageStories

    def loadPage(self):
        if self.enable == True:
            if len(self.stories) < 2:
                pageStories = self.getPageItems(self.pageIndex)
                if pageStories:
                    self.stories.append(pageStories)
                    self.pageIndex += 1

    def getOneStory(self, pageStories, page):
        # 打开数据库连接
        db = MySQLdb.connect(host='127.0.0.1', user='root',
                                     passwd='123', db='test', port=3306, charset='utf8')

        global i
        for story in pageStories:
            if i > 1000:
                print "数据库即将关闭"
                # 关闭数据库连接
                db.close()
                sys.exit()
                break
            '''input = raw_input()'''
            self.loadPage()
            '''if input == "Q":
                self.enable = False
                return'''
            '''print u"第%d页\t发布人：%s\t 赞：%s\n%s" % (page, story[0], story[2], story[1])
            '''

            # 使用cursor()方法获取操作游标
            cursor = db.cursor()

            # SQL 插入语句
            sql = "INSERT INTO qsbk(pagenum,author,pointnum,content) VALUES ('%s','%s','%s','%s')" % (
                    page, story[0], story[2], story[1])
            try:
                # 执行sql语句
                cursor.execute(sql)
                # 提交到数据库执行
                db.commit()
                print "成功爬取 %d 条\n" %(i)
            except:
                # Rollback in case there is any error
                db.rollback()
                traceback.print_exc()
                print "失败"
            i+=1
        
        

    def start(self):
        print u'正在读取，回车查看，Q退出'
        self.enable = True
        self.loadPage()
        nowPage = 0
        while self.enable:
            if len(self.stories) > 0:
                pageStories = self.stories[0]
                nowPage += 1
                del self.stories[0]
                self.getOneStory(pageStories, nowPage)

spider = QSBK()
spider.start()
