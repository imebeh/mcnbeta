#coding: utf-8
__author__ = 'gmebeh'

#import time
#import urllib2
from xml.sax.saxutils import escape

class SimpleRSS:
    __version__ = 0.99
    __author__  = 'gmebeh'
    #default values
    item= {
        'title'     : u'',
        'link'      : u'',
        'author'    : None,
        'category'  : None,
        'comments'  : None,
        'description'   : u'',
        'guid'      : None,
        'pubDate'   : None
    }
    channel= {
        'title'     : u'',
        'link'      : u'',
        'description'   : u'',
        'language'  : None,
        'copyright' : None,
        'lastBuildDate' : None,
        'pubDate'   : None,
        'category'  : None,
        'generator' : u'SimpleRSS v%s' % __version__,
        'docs'      : u'http://cyber.law.harvard.edu/rss',
        'ttl'       : None,
        'image'     : None,
        'item'      : []
    }
    rss= {
        'version'   : '2.0',
        'encoding'  : 'utf-8',
        'rss'       : []
    }

    def getSampleItem(self):
        return self.item

    def getSampleChannel(self):
        return self.channel

    def quoteString(self, str):
        try:
            #return urllib2.quote(str.encode('utf-8'))
            #return str.replace('<', u'&lt;').replace('>',u'&gt;')
            return escape(str)
        except Exception:
            return str

    def getRSSItem(self, title, link, description,
                   author= None, category= None, comments= None, guid= None, pubDate= None):
        itemX= dict()
        itemX.update(self.item)
        itemX.update({
            'title' : title,
            'link'  : link,
            'description'   : description
        })
        if author:      itemX.update({'author'   : author})
        if category:    itemX.update({'category' : category})
        if comments:    itemX.update({'comments' : comments})
        if guid:        itemX.update({'guid'     : guid})
        if pubDate:     itemX.update({'pubDate'  : pubDate})
        return itemX

    def getRSSChannel(self, title, link, description, items,
                      language= None, copyright= None, lastBuildDate=None, pubDate=None, category=None, ttl=None, image=None):
        channelX= dict()
        channelX.update(self.channel)
        channelX.update({
            'title' : title,
            'link'  : link,
            'description'   : description,
            'item'  : items
        })
        if language:        channelX.update({'language'      : language})
        if copyright:       channelX.update({'copyright'     : copyright})
        if lastBuildDate:   channelX.update({'lastBuildDate' : lastBuildDate})
        if pubDate:         channelX.update({'pubDate'       : pubDate})
        if category:        channelX.update({'category'      : category})
        if ttl:             channelX.update({'ttl'           : ttl})
        if image:           channelX.update({'image'         : image})
        return channelX

    def RSSDictToText(self, rssDict):
        #将填充好的 self.rss 结构的字典转换成 RSS 数据文本
        channels= rssDict['rss']
        s_channels= u''
        for channel in channels:
            items= channel['item']
            s_items= u''
            if type(items) is not list:
                raise TypeError #TODO: 类型检查放在生成相应的结构时
            for item in items:
                if type(item) is not dict:
                    raise TypeError #TODO: 类型检查
                s_item= u''
                for key in item:
                    if item[key]:
                        if key=='guid':
                            s_item+= u'\t\t\t<guid isPermaLink="%s">%s</guid>\n' % ((u'True' if item[key].lower()[:7]=='http://' else u'False'), item[key])
                        else:
                            s_item+= u'\t\t\t<%s>%s</%s>\n' % (key, self.quoteString(item[key]), key)
                s_items+= u'\t\t<item>\n%s\t\t</item>\n' % s_item
            #s_items= u'\t\t<item>\n%s\t\t</item>\n' % s_items

            s_channel= u''
            for key in channel:
                if key != 'item' and (channel[key]):
                    s_channel+= u'\t\t<%s>%s</%s>\n' % (key, self.quoteString(channel[key]), key)
            s_channel= u'%s%s' % (s_channel, s_items)

            s_channels+= u'\t<channel>\n%s\t</channel>\n' % s_channel


        rss= u'<?xml version="1.0" encoding="%s"?>' % rssDict['encoding']+\
             u'\n<rss version="%s">' % rssDict['version']+\
             u'\n%s</rss>' % s_channels
        return rss

    def getRSS(self, channels):
        rssX= dict()
        rssX.update(self.rss)
        rssX.update({'rss': channels})
        return self.RSSDictToText(rssX)


if __name__ == "__main__":
    x= SimpleRSS()
    item1= x.getRSSItem(
        title=  'item 1 title',
        link=   'item 1 link',
        description= u'item 1 desc中文'
    )
    item2= x.getRSSItem(
        title=  'item 2 title',
        link=   'item 2 link',
        description=    'item 2 desc'
    )
    channel= x.getRSSChannel(
        title=  'channel 1 test',
        link=   'channel 1 link',
        description=    'channel 1 desc',
        items= [item1, item2]
    )
    s= x.getRSS([channel, channel])
    print s
    #open('rss_test.xml', 'w').write(s)


