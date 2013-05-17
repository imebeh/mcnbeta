# coding: utf-8
__author__ = 'gmebeh'

from basictools import *
import re
import datetime
import simprss

class cnBeta():
    __author__ = 'gmebeh'
    __name__ = 'mcnbeta'
    __version__ = 1.0
    TitlesPerPage= 30       #每页多少条新闻
    News = {
        #'id1'   :   {
        #    'title':    '', #标题
        #    'content':  '', #正文
        #    'comment':  '', #全部评论
        #    'hot':      ''  #热门评论
        #}
    }
    #rePage              = re.compile(ur'(?<=sid=)[0-9]+(?=">)|(?<=[0-9]{5}">)[^\n]+(?=</a><br)')
    #reTitle             = re.compile(ur'(?<=<title>).*(?=_cnBeta手机版</title>)')
    #reTime              = re.compile(ur'(?<=新闻发布日期：</b>).*(?=<br/><b>)')
    #reComment           = re.compile(ur'(?<=\n\t\t \n\t\t).*(?=<br/>\n\t\t \n      )', re.S + re.U)
    #reCommentContent    = re.compile(ur'(?<=\t   \n\t   ).*(?=\n)')
    #reCommentIndex      = re.compile(ur'(?<=<strong>).*(?=</strong>)')
    #reCommentTime       = re.compile(ur'(?<=<br/>).*(?=</span><br/>\n)')
    #reCommentVoteUp     = re.compile(ur'(?<=\(<span >)[0-9]+(?=</span>\) )')
    #reCommentVoteDown   = re.compile(ur'(?<=\(<span >)[0-9]+(?=</span>\);)')
    reContent           = re.compile(ur'(?<=返回首页</a><br/><br/>).*(?=<a href="hcomment.php\?)',re.S + re.U)
    
    rePage              = re.compile(ur'sid=([0-9]{4,7})">([^\n]+?)</a>')
    reTitle             = re.compile(ur'</head>\n<b>([^\n]+?)</b>')
    reTime              = re.compile(ur'<b>文章发布日期：</b>([0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2})<br/>')
    #reComment           = re.compile(ur'<br/>\n\n\t\t\n(.*)\t\n\t<br/>\n', re.S + re.U)
    reContent           = re.compile(ur'</script><br>(.*?)<script type="text/javascript">',re.DOTALL)
    
    
    request = BasicTools().request

    def __init__(self, url= r'http://m.cnbeta.com'):
        self.url= url
        print 'inited cnBeta class.'

    def updateNewsContent(self, id):
        id= unicode(id)
        url= '%s/marticle.php?sid=%s' % (self.url, id)
        html= self.request(url= url, method= 'GET')
        if html:
            r= self.reContent.findall(html)
            t= self.reTitle.findall(html)
            e= self.reTime.findall(html)

            #print r,t,e

            if not self.News.has_key(id):
                self.News.update({
                    id : {
                        'id': int(id),
                        'comment': u'',
                        'hot': u''
                    }
                })
            self.News[id].update({
                'time'   : e[0] if e else None,
                'content': r[0] if r else None,
                'title'  : t[0] if t else None
            })
            return True
        return False

    def updateNewsComment(self, id, isHotNews= False):
        id= unicode(id)
        if isHotNews:
            url= '%s/hcomment.php?sid=%s' % (self.url, id)
        else:
            url= '%s/mcomment.php?sid=%s' % (self.url, id)
        html= self.request(url= url, method= 'GET')
        if html:
            r= self.reComment.findall(html)
            if not self.News.has_key(id):
                self.updateNewsContent(id)
            
            if isHotNews:
                self.News[id].update({
                    'hot': r[0] if r else None
                })
            else:
                self.News[id].update({
                    'comment': r[0] if r else None
                })
            return True
        return False

    def updateNewsById(self, id):
        id= unicode(id)
        if not self.News.has_key(id):
            self.News.update({
                id : {
                    'id': int(id),
                    'time': None,
                    'content': None,
                    'comment': None,
                    'hot': None
                }
            })
        self.updateNewsContent(id)
        #self.updateNewsComment(id)
        self.updateNewsComment(id, isHotNews= True)

    def updateNews(self, page= 1):
        if page<1: page= 1
        url= '%s/index.php?pageID=%s' % (self.url, page)

        html= self.request(url= url, method= 'GET')
        if html:
            m= self.rePage.findall(html)
            if not m:
                return False
            c=len(m)
            i=0
            for x in m:
                i+=1
                nid= int(x[0])
                title=x[1]

                print '\t page %s: news %s of %s\n\t  %s' % (page, i, c, title)

                if self.News.has_key(nid):
                    self.News[nid].update({
                        'id': nid,
                        'title': title
                    })
                else:
                    self.News.update({
                        unicode(nid) : {
                            'id': nid,
                            'title': title,
                            'time': None,
                            'content': None,
                            'comment': None,
                            'hot': None
                        }
                    })
                self.updateNewsById(nid)


            # for i in range(1, c, 2):
            #     print '\t page %s: news %s of %s' % (page, (i+1)/2, c/2)
            #     if self.News.has_key(m[i-1]):
            #         self.News[m[i-1]].update({
            #             'id': int(m[i-1]),
            #             'title': m[i]
            #         })
            #     else:
            #         self.News.update({
            #             unicode(m[i-1]) : {
            #                 'id': int(m[i-1]),
            #                 'title': m[i],
            #                 'time': None,
            #                 'content': None,
            #                 'comment': None,
            #                 'hot': None
            #             }
            #         })
            #     self.updateNewsById(m[i-1])
                #if i>0: return True
            self.TitlesPerPage= c
            return True
        return False

    def getRSS(self):
        x= simprss.SimpleRSS()
        items=[]
        d= self.News.keys()
        d.sort(reverse= True)
        for id in d:
            news= self.News[id]
            try:
                news.update({
                    'time' : news['time'] if news['time'] else u'1999-01-09 09:09:09'
                })
                items.append(x.getRSSItem(
                    title   = news['title'],
                    link    = 'http://www.cnbeta.com/articles/%s.htm' % news['id'],
                    description = '%s<br/><br/><br/>%s' % (news['content'],news['hot']),
                    guid    = 'http://www.cnbeta.com/articles/%s.htm' % news['id'],
                    pubDate = datetime.datetime.strptime(news['time'], '%Y-%m-%d %H:%M:%S') #- datetime.timedelta(hours= 8)
                ))
            except Exception, e:
                pass
        channel= x.getRSSChannel(
            title = u"cnBeta 全文RSS",
            link = u"http://www.cnbeta.com",
            description = u"cnBeta的全文+热评RSS",
            lastBuildDate = datetime.datetime.now(),
            items = items
        )
        return x.getRSS([channel])

    def getNewsByCount(self, count):
        d= self.News.keys()
        if len(d)==0: return []
        d.sort(reverse= True)
        r= []
        i= 0
        for k in d:
            r.append(self.News[k])
            i+=1
            if i >= count: break
        return r

    def getNewsById(self, id):
        if self.News.has_key(id):
            if self.News[id]['content']==True:
                self.updateNewsById(id)
            return self.News[id]
        else:
            r= self.Newest()
            if r['content']==True:
                self.updateNewsById(r['id'])
            return self.Newest()

    def getNewestId(self):
        d= self.News.keys()
        d.sort(reverse= True)
        return d[0]

    def getNewsByIndex(self, start, count, reverse= True):
        d= self.News.keys()
        d.sort(reverse= reverse)
        ret= []
        for idx in range(start-1, start+count-1):
            ret.append(self.getNewsById(d[idx]))
        return ret

    def Newest(self):
        return self.News[self.getNewestId()]

    def Previous(self, id):
        d= self.News.keys()
        d.sort(reverse= True)
        if d.index(id)+1==len(d):
            return self.News[d[-1]]
        else:
            return self.News[d[d.index(id)+1]]

    def Next(self, id):
        d= self.News.keys()
        d.sort()
        if d.index(id)+1==len(d):
            return self.News[d[-1]]
        else:
            return self.News[d[d.index(id)+1]]

if __name__ == "__main__":
    x= cnBeta()
    x.updateNewsById(203394)
    max_page= raw_input(u'max page: ')
    if not max_page.isdigit(): max_page= 1
    max_page= int(max_page)
    if max_page<1: max_page= 1
    for i in range(1, max_page+1):
        print 'page %s of %s' % (i, max_page)
        x.updateNews(page=i)

    rss= x.getRSS()
    r=allToStr(x.getRSS())
    f=open("mcnbeta.xml", "w")
    f.write(r)
    f.close()
    
    print 'Update complete, exit after 5 seconds.'
    time.sleep(5)
    exit(0)
