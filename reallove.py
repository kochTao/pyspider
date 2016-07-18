#!/usr/bin/env python
# coding:utf-8
__author__ = 'Koch'

import urllib, urllib2
import re, os
import threading
import shutil,time


class MySpider:
    def __init__(self, url):
        self.searchUrl = url
        self.MmUrl = 'http://album.zhenai.com/u/'
        self.user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
        self.headers = {'User-Agent': self.user_agent}

    def getSearchPage(self, Searchurl, pageIndex):
        try:
            url = Searchurl + str(pageIndex)
            request = urllib2.Request(url, headers=self.headers)
            response = urllib2.urlopen(request)
            searchPage = response.read().decode('gbk')
            return searchPage
        except urllib2.URLError, e:
            if hasattr(e, "reason"):
                print u"搜索MM出错,错误原因", e.reason
                os.exit(1)

    def getOnePageList(self, pageIndex):
        Page = self.getSearchPage(self.searchUrl, pageIndex)
    # print searchPage
        pattern = re.compile('search_user_name.*?href=.*?/u/(.*?)".*?title="(.*?)".*?target.*?id=.*?title="(.*?)">',
                                 re.S)
        items = re.findall(pattern, Page)
        pageList = items
        return pageList


    def loopIndex(self,pageIndex):
        p = pageIndex
        while True:
            self.saveOnePage(p)
            if len(pageList) == 0:
                p += 1

    def saveOnePage(self, pageIndex):
        global  pageList
        pageList = self.getOnePageList(pageIndex)
        while True:
            if len(pageList):
                i = pageList.pop()
                mainIndex = self.MmUrl+i[0]
                print '--+'*20
                print u'页面剩余: %s' %(len(pageList))
                print u'第%s页，发现一位MM,名字叫 %s,今年%s' %(pageIndex,i[1],i[2])
                print u'她的主页为%s' %(self.MmUrl+i[0])
                defaultInfo,lifeInfo,dataInfo,gobbyInfo,termInfo,imagelist,text,privacyInfo = self.getMmPage(self.MmUrl,i[0])
                print u'总共有%s张个人照片' % (len(imagelist))
                print u'正在努力保存她的照片与信息 O(∩_∩)O~~ ...'
                name = i[1].split('.')[0].strip()
                path = 'mm/' + i[1].split('.')[0].strip() + '_id_' + i[0] + '/'
                self.mkdir(path)
                with open(path + name + '.txt','a+') as f:
                    f.write(u'\n--------------------她的主页-------------------- \n'.encode('utf-8'))
                    f.write(mainIndex.encode('utf-8'))
                    self.saveInfo(defaultInfo,u'基本信息',f)
                    self.printInfo(defaultInfo,u'基本信息')
                    f.write(u'\n--------------------内心独白-------------------- \n'.encode('utf-8'))
                    f.write(text[0].encode('utf-8'))
                    self.printInfo(termInfo,u'择偶条件')
                    self.saveInfo(dataInfo,u'详细资料',f)
                    self.saveInfo(lifeInfo,u'生活状况',f)
                    self.saveInfo(gobbyInfo,u'兴趣爱好',f)
                    self.saveInfo(privacyInfo,u'婚姻观点',f)
                    self.saveInfo(termInfo,u'择偶条件',f)
                    self.mutiThreadSaveImage(path,imagelist)
                    time.sleep(0.2)
            else:
                break

    def getMmPage(self, MmUrl, id):
        Page = self.getSearchPage(MmUrl, id)
        defaultInfo = self.getDefaultInfo(Page)
        lifeInfo = self.getLifeInfo(Page)
        dataInfo = self.getDataInfo(Page)
        gobbyInfo = self.getHobbyInfo(Page)
        privacyInfo = self.getPrivacyInfo(Page)
        termInfo = self.getTermInfo(Page)
        imagelist = self.getImage(Page)
        text = self.getPersonMessage(Page)
        return defaultInfo,lifeInfo,dataInfo,gobbyInfo,termInfo,imagelist,text,privacyInfo
    #基本信息
    def getDefaultInfo(self, Page):
    #defaultPattern = '.*?<td.*?class="label">(.*?)</span>(.*?)</td>.*?'
        p1 = re.compile('brief-center(.*?)</table>',re.S)
        item = re.findall(p1,Page)
        p2 = re.compile('label">(.*?)</span>(.*?)</td>',re.S)
    #pattern = re.compile('class="brief-table"' + defaultPattern * 9 + '</tr>', re.S)
        items = re.findall(p2,item[0])
        return items

    def getInfoMain(self,Page,p1):
        item = re.findall(p1,Page)
        try:
            p2 = re.compile('class="label">(.*?)<.*?field.*?>(.*?)</span',re.S)
            items = re.findall(p2,item[0])
        except Exception,e:
            items = []
        return items
    ##生活状况
    def getLifeInfo(self,Page):
        p1 = re.compile('floor-life posr clearfix">.*?"floor-table"(.*?)</table>',re.S)
        items = self.getInfoMain(Page,p1)
        return items
    #详细资料
    def getDataInfo(self,Page):
        p1 = re.compile('floor-data posr clearfix">.*?"floor-table"(.*?)</table>',re.S)
        items = self.getInfoMain(Page,p1)
        return items
    #item = re.findall(p2,Page)
            #p2 = re.compile('class="label">(.*?)<.*?field.*?>(.*?)</span',re.S)
            #items = re.findall(p2,item[0])
            #return items
        #兴趣爱好
    def getHobbyInfo(self,Page):
        p1 = re.compile('floor-hobby posr clearfix">.*?"floor-table"(.*?)</table>',re.S)
        items = self.getInfoMain(Page,p1)
        return items

    #婚姻观
    def getPrivacyInfo(self,Page):
        p1 = re.compile('floor-privacy posr clearfix">.*?"floor-table"(.*?)</table>',re.S)
        items = self.getInfoMain(Page,p1)
        return items

    #择偶条件
    def getTermInfo(self,Page):
        p1 = re.compile('floor-term posr clearfix">.*?"floor-table"(.*?)</table>',re.S)
        items = self.getInfoMain(Page,p1)
        return items

    #照片
    def getImage(self, Page):
        pattern = re.compile('<img data-big-img="(.*?)".*?data-mid-img', re.S)
        items = re.findall(pattern, Page)
        return items
    def saveInfo(self,list,type,f):
        f.write('\n--------------------%s--------------------\n' %(type.encode('utf-8')))
    #f.write('\n'+'-'*30 + type.encode('utf-8') +'-'*30' +'\n')
        for i in list:
            f.write('%s\t%s\n'%(i[0].encode('utf-8'),i[1].encode('utf-8')))

    def printInfo(self,list,type):
        print '\n--------------------%s--------------------\n' %(type)
        for i in list:
            print i[0],i[1]
    #内心独白&&自我描述
    def getPersonMessage(self,Page):
        pattern = re.compile('<p class.*?slider-area-js">(.*?)<span.*?class="info-mark"',re.S)
        replaceBR = re.compile('<br.*?/>')
        replaceNull = re.compile('&nbsp;')
        items = re.findall(pattern, Page)
        txt = []
        for i in items:
            text1 = re.sub(replaceBR,"\n",i)
    #print text1
            text = re.sub(replaceNull,"",text1)
            try:
                ss=text.split('<')
                txt.append(ss[0]+ss[1].split('>')[1])
            except Exception,ex:
                txt.append(text)
        return txt

    def saveOneImage(self, fileName, imgUrl):
        img = urllib.urlopen(imgUrl)
        data = img.read()
        try:
            with open(fileName, 'wb') as f:
                f.write(data)
                print u"保存她的一张图片为", fileName
        except Exception,ex:
            pass

    def mkdir(self,path):
        path = path.strip()
        isExists = os.path.exists(path)
        if not isExists:
            print u"新建了一个MM", path, u'的文件夹'
            os.makedirs(path)
            return True



    def mutiThreadSaveImage(self,path,imagelist):
        task_threads = []  # 存储线程
        count = 1
        for imgUrl in imagelist:
            fileName = path + str(count) + '.jpg'
            t = threading.Thread(target=self.saveOneImage, args=(fileName, imgUrl))
            count = count + 1
            task_threads.append(t)
        for task in task_threads:
            task.start()
        for task in task_threads:
            task.join()

    def saveText(self,content,name):
        fileName = name + "/" + name + ".txt"
        with open(fileName,"w+") as f:
            print u"她的个人信息保存到",fileName
            f.write(content.encode('utf-8'))


    def mutiThreadGetPage(self, pageList):
        task_threads = []  # 存储线程
        count = 1
        for p in pageList:
            t = threading.Thread(target=self.getMmPage, args=(self.MmUrl, p[0]))
            count = count + 1
            task_threads.append(t)
        for task in task_threads:
            task.start()
        for task in task_threads:
            task.join()


    class SaveIntoMongo:
        def __init__(self, dbname, host, dbpasswd):
            self.dbname = dbname
            self.host = host
            self.dbpasswd = dbpasswd


if __name__ == '__main__':

    url = 'http://search.zhenai.com/search/getfastmdata.jsps?condition=3&hash=TXlNZW1iZXJJZDo3NjE1MzMwNi9hZ2VCZWdpbjoyMC9hZ2VFbmQ6MzAvc2V4OjEvbXlzZXg6MC9p%0Ac2FsbDoxL2VkbToxL2xlZXI6MS9tZW1iZXJ0eXBlOjEvUGhvdG86MS9NZW1iZXJUeXBlOjEvQ29u%0Ac3RlbGxhdGlvbjotMS9BbmltYWxzOi0xL0JlbGllZjotMS9PY2N1cGF0aW9uOi0xL01hcnJpYWdl%0AOjEvaDotMS9jOjEvV29ya0NpdHk6MTAxMDEyMDEvU2FsYXJ5Oi0xL0VkdWNhdGlvbjo0L09yZGVy%0AOmhwZi9QYWdlOjEvUGFnZVNpemU6MjAv&orderby=hpf&cy=0&cyd=-1&currentpage='
    SS = MySpider(url)
    #SS.saveOnePage(20)
    SS.loopIndex(1)

