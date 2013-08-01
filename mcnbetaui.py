# coding: utf-8
__author__ = 'gmebeh'
#TODO: 学习web.py然后重构

import web
import mcnbeta
import newcb
import random
import threading
import time
import re
import base64

#x= mcnbeta.cnBeta()
x= newcb.cnBeta()

urls = (
    '/feed', 'feed',
    '/update/(\d*)', 'update',
    '/u/(\d*)', 'update',
    '/count/(\d*)', 'webUI',
    '/c/(\d*)', 'webUI',
    '/(\d*)/(next|previous|update|n|p|u|)','pageMove',
    '/start(\d*?)count(\d*?)','randomPages',
    '/s(\d*?)c(\d*?)','randomPages',
    '/topics/(\d+).htm', 'topics',
    '/(\d*)', 'webUI'
)
app = web.application(urls, globals())

def renderPages(pages, keywords={u'小米':u'粗粮', u'Xiaomi':u'粗粮', u'米聊':u'粗聊', u'MIUI':u'粗UI', u'360':u'数字'}):
    ret=[]
    stTime= time.time()
    render = web.template.render('templates')
    for b in pages:
        a={}
        a.update(b)
        a.update({
            'content': _replaceImgWithIframe(a['content'])
        })
        for k in keywords.keys():
            a.update({  
                'content': a['content'].replace(k, keywords[k]) if a['content'] and (a['content']!=True) else u'',
                'title'  : a['title'].replace(k, keywords[k]) if a['title'] else u''
            })
        ret.append(a)

    return render.webui(
        title= u'cnBeta 全文' if len(pages)>1 else pages[0]['title'] , 
        body= ret, 
        newsCount= len(x.News.keys()), 
        r= random.random(), 
        time= time, 
        stTime= stTime
    )

def _update(page):
    if int(page)>9999:
        #g= x.updateNewsById
        print 'update news id: %s' % page
        #threading.Thread(target= g, args= (page)).start()
        x.cacheNewsById(page)
        return web.redirect('/%s?r=%s' % (page, random.random()))
    else:
        print 'update page: %s' % page
        x.updateNews(page)
        return web.redirect('/?r=%s' % random.random())

def _findImgUrl(ret, content):
    reImage= re.compile(ur'<img.+(?<=src="http://img.cnbeta.com)(.+?)(?=")', re.I)
    if not content: return None
    r= reImage.findall(content)
    if r:
        for url in r:
            if not ret.has_key(url):
                ret.update({
                    #url:u'<iframe src="data:text/html;base64,%s"></iframe>' % base64.b64encode('<img src="%s"></img>' % url)
                    url:'<img src="http://img.cnbeta.com%s"/>' % url
                    })

def _replaceImgWithIframe(content):
    ret= u'%s' % content

    reImage= re.compile(ur'(?<=<img )(.*?)(?=>)', re.I)
    if len(ret)==0: return u''
    
    sFrame= u'<iframe width="100%%" frameborder="0" scrolling="no" id="%s" onload="this.height = document.getElementById(\'%s\').contentWindow.document.documentElement.scrollHeight;" src="data:text/html;base64,%s"></iframe>'
    r= reImage.findall(ret)
    if r:
        for url in r:
            rndName= (u'the%sname' % random.random()).replace('.','')
            ret= ret.replace(
                u'<img %s>' % url, 
                sFrame % (rndName, rndName, base64.b64encode((u'<img %s>' % url).encode('utf-8')))
            )
    return ret

class webUI:
    def GET(self, count= u''):
        print 'webUI count="%s"' % count
        ret= None
        if count.isdigit():
            if int(count)>9999:
                r=x.getNewsById(count)
                if r:
                    ret= [r]
                else:
                    ret= None
            else:
                ret= x.getNewsByCount(int(count))
        else:
            ret= x.getNewsByCount(30)

        if ret and len(ret): 
            return renderPages(ret)
        else:
            return web.notfound("404")

class randomPages():
    def GET(sefl, start, count):
        print start, count
        ret= x.getNewsByIndex(int(start), int(count))
        if ret: return renderPages(ret)

class pageMove:
    def GET(self, article, action= 'previous'):
        #print 'page move id: %s' % article
        if action=='next' or action=='n':
            ret= x.Next(article)
        elif action=='previous' or action=='p':
            ret= x.Previous(article)
        elif action=='update' or action=='u':
            return _update(article)
        else:
            ret= x.getNewsById(article)

        web.redirect('/%s' % ret['sid'])

class topics:
    def GET(self, sid):
        web.redirect('http://www.cnbeta.com/topics/%s.htm' % sid)

class update:
    def GET(self, page= 1):
        # TODO: print waiting info.
        _update(page)

class feed:
    def GET(self):
        return x.getRSS()

b= False
if __name__ == "__main__":
    if not b:
        b= True
        threading.Thread(target=x.initNews).start()
    app.run()


