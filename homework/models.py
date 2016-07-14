# -*- coding: GBK -*-
import logging
import re

import urllib

import urllib2
from math import ceil
from urlparse import urlsplit, urljoin
from bs4 import BeautifulSoup
from datetime import datetime
from django.db import models
import hashlib
import requests
import time

# Create your models here.
from homework.info import PASSWD, HEJUN_BBS_SECRET
from homework.info import USER_NAME

BBS_HOME_URL = 'http://bbs.hejun.com'
BBS_LOGIN_URL = BBS_HOME_URL + '/member.php?mod=logging&action=login&loginsubmit=yes&infloat=yes&lssubmit=yes&inajax=1'
DISCUZ_SITE_NAME = 'R5s6_2132'
COOKIE_SALTKEY_NAME = DISCUZ_SITE_NAME + '_saltkey'
COOKIE_AUTH_NAME = DISCUZ_SITE_NAME + '_auth'

PAGE_SIZE = 200
HEJUN_BBS_API = 'http://bbs.hejun.com/api.php'


MUST_READ = '0'
CORE_LESSON_HOMEWORK = '1'
THREAD_TYPE_CHOICES = (
    (MUST_READ, 'MustRead'),
    (CORE_LESSON_HOMEWORK, 'CoreLessonHomework'),
)

logging.basicConfig(filename='hejun.log', filemode='a', level=logging.INFO)

class Class(models.Model):
    title = models.CharField(max_length=60)
    created = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return u"%s" % self.title


class Student(models.Model):
    name = models.CharField(max_length=60)
    bbs_id = models.CharField(max_length=60, unique=True)        #same with hejun bbs ID
    wihchclass = models.ForeignKey(Class, related_name='student', null=True)

    def __unicode__(self):
        return u"%s" % self.bbs_id

    def work_completed(self):
        res = {}
        for i in Thread.objects.all():
            replys = Reply.objects.filter(author=self, thread=i)
            total_words = 0
            post_time = datetime.now()
            for r in replys:
                total_words += r.contentLength
                if r.post_time < post_time:
                    post_time = r.post_time
            res[i.id] = (total_words, post_time.strftime("%Y-%m-%d %H:%M:%S"))
        #print res
        return res

class Thread(models.Model):                         #refer to "tong zhi bi du", "da ke zuo ye", etc
    tid = models.IntegerField(default=-1)
    title = models.CharField(max_length=200)
    url_addr = models.CharField(max_length=200)
    post_time = models.DateTimeField()
    thread_type = models.CharField(max_length=1, choices=THREAD_TYPE_CHOICES)
    last_update_time = models.DateTimeField(default=datetime.strptime('2015/1/1 0:0:0', '%Y/%m/%d %H:%M:%S'))
    last_update_page = models.IntegerField(default=1)
    last_update_page_api = models.IntegerField(default=1)

    def __unicode__(self):
        return u"%s -- %s" % (self.title, self.post_time)

    def update(self, start_page=1, end_page=-1):
        # proxy = urllib2.ProxyHandler({'http': '127.0.0.1:8080'})
        # opener = urllib2.build_opener(proxy)
        # urllib2.install_opener(opener)

        paramDic = {}
        paramDic['fastloginfield'] = 'username'
        paramDic['username'] = USER_NAME
        paramDic['password'] = PASSWD
        paramDic['quickforward']='yes'
        paramDic['handlekey']='ls'
        res = visit_response(BBS_LOGIN_URL, data=urllib.urlencode(paramDic))
        while (res==''):
            res = visit_response(BBS_LOGIN_URL, data=urllib.urlencode(paramDic))
            time.sleep(3)
        set_cookies = res.info().getheader('set-cookie')
        #print set_cookies
        temp = set_cookies[set_cookies.index(COOKIE_SALTKEY_NAME):]
        cookie_saltkey = temp[len(COOKIE_SALTKEY_NAME)+1:temp.index(";")]
        #print cookie_saltkey

        temp = set_cookies[set_cookies.index(COOKIE_AUTH_NAME):]
        cookie_auth = temp[len(COOKIE_AUTH_NAME)+1:temp.index(";")]
        #print cookie_auth

        header = {'Cookie' : COOKIE_SALTKEY_NAME + '=' + cookie_saltkey + ';' + COOKIE_AUTH_NAME + '=' + cookie_auth}
        #print header
        res = visit(self.url_addr, header)
        while (res==''):
            res = visit(self.url_addr, header)
            time.sleep(3)
        #print res
        soup = BeautifulSoup(res, 'html.parser', from_encoding="gb18030")
        page = soup.find('span', title=re.compile(ur'共 \d+ 页'))
        total_page = re.match(ur'共 (\d+) 页', page['title']).group(1)
        print total_page
        page = int(total_page)

        if end_page == -1 or end_page > page:
            end_page = page
        except_count = update_detail(self, start_page, end_page, header)
        self.last_update_time = datetime.now()
        self.last_update_page = end_page
        self.save()
        print 'exception count: ' + str(except_count)

    def updateWithJsonApi(self, start_page=1, end_page=-1):
        #get signature
        md5 = hashlib.md5()
        src = 'tid=' + str(self.tid) + '&' + HEJUN_BBS_SECRET
        md5.update(src)
        sign = md5.hexdigest()

        #get thread info
        repliesCount = -1
        params = dict(
            mod = 'thread',
            tid = self.tid,
            sign = sign
        )

        try:
            resp = requests.get(url=HEJUN_BBS_API, params=params)
            while resp.status_code != requests.codes.ok:
                resp = requests.get(url=HEJUN_BBS_API, params=params)
                print 'requests.get thread info failed'
                time.sleep(30)
            print resp
            respJson = resp.json()
            if respJson['status'] != 1:
                logging.error('update thread info with json api failed!')
                logging.error(str(respJson))
                return False
            else:
                data = respJson['data']
                fields = data[0]['fields']
                repliesCount = int(fields['replies'])
                if self.title == None:
                    self.title == fields['fulltitle']
                    self.url_addr = BBS_HOME_URL + '/' + data['url']
                    self.post_time = datetime.fromtimestamp(int(fields['dateline']))
                    self.save()
            logging.info('repliesCount of ' + str(self.tid) + ': ' + str(repliesCount))

        except Exception as e:
            print e.message
        print repliesCount

        # get replys info
        if repliesCount > 0:
            last_page = int(ceil(float(repliesCount) / PAGE_SIZE))
            end_page = end_page if end_page > last_page else last_page
            print 'start_page:' + str(start_page) + ', end_page:' + str(end_page)
            for i in range(start_page, end_page+1):
                print 'current page: %d' % i
                params = dict(
                    mod='post',
                    tid=self.tid,
                    dis_msg=0,
                    page=i,
                    limit=PAGE_SIZE,
                    sign=sign,
                )
                try:
                    resp = requests.get(url=HEJUN_BBS_API, params=params)
                    while resp.status_code != requests.codes.ok:
                        resp = requests.get(url=HEJUN_BBS_API, params=params)
                        print 'requests.get replys failed'
                        time.sleep(30)
                    print resp
                    respJson = resp.json()
                    if respJson['status'] != 1:
                        logging.error('update replies info with json api failed!')
                        logging.error(str(respJson))
                        return False
                    else:
                        data = respJson['data']
                        if (isinstance(data, dict)):
                            print 'replies count: %d' % len(data.keys())
                            for j in data:
                                post_id = int(j)
                                postInfo = data[j]
                                user_id = postInfo['author']
                                postTime = datetime.fromtimestamp(int(postInfo['dateline']))
                                #print 'get new reply: pid=%d, author=%s, post_time=%s' % (pid, user_id, str(postTime))
                                try:
                                    student = Student.objects.get(bbs_id=user_id)
                                except:
                                    logging.info('info: no such user, create it')
                                    k = -1
                                    while user_id[k].isdigit():
                                        k = k - 1
                                    k += 1
                                    if k == 0:
                                        user_name = user_id
                                    else:
                                        user_name = user_id[0:k]
                                    student = Student(name=user_name, bbs_id=user_id, wihchclass=None)
                                    student.save()

                                try:
                                    r = Reply.objects.get(reply_id=post_id)
                                except:
                                    logging.info('info: no such reply, create it')
                                    r = Reply(author=student, reply_id=post_id, post_time=postTime, thread=self,
                                              contentLength=-1)
                                r.contentLength = -1
                                print r
                                r.save()
                            if len(data.keys()) < PAGE_SIZE:
                                print 'reach last page, break'
                                break
                        elif (isinstance(data, list)):
                            print 'reach last page, break'
                            break
                        else:
                            logging.error('unkown result found')
                            logging.error(str(data))
                            break

                    self.last_update_page_api = i
                    self.save()
                except Exception as e:
                    print 'Exception found: ' + e.message
                    break
                time.sleep(5)
            self.last_update_time = datetime.now()
            self.save()
        return True



class Reply(models.Model):
    author = models.ForeignKey(Student)
    post_time = models.DateTimeField()
    thread = models.ForeignKey(Thread, related_name='reply')
    contentLength = models.IntegerField()
    reply_id = models.CharField(max_length=60, unique=True)

    def __unicode__(self):
        return u"%s reply %d words to %s at %s" % (self.author, self.contentLength, self.thread.title, self.post_time)



def visit(url, header=None, data=None, timeout=10, referer=BBS_HOME_URL):
    req = urllib2.Request(url)
    req.add_header('Referer', referer)
    req.add_header('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.10; rv:35.0) Gecko/20100101 Firefox/35.0')
    #req.add_header('X-Forwarded-For', '8.8.8.8')
    #req.add_header('Cookie', cookie)
    if header != None:
        for i in header:
            req.add_header(i, header[i])
    if data != None:
        req.add_data(data)
    res = ''
    try:
        response = urllib2.urlopen(req, timeout=timeout)
        res = response.read()
    except:
        print 'network problem: timeout'
    return res

def visit_response(url, header=None, data=None, timeout=10, referer=BBS_HOME_URL):
    req = urllib2.Request(url)
    req.add_header('Referer', referer)
    req.add_header('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.10; rv:35.0) Gecko/20100101 Firefox/35.0')
    req.add_header('X-Forwarded-For', '8.8.8.8')
    req.add_header('Content-Type', 'application/x-www-form-urlencoded')
    req.add_header('Cookie', '')
    if header != None:
        for i in header:
            req.add_header(i, header[i])
    if data != None:
        req.add_data(data)
    res = None
    try:
        res = urllib2.urlopen(req, timeout=timeout)
    except:
        print 'network problem: timeout'
    return res

def is_relative_url(url):
    s = urlsplit(url)
    if not s.scheme:
        return True
    else:
        return False

def to_absolute_url(baseurl,url):
    if not is_relative_url(url):
        return url
    else:
        return urljoin(baseurl,url)


def update_detail(thread, start_page, end_pages, header=None):
    except_count = 0
    print 'start_page:' + str(start_page) + ', end_pages:' + str(end_pages)
    for i in range(start_page, end_pages+1):
    #for i in range(100, 102):
        print 'current page: ' + str(i)
        res = visit(thread.url_addr + '&page=' + str(i), header)
        while res=='':
            res = visit(thread.url_addr + '&page=' + str(i), header)
            time.sleep(3)
        soup = BeautifulSoup(res, 'html.parser', from_encoding="gb18030")
        for tag in soup.find_all('div', id=re.compile(r'post\_\d+')):
            #print(tag['id'])
            try:
                post_id = re.match(r'post\_(\d+)', tag['id']).group(1)
            except:
                logging.exception('exception: get reply id failed')
                except_count += 1
                continue
            #print post_id

            try:
                del_tag = tag.find('em', text=ur'该用户已被删除')
                if del_tag == None:
                    user_tag = tag.find('a', href=re.compile(r'home\.php\?mod=space\&uid=\d+'))
                    if user_tag == None:
                        logging.exception('exception: get user id failed')
                        except_count += 1
                        continue
                    else:
                        #print 'here2'
                        #print user_tag
                        #print user_tag.contents
                        user_id = user_tag.string
                else:
                    #print 'here1'
                    user_id = del_tag.parent.contents[0]
            except:
                logging.exception('exception: get user id with del failed')
                except_count += 1
                continue
            #print user_id

            try:
                post_time_tag = tag.find('em', id=re.compile(r'authorposton\d+'))
                if post_time_tag.find('span') == None:
                    post_time = time.strptime(post_time_tag.string, u'发表于 %Y年%m月%d日 %H:%M',)
                else:
                    post_time = time.strptime(post_time_tag.find('span')['title'], u'%Y年%m月%d日 %H:%M')
                post_datetime = datetime(*post_time[:6])
            except:
                logging.warning('exception: get post time without second failed')
                try:
                    post_time_tag = tag.find('em', id=re.compile(r'authorposton\d+'))
                    if post_time_tag.find('span') == None:
                        post_time = time.strptime(post_time_tag.string, u'发表于 %Y年%m月%d日 %H:%M:%S',)
                    else:
                        post_time = time.strptime(post_time_tag.find('span')['title'], u'%Y年%m月%d日 %H:%M:%S')
                    post_datetime = datetime(*post_time[:6])
                except:
                    logging.exception('exception: get post time with second also failed')
                    except_count += 1
                    continue
            #print post_datetime

            try:
                c = tag.find('td', id=re.compile(r'postmessage_\d+'))
                content_length = len(c.get_text(strip=True))
            except:
                logging.exception('exception: get content_length failed')
                except_count += 1
                continue
            #print content_length

            try:
                student = Student.objects.get(bbs_id=user_id)
            except:
                logging.info('info: no such user, create it')
                i = -1
                while user_id[i].isdigit():
                    i = i-1
                i += 1
                if i == 0:
                    user_name = user_id
                else:
                    user_name = user_id[0:i]
                student = Student(name=user_name, bbs_id=user_id, wihchclass=None)
            #print student.bbs_id
            student.save()

            try:
                r = Reply.objects.get(reply_id=post_id)
            except:
                logging.info('info: no such reply, create it')
                r = Reply(author=student, reply_id=post_id, post_time=post_datetime, thread=thread, contentLength=content_length)
            r.contentLength = content_length
            #print r
            r.save()
        time.sleep(1)
    return except_count