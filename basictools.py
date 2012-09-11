# -*- coding:utf8 -*-
__author__ = 'gmebeh'
__the_name__=  'basictools'
__the_version__= '0.1'
#version 2012/07/05

import hashlib
import urllib
import urllib2
import StringIO
import gzip
import time


class BasicTools():
    header = {
        'Accept':r'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'User-Agent':r'%s/%s zh-cn' % (__the_name__, __the_version__), #r'Opera/9.80 (Windows NT 6.1; U; IBM EVV/3.0/EAK01AG9/LE; zh-cn) Presto/2.10.229 Version/11.60',
        'Referer' : 'http://www.google.com/',
        'Accept-Language': 'zh-cn,zh;q=0.5',
        'Accept-Encoding':'gzip, deflate',
        'Accept-Charset':'GB2312,utf-8;q=0.7,*;q=0.7',
        'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8',
        'Connection':'keep-alive'
    }
    #cookie = urllib2.HTTPCookieProcessor()
    #opener = urllib2.build_opener(cookie)

    def __init__(self, opener = None, cookie = None, header = None):
        if cookie: self.cookie = cookie
        else: self.cookie = urllib2.HTTPCookieProcessor()
        if opener: self.opener = opener
        else: self.opener = urllib2.build_opener(self.cookie)
        if header: self.header.update(header)

    def updateHeaders(self, headers):
        self.header.update(headers)

    def request(self, url, method= 'POST', data= None, timeout= 60):
        if method.upper() == 'POST':
            if not data: data = {}
            data = urllib.urlencode(data).encode('utf-8')
            request = urllib2.Request(url= url,
                                      headers= self.header,
                                      data= data)
        elif method.upper() == 'GET':
            if data:
                data = urllib.urlencode(data).encode('utf-8')
                request = urllib2.Request(url =url + ('?%s' % data),
                                          headers= self.header)
            else:
                request = urllib2.Request(url =url,
                                          headers= self.header)
        else:
            return False
        try:
            response = self.opener.open(request, timeout= timeout)
        except Exception:
            return ''
        x= response.read()
        if 'gzip' in str(response.info().get('Content-Encoding')).lower():
            buf = StringIO.StringIO(buf = x)
            f = gzip.GzipFile(fileobj= buf)
            x = f.read()
        try:
            ret = x.decode('utf-8')
        except UnicodeDecodeError:
            ret = x
        response.close()
        return ret

def md5_3times_with_salt(str, salt):
    if type(str) is not list:
        return hashlib.md5((md5_3times(str.encode('utf-8')) + salt.encode('utf-8').upper()).encode('utf-8')).hexdigest().upper()
    else:
        # when type(str) == list, str means a md5_3timed string
        str = str[0]
        return hashlib.md5((str.upper().encode('utf-8') + salt.encode('utf-8').upper()).encode('utf-8')).hexdigest().upper()

def md5_3times(str):
    # 3次md5加密
    return hashlib.md5(hashlib.md5(hashlib.md5(str.encode('utf-8')).digest()).digest()).hexdigest().upper()

def md5(str):
    return hashlib.md5(str).hexdigest().upper()

def get_timestamp():
    return long(time.time() * 1000)

def readableFileSize(size):
    size= float(size)
    if size <1024.0:
        r= '%s Bytes' % size
    elif size <1024.0*1024:
        r= '%s KB' % round(size/1024,2)
    elif size <1024.0*1024*1024:
        r= '%s MB' % round(size/1024/1024,2)
    elif size <1024.0*1024*1024*1024:
        r= '%s GB' % round(size/1024/1024/1024,2)
    elif size <1024.0*1024*1024*1024*1024:
        r= '%s TB' % round(size/1024/1024/1024/1024,2)
    elif size <1024.0*1024*1024*1024*1024*1024:
        r= '%s PB' % round(size/1024/1024/1024/1024/1024,2)
    elif size <1024.0*1024*1024*1024*1024*1024*1024:
        r= '%s EB' % round(size/1024/1024/1024/1024/1024/1024,2)
    elif size <1024.0*1024*1024*1024*1024*1024*1024*1024:
        r= '%s ZB' % round(size/1024/1024/1024/1024/1024/1024/1024,2)
    elif size <1024.0*1024*1024*1024*1024*1024*1024*1024*1024:
        r= '%s YB' % round(size/1024/1024/1024/1024/1024/1024/1024/1024,2)
    else :
        r= 'many Bytes'
    return r

def unistring(str):
    #todo: 
    chars = str.split('\\')
    ret= ''
    for char in chars:
        if char:
            if char[0] == 'u':
                ret += unichr(eval('0x{0:>s}'.format(char[1:5])))
                ret += char[5:]
            elif char[0] in 'rn':
                ret += '\n'
                ret += char[1:]
            else:
                ret += char
    ret= ret.replace('<br />','\n')
    return ret

def allToStr(str):
    #urllib's many parameters need str
    try:
        return str.encode('utf-8')
    except UnicodeDecodeError:
        return str

def allToUni(str):
    try:
        return str.decode('utf-8')
    except UnicodeEncodeError:
        return str

def writefile(filepath, content, mode='wb'):
    f= open(filepath, mode)
    if f:
        f.write(allToStr(content))
        f.close()
        return True
    else:
        return False

def curl(url):
    return BasicTools().request(url = url, method = 'GET')

def wget(url, filepath):
    ret =BasicTools().request(url = url, method = 'GET')
    if ret:
        return writefile(filepath, ret)
    else:
        return False