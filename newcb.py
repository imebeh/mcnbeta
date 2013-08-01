#coding: utf-8

from basictools import *
import re
import json
import datetime
import time
import simprss
import Queue
import threading


class cnBeta():
    SITE_URL = u'http://www.cnbeta.com'
    URL_NEWS_LIST = u'%s/more.htm?jsoncallback=ug&type=all&page=%s&_=1376023684283' % (SITE_URL, '%s')
    URL_NEWS_COMMENT = u'%s/cmt?jsoncallback=ug&op=info&page=%s&sid=%s&sn=%s' % (SITE_URL, '%s', '%s', '%s')
    NEWS_COUNT_PER_MORE = 60
    LIST_SLEEP_RATE = [3600, 3600, 3600, 3600, 3600, 3600,   0,   0,   0,   0,   0, 600, 
                        600,  600,  600,  600,  600,  600, 600, 600, 600, 600, 600, 600]

    rePage = re.compile(ur'<div\sclass="content">(.+?)<div\sclass="clear"></div>'\
                        ur'.+?'\
                        ur'GV.DETAIL[\s]*=[\s]*{SID:"(\d+?)",POST_URL:"(.+?)",POST_VIEW_URL:"(.+?)",SN:"(.+?)"};'
        , re.DOTALL)
    #过滤评论中的短链
    reShortURL = re.compile(ur'[http://\s]+[\w\d\s]{2,6}.[\w\d\s]{2,3}/[\w\d\s]{2,8}/{0,1}')

    COMMENT_TEMPLATE = u'<strong>第%s名</strong><br/>\n%s 发表于 %s' \
                       u'<br/>%s <span style="color:#bc2931;">支持</span>(%s) 反对(%s)<br/>\n'
    NEWS_TEMPLATE = {
        'sid': '',
        'title': '',
        'content': '',
        'hometext': '',
        'logo': '',
        'url': '',
        'counter': '',
        'comments': [],
        's_comments': '',
        'hot': '',
        'score': '',
        'time': '1999-01-09 09:09:09'
    }
    News = {}

    bt = BasicTools()
    request = bt.request
    pages = Queue.Queue()
    pagesNow = Queue.LifoQueue()

    thdPages = None
    thdLists = None
    thdTemp = None

    def __init__(self):
        self.bt.updateHeaders({
            'X-Requested-With': 'XMLHttpRequest'
        })
        self.getSite()
        print 'init complete!'


    def dict_print(self, v, indent=0):
        s = '                                                             '
        t = type(v)
        if t == dict:
            print
            for x in v:
                print s[:indent], x, ':',
                self.dict_print(v[x], indent + 1)
        elif t == list or t == tuple:
            for x in v:
                self.dict_print(x, indent + 1)
        else:
            print v

    sa, sb, sc, sd = '', '', '', ''
    mutex = threading.Lock()

    def my_print(self, s=None, a=None, b=None, c=None, d=None):
        if self.mutex.acquire(1):
            if s is None and a is None and b is None and c is None and d is None:
                return
            self.sa = self.sa if a is None else a
            self.sb = self.sb if b is None else b
            self.sc = self.sc if c is None else c
            self.sd = self.sd if d is None else d
            print '\r                                                                              \r',
            if s is not None:
                try:
                    print s     #windows 的垃圾控制台不支持某些字符
                except:
                    pass
            print '\r', self.sa, self.sb, self.sc, self.sd, '\r',
            self.mutex.release()


    def getSite(self, url=SITE_URL, headers=None):
        r = None
        c_failed = 0
        if headers:
            self.bt.updateHeaders(headers)
        while True:
            r = self.request(url=url, method='GET')
            if not r or len(r) == 0:
                c_failed += 1
                if c_failed > 10: break
                time.sleep(c_failed)
                x = self.request(url=self.SITE_URL, method='GET')
            else:
                if r[:2] == u'ug':
                    #json result
                    try:
                        j = json.loads(r[3:-1])
                    except:
                        j = {}
                        pass
                    if j.has_key('status') and j.has_key('result') and j['status'] == u'success':
                        return j['result']
                else:
                    #html
                    break
        return r

    def threadTravelNewsList(self, page=1, sid=0, sleeptime=0):
        self.my_print('page %s, sid: %s, sleeptime: %s' % (page, sid, sleeptime))
        if page<1:
            self.my_print('page %s, sid: %s, failed, out!' % (page, sid))
            return

        url = self.URL_NEWS_LIST % page
        headers = {
            'Referer': self.SITE_URL
        }

        while True:
            r = self.getSite(url, headers)
            if r and type(r) is dict:
                r = r['list']
                i, c = 0, len(r)
                self.NEWS_COUNT_PER_MORE = c
                for x in r:
                    i += 1
                    if sid and sid==long(x['sid']):
                        self.pagesNow.put(x)
                        break
                    elif sid==0:
                        self.pages.put(x)
                        self.my_print(a='Page %s: %s/%s' % (page, i, c))

            if sleeptime > 0:
                self.my_print('page %s, wait  to sleep: %s' % (page, sleeptime))
                while self.pages.qsize()>0:
                    time.sleep(10)

                rate= self.LIST_SLEEP_RATE[int(time.strftime('%H'))]
                self.my_print('page %s, going to sleep: %s' % (page, rate))
                time.sleep(rate)
                self.my_print('page %s, going to sleep: %s' % (page, sleeptime))
                time.sleep(sleeptime)
                self.my_print('page %s, wakeup!' % page)
            else:
                if r: 
                    self.my_print('page %s, out!' % page)
                    break

    def threadTravelPages(self):
        while True:
            c = self.pages.qsize()
            d = self.pagesNow.qsize()
            self.my_print(b=u'Page Left: %s' % (c+d))
            while c==0 and d==0:
                time.sleep(5)
                c = self.pages.qsize()
                d = self.pagesNow.qsize()

            if c or d:
                if d:
                    p= self.pagesNow.get()
                elif c:
                    p = self.pages.get()

                try:
                    self.my_print(u'%s %s' % (p['sid'], p['title_show']))
                except:
                    pass

                news = {}
                news.update(self.NEWS_TEMPLATE)
                news.update({
                    'sid': p['sid'],
                    'title': p['title_show'],
                    'content': '',
                    'hometext': p['hometext_show_short'],
                    'logo': p['logo'],
                    'url': p['url_show'],
                    'counter': p['counter'],
                    'comments': [],
                    's_comments': '',
                    'hot': '',
                    'score': p['score'],
                    'time': p['time']
                })
                if self.News.has_key(long(p['sid'])):
                    t= self.News[long(p['sid'])]
                    news.update({
                        'comments' : t['comments'],
                        's_comments' : t['s_comments'],
                        'hot': t['hot']
                        })

                url = '%s%s' % (self.SITE_URL, p['url_show'])
                headers = {
                    'Referer': self.SITE_URL
                }

                # get content and sn
                time.sleep(0.5)
                html = self.getSite(url, headers)
                if html:
                    d = self.rePage.findall(html)
                    if d and len(d) == 1 and len(d[0])==5:
                        d= d[0]
                        news.update({
                            'content': d[0]
                        })

                        # comment
                        murl = self.URL_NEWS_COMMENT % (1, d[1], d[4])
                        head = {
                            'Referer': url
                        }
                        time.sleep(1)
                        c_comments = self.getSite(murl, head)
                        if c_comments and type(c_comments) is dict:
                            if c_comments.has_key('cmntstore'):
                                c_comments = c_comments['cmntstore'].values()
                                l_comments = len(c_comments)

                                scores = {}
                                comments_hot = ''
                                comments_all = ''
                                i = 0
                                for comm in c_comments:
                                    i += 1
                                    if not self.reShortURL.findall(comm['comment']):
                                        #print comm
                                        sco = int(comm['score']) - int(comm['reason']) * 1.2 + int(
                                            l_comments - i) * 0.0001

                                        #print sco
                                        if sco >= 4.5 and int(comm['score']) >= 5:
                                            scores.update({
                                                sco: comm
                                            })

                                        comments_all += self.COMMENT_TEMPLATE % (
                                            i,
                                            comm['name'] + u'来自[' + comm['host_name'] + ']' if len(
                                                comm['name']) else u'匿名人士',
                                            comm['date'],
                                            comm['comment'],
                                            comm['score'],
                                            comm['reason']
                                        )

                                ke = scores.keys()
                                ke.sort(reverse=True)
                                #print ke
                                for k in range(0, min(11, len(ke))):
                                    comm = scores[ke[k]]
                                    comments_hot += self.COMMENT_TEMPLATE % (
                                        k + 1,
                                        comm['name'] + u'来自[' + comm['host_name'] + ']' if len(
                                            comm['name']) else u'匿名人士',
                                        comm['date'],
                                        comm['comment'],
                                        comm['score'],
                                        comm['reason']
                                    )
                                if l_comments:
                                    news.update({
                                        'hot': comments_hot,
                                        's_comments': comments_all,
                                        'comments': c_comments
                                    })

                self.News.update({
                    long(p['sid']): news
                })

    def cacheNewsById(self, sid):
        # page= newest id - id /60
        sid= long(sid)
        if self.News.has_key(sid):
            self.pagesNow.put(self.News[sid])
            time.sleep(1)
            return

        reid = re.compile(ur'id=(\d+?)"')
        max_id = 0

        url = u'http://m.cnbeta.com'
        headers = {
            'Referer': None
        }
        html = self.getSite(url, headers)
        if html:
            ids = reid.search(html)
            if ids:
                max_id = long(ids.group(1))
        if max_id:
            page = long((max_id - sid) / self.NEWS_COUNT_PER_MORE) + 1
            time.sleep(1)
            self.threadTravelNewsList(page=page, sid= sid)
            time.sleep(1)

    def getRSS(self):
        x = simprss.SimpleRSS()
        items = []
        d = self.News.keys()
        d.sort(reverse=True)
        for sid in d:
            news = {}
            news.update(self.News[sid])
            try:
                news.update({
                    'time': news['time'] if news['time'] else u'1969-01-09 09:09:09'
                })
                items.append(x.getRSSItem(
                    title=news['title'],
                    link='%s%s' % (self.SITE_URL, news['url']),
                    description='%s<br/><br/><br/>%s' % (news['content'], news['hot']),
                    guid='http://www.cnbeta.com/articles/%s.htm' % news['sid'],
                    pubDate=datetime.datetime.strptime(news['time'], '%Y-%m-%d %H:%M:%S')
                    #- datetime.timedelta(hours= 8)
                ))
            except Exception, e:
                pass
        channel = x.getRSSChannel(
            title=u"cnBeta 全文RSS",
            link=u"http://www.cnbeta.com",
            description=u"cnBeta的全文+热评RSS",
            lastBuildDate=datetime.datetime.now(),
            items=items
        )
        return x.getRSS([channel])

    def getNewsByCount(self, count):
        d = self.News.keys()
        if len(d) == 0: return []
        d.sort(reverse=True)
        r = []
        i = 0
        for k in d:
            r.append(self.News[k])
            i += 1
            if i >= count: break
        return r

    def getNewsById(self, sid):
        sid = long(sid)
        if not self.News.has_key(sid):
            self.cacheNewsById(sid)

        if not self.News.has_key(sid):
            return None
        return self.News[sid]

    def getNewestId(self):
        d = self.News.keys()
        d.sort(reverse=True)
        return d[0]

    def getNewsByIndex(self, start, count, reverse=True):
        d = self.News.keys()
        d.sort(reverse=reverse)
        ret = []
        for idx in range(start - 1, start + count - 1):
            ret.append(self.getNewsById(d[idx]))
        return ret

    def Newest(self):
        return self.News[self.getNewestId()]


    def move(self, sid, reverse=False):
        sid = long(sid)
        if not self.News.has_key(sid):
            self.cacheNewsById(sid)

        d = long(sid)
        c = 0
        while True:
            c+=1
            if c>5: break
            if reverse:
                d = d - 1
            else:
                d = d + 1
            if not self.News.has_key(d):
                self.cacheNewsById(d)
                time.sleep(5)
            if self.News.has_key(d):
                break
            if d > int(self.getNewestId()):
                break

        return self.Newest() if self.News.has_key(d) == False else self.News[d]

    def Previous(self, sid):
        return self.move(sid,True)

    def Next(self, sid):
        return self.move(sid)

    def initNews(self):
        self.my_print('start thread')
        self.thdPages = threading.Thread(target=self.threadTravelPages)
        self.thdLists = threading.Thread(target=self.threadTravelNewsList, args= (1, 0, 600))
        self.thdTemp = threading.Thread(target= self.threadTravelNewsList, args= (2, 0, 0  ))

        self.thdPages.start()
        self.thdLists.start()
        self.thdTemp.start()

        #self.thdPages.join()
        self.thdLists.join()
        self.thdTemp.join()
        self.my_print('done')

    def updateNews(self, page):
        self.thdTemp = threading.Thread(target= self.threadTravelNewsList, args= (page, 0, 0  ))
        self.thdTemp.start()
        


