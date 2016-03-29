#encoding:utf-8
import pycurl
import StringIO
import urllib
import time
import re
import os
from datetime import datetime
from functools import partial
t1 = time.time()
t2 = time.ctime()

vid = '1'   #vid,sid,hid,CUSTOMVIEWSTATE这4个参数来自ebsco检索页面源码。注意这四个参数，要隔一段时间更新一下
sid = '22dedbf1-45c5-4640-9dc1-6953cb578013%40sessionmgr4003'
hid = '4201'
CUSTOMVIEWSTATE = 'H4sIAAAAAAAEAJWRwU/CMBTGs0IBgbiDCdGLlJB428aAIKAxMZw86MEoV1PWsjWu7Vw7lL9e14UFQjzo5eXlve/9vr7Xb8smNmz60+lwOPPHs5HdAZdnSxwzgjV9ph8ZVfpREgqsDljbZBeAZXTVGIsQAiryQsUUYBBjpeD5JyMUrbBiARLSUe9MIBpJpXMdzMcbJcPM1JdMsVVMI0JAw1S6FZOe7CRlrK73PWufnh7J2sVDTA/UDkxaT3jDwnyj1zSGF5HWydzzVJYkMtUuXalAuoHkXg6sF/K33oOmfCEzoUGlUzswKIn2QnKOBblPw4xToaH3G9UsXZCL9b0kZRscbN1I8zj3AsfUbg06f8BomnJVQiq/QK7/BekHMtmmLIz0wd2L/32hXxq2r/r+ZHaDhgN/jHJFszxwyyR12L/tOQ7KFE3nSPmDwWg0mbgcM+EWRgg5zh35AeqzLhpoAgAA'

buff = []

field_list = ['url','title','author','soc','type','keyword','content']

rlist = [
         '\d{1,2}/\d{1,2}/\d{4}', #01/01/2014
         '\d{1,2}/\d{1,2}/\d{2}', #01/01/14
         '[a-zA-Z]{3,10}\d{2,4}', #Jan2014
         '[a-zA-Z]{3,10}\s\d{4}', #Jan 2014
         '\d{4}\s[a-zA-Z]{3,10}', #2014 Jan
         '\d{8}', #20140101
         '\d{4}' #2014
        ]

templates = ['%m/%d/%Y','%m/%d/%y','%Y%m%d','%b%Y','%b%y','%b %Y','%Y %b','%Y']

rep_dict = {
               'Spring':'Mar',
               'Summer':'Jun',
               'Autumn':'Sep',
               'Winter':'Dec',
               'Annual':'Jan',
               'Fall':'Sep',
               'Spr':'Mar'
               }
soc_list = []
def replace(datestr):
    for keystr in rep_dict.keys():
        if keystr in datestr:
            return datestr.replace(keystr,rep_dict[keystr])
    return datestr

def format(datestr,template):
    try:
        date = datetime.strptime(datestr,template)
        return True,date.strftime('%Y-%m-%d')
    except:
        return False,None

def getDate(soc):
    global buff
    datestr = ''
    for r in rlist:
        dateli = re.findall(r,soc)
        if dateli:
            datestr = replace(dateli[0])
            func = partial(format,datestr)
            global buff
            for temp in buff + templates:
                answer,date = func(temp)
                if answer:
                    buff = [temp]
                    return date
                    break
            break
    return

def getSoc(soc):
    r = '[^(0-9a-zA-Z )]'
    if soc:
        p = re.findall(r,soc)[0]
        source = soc.split(p)[0]
        #print '--',source
        if source not in soc_list:
            soc_list.append(source)
        return source
    else:
        return None

def process(soc):
    date = getDate(soc)
    soc = getSoc(soc)
    if data == None:
        date = '0000-00-00'
    return soc,date

def exceptSolution(html,location,pc):  #处理页面过期异常
    #print html
    print 'sid lose efficacy!'
    f = open('EBSCO_error.txt','w')  #record error information
    f.write(html)
    f.close()
    source = 'http://web.a.ebscohost.com'
    newUrl = source + location
    #print 'newUrl',newUrl
    time.sleep(2)
    pc.setopt(pycurl.URL, newUrl)
    pc.setopt(pycurl.HTTPHEADER,  ['Content-Type: application/x-www-form-urlencoded'])  #important!
    pc.setopt(pc.WRITEFUNCTION, pc.fp.write)
    pc.perform()
    ls = pc.fp.getvalue()
    CUSTOMVIEWSTATE = re.findall('id="__CUSTOMVIEWSTATE" value="(.*?)" />',ls.replace('\n',''))
    CUSTOMVIEWSTATE = ''.join(CUSTOMVIEWSTATE)
    print 'CUSTOMVIEWSTATE',CUSTOMVIEWSTATE
    vid = re.findall('id="__vid" value="(.*?)" />',''.join(ls).replace('\n',''))
    vid = ''.join(vid)
    print 'vid',vid
    sid = re.findall('id="__sid" value="(.*?)" />',''.join(ls).replace('\n',''))
    sid = ''.join(sid)
    print 'sid',sid
    hid = re.findall('vid=%s&amp;hid=(.*?)"'%(vid),''.join(ls).replace('\n',''))
    hid = ''.join(hid)
    print 'hid',hid
    head = [
    'Host: web.a.ebscohost.com',
    'User-Agent: Mozilla/5.0 (Windows NT 5.1; rv:30.0) Gecko/20100101 Firefox/30.0',
    'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language: zh-cn,zh;q=0.8,en-us;q=0.5,en;q=0.3',
    'Accept-Encoding: gzip, deflate',
    'Referer: ' + newUrl,                  
    'Connection: keep-alive',
    'Content-Type: application/x-www-form-urlencoded'
    ]
    post_data_dic = {
    'RelRequestPath':	'error',
    'ajax':	'enabled',
    '__VIEWSTATE':'',	
    '__vid':	vid,
    '__sid':	sid,
    '__EVENTTARGET':	'ctl00$ctl00$MainContentArea$MainContentArea$linkError',
    '__EVENTARGUMENT':'',	
    '__CUSTOMVIEWSTATE':    CUSTOMVIEWSTATE	
    }
    pc = pycurl.Curl()
    pc.setopt(pycurl.COOKIEFILE, 'cookie.txt')#把cookie保存在该文件中  
    pc.setopt(pycurl.COOKIEJAR, 'cookie.txt') 
    pc.setopt(pycurl.POST, 1)
    pc.setopt(pycurl.HEADER, 1)
    pc.setopt(pycurl.URL, newUrl)
    pc.setopt(pycurl.VERBOSE,1)
    pc.setopt(pycurl.FOLLOWLOCATION, 0)
    pc.setopt(pycurl.MAXREDIRS, 5)
    pc.setopt(pycurl.HTTPPROXYTUNNEL,1)
    pc.setopt(pc.HTTPHEADER,  head)
    pc.fp = StringIO.StringIO()
    pc.setopt(pc.POSTFIELDS,  urllib.urlencode(post_data_dic))
    pc.setopt(pc.WRITEFUNCTION, pc.fp.write)
    pc.perform()
    html = pc.fp.getvalue()
    location = re.findall('Location: (.*?)\r', html)[0]
    print 'location',location
    source = 'http://web.a.ebscohost.com'
    newUrl = source + location
    #print 'newUrl',newUrl
    #time.sleep(2)
    pc.setopt(pycurl.URL, newUrl)
    pc.setopt(pycurl.HTTPHEADER,  ['Content-Type: application/x-www-form-urlencoded'])  #important!
    pc.setopt(pc.WRITEFUNCTION, pc.fp.write)
    pc.perform()
    ls = pc.fp.getvalue()
    print ls  #打印出新的搜索页面内容
    return ls

def downloadNextPage(num,newUrl): #抓取自动翻页（第2页-第5页）
    
    #翻页抓取
    while num <= 5:

        ls = open('EBSCO%d.html'%(num - 1),'r').readlines() #读取前一页的内容
        #print ls
        CUSTOMVIEWSTATE = re.findall('id="__CUSTOMVIEWSTATE" value="(.*?)" />',''.join(ls).replace('\n',''))
        CUSTOMVIEWSTATE = ''.join(CUSTOMVIEWSTATE)
        #print 'CUSTOMVIEWSTATE',CUSTOMVIEWSTATE
        vid = re.findall('id="__vid" value="(.*?)" />',''.join(ls).replace('\n',''))
        vid = ''.join(vid)
        print 'vid',vid
        sid = re.findall('id="__sid" value="(.*?)" />',''.join(ls).replace('\n',''))
        sid = ''.join(sid)
        #print 'sid',sid
        ls = re.findall('form method="post"(.*?)<!--\[if lt IE 7\]>',''.join(ls).replace('\n',''))
        hid = re.findall('hid=(.*?)&amp',''.join(ls).replace('\n',''))
        hid = ''.join(hid)
        #print 'hid',hid
        bquery = re.findall('bquery=(.*?)&amp',''.join(ls).replace('\n',''))
        bquery = ''.join(bquery)
        print 'bquery',bquery
        if bquery == '':
    #说明没有搜到这个关键词的结果
            print 'No search result!'
            break 
        bdata = re.findall('bdata=(.*?)"',''.join(ls).replace('\n',''))
        bdata = ''.join(bdata)
        #print 'bdata',bdata
        post_data_dic = {
        'SearchTerm':	bquery,
        'RelRequestPath':	'results',
        'PerformSearchSettingValue':	'2',
        'ctl00$ctl00$Column1$Column1$ctl00$isSliderChanged':	'0',
        'ctl00$ctl00$Column1$Column1$ctl00$HasSliderBeenSet':	'0',
        'ctl00$ctl00$Column1$Column1$ctl00$ctrlResultsDualSliderDate$txtFilterDateTo':	'2015',
        'ctl00$ctl00$Column1$Column1$ctl00$ctrlResultsDualSliderDate$txtFilterDateFrom':	'1841',
        'ctl00$ctl00$Column1$Column1$ctl00$ctrlResultsDualSliderDate$MinDateOrig':	'1841',
        'ctl00$ctl00$Column1$Column1$ctl00$ctrlResultsDualSliderDate$MaxDateOrig':	'2015',
        'common_DT1_ToYear':'',	
        'common_DT1_FromYear':'',
        'ajax':	'enabled',
        '_sort_order_':	'Desc',
        '_sort_order_':	'Desc',
        '_sort_':	'Hits',
        '_sort_':	'Hits',
        '_clusterId_':	'SubjectThesaurus',
        '_clusterId_':	'SubjectMajor',
        '_clusterId_':	'Subject',
        '_clusterId_':	'Journal',
        '_clusterId_':	'SubjectCompany',
        '_clusterId_':	'SubjectAge',
        '_clusterId_':	'SubjectGender',
        '_clusterId_':	'SubjectGeographic',
        '_clusterId_':	'SubjectNAICS',
        '__VIEWSTATE':'',	
        '__vid':	vid,
        '__sid':	sid,
        '__EVENTTARGET':	'ctl00$ctl00$MainContentArea$MainContentArea$bottomMultiPage$lnkNext',
        '__EVENTARGUMENT':'',	
        '__CUSTOMVIEWSTATE':    CUSTOMVIEWSTATE
           }



        head = [
            'Host: web.a.ebscohost.com',
            'User-Agent: Mozilla/5.0 (Windows NT 5.1; rv:30.0) Gecko/20100101 Firefox/30.0',
            'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language: zh-cn,zh;q=0.8,en-us;q=0.5,en;q=0.3',
            'Accept-Encoding: gzip, deflate',
            'Referer: ' + newUrl,                  
            'Connection: keep-alive',
            'Content-Type: application/x-www-form-urlencoded'
            ]

        url1 = 'http://web.b.ebscohost.com/ehost/results?sid=' + sid + '&vid=' + vid +'&hid=' + hid + '&bquery=' + bquery + '&bdata=' + bdata 
        time.sleep(2)
        pc = pycurl.Curl()
        pc.setopt(pycurl.COOKIEFILE, 'cookie.txt') 
        pc.setopt(pycurl.COOKIEJAR, 'cookie.txt') 
        pc.setopt(pycurl.POST, 1)
        pc.setopt(pycurl.HEADER, 1)
        pc.setopt(pycurl.URL, url1)
        pc.setopt(pycurl.VERBOSE,1)
        pc.setopt(pycurl.FOLLOWLOCATION, 0)
        pc.setopt(pycurl.MAXREDIRS, 5)
        pc.setopt(pycurl.HTTPPROXYTUNNEL,1)
        pc.setopt(pc.HTTPHEADER,  head)
        pc.setopt(pc.HTTPHEADER,  ['Content-Type: application/x-www-form-urlencoded'])    #important!
        pc.fp = StringIO.StringIO()
        pc.setopt(pc.POSTFIELDS,  urllib.urlencode(post_data_dic))
        pc.setopt(pc.WRITEFUNCTION, pc.fp.write)
        try:
                pc.perform()
                html = pc.fp.getvalue()
        except Exception,e:
                print e
        #print html
        b = open('EBSCO%d.html'%(num),'w')
        b.write(pc.fp.getvalue())
        b.close()
        num += 1
        time.sleep(2)

def downloadPageContents(bquery,Crawler_term_nums,each_term_num,break_flag,bquery_temp,bquery1,bquery2): #*************抓每一页的50篇论文的详细内容

    for k in range(1,6): #针对第1-5页
        ls = open('EBSCO%d.html'%(k),'r').readlines()
        html = ''.join(ls)
        html = html.replace('\n','')
        for i in range(50*k-49,50*k):
            print '***Downloading page: %d\t***Downloading terms：%s\t***Downdloading nums: %d'%(i,bquery,Crawler_term_nums + 1)
            try:
                url = re.findall('name="Result_%d" id="Result_%d" href="(.*?);'%(i,i),html)[0] #提取url
            except Exception,e:
                print e
                break_flag = 1
                break
            print 'url--------------',url
            time.sleep(0.5)
            pc = pycurl.Curl()
            pc.setopt(pycurl.FOLLOWLOCATION, 1) #important!
            pc.setopt(pycurl.URL,url)
            pc.fp = StringIO.StringIO()
            pc.setopt(pc.WRITEFUNCTION, pc.fp.write)
            try:
                pc.perform()  
                htmlTemp = pc.fp.getvalue() #获取该篇文章的详细内容
            except Exception,e:
                print e
                if "couldn't connect to host" in e:
                    time.sleep(2)
                    continue

            htmlTemp = htmlTemp.replace('\n','')

            #print htmlTemp
            Title = re.findall('<a name="citation"><span>(.*?)</span>',htmlTemp)[0]
            print 'Title-------------',Title
            Authors = ''.join(re.findall('Authors:</dt><dd>(.*?)</dd><dt>',htmlTemp))
            if Authors == '':
                Authors = ''.join(re.findall('Author\(s\):</dt><dd>(.*?)</dd><dt>',htmlTemp))
            Authors = Authors.split('<br />')
            AuthorsTemp = []
            for i in Authors:
                if '<sup>' in i:
                    i = ''.join(re.findall('(.*?)<sup>',i))
                if '<cite>' in i:
                    i = ''.join(re.findall('(.*?)<cite>',i))
                i = i.replace(',','')
                AuthorsTemp.append(i)   
            Authors = ','.join(AuthorsTemp)
            print 'Authors-----------',Authors
            Source = ''.join(re.findall('Source:</dt><dd>(.*?)</dd><dt>',htmlTemp)).replace('amp;','')
            Source,Date = process(Source)   #调用process函数,获得来源Source和日期Date.
            print 'Source-----------',Source
            print 'Date------------',Date
            DocumentType = ''.join(re.findall('Document Type:</dt><dd>(.*?)</dd>',htmlTemp))
            print 'DocumentType-----------',DocumentType
            Keywords = ''.join(re.findall('Keywords:</dt><dd>(.*?)</dd>',htmlTemp))
            Keywords = Keywords.replace('<br />',',')
            print 'Keywords-----------',Keywords
            Abstract = ''.join(re.findall('Abstract:</dt><dd>(.*?)</dd><dt>',htmlTemp))
            if Abstract == '':
                Abstract = ''.join(re.findall('Abstract \(English\):</dt><dd>(.*?)</dd><dt>',htmlTemp))
            Abstract = Abstract.replace('amp;','')
            print 'Abstract-----------',Abstract
            f = open('Original_' + bquery_temp + '.txt','a')  #记录筛选前的相关信息
            f.write(url + '\t' + Title + '\t' + Authors + '\t' + Source + '\t' + DocumentType + '\t' + Keywords + '\t' + Abstract + '\t' + Date + '\n')
            f.close()
            content = Title + Abstract
            if bquery1 in content and bquery2 in content: #记录筛选后的信息
                f = open(bquery_temp + '.txt','a')
                f.write(url + '\t' + Title + '\t' + Authors + '\t' + Source + '\t' + DocumentType + '\t' + Keywords + '\t' + Abstract + '\t' + Date + '\n')
                f.close()
                each_term_num += 1
                print '#################################each_term_num**************************:',each_term_num
        if break_flag == 1:
            break   

def ebsco_main(vid,sid,hid,CUSTOMVIEWSTATE):  #抓取主程序
    each_term_num = 0
    num = 2
    break_flag = 0
    bp = int(open('bp_log.txt','r').readlines()[0])
    Crawler_term_nums = bp
    ls = open('kws.txt','r').readlines()
    ls = ''.join(ls)
    #ls_terms = ls.split('\n')
    ls = ls.split('\n')
    lst = []
    #for ls_s in ls_terms:
    for ls_s in ls[bp:99]: #numbers of terms is 99
        ls_s = ls_s.split('+')
        if len(ls_s) > 2:
            print 'The length of query words >= 3 ! Please be careful!'
            break
        elif len(ls_s) < 2:
            lst.append(ls_s)
        else:
            temp = '(' + ls_s[0] + ')' + 'AND' + '(' + ls_s[1] + ')'
            lst.append(temp)    
    print len(lst)
    for bquery in lst:
        bquery_temp = bquery
        print 'bquery: ',bquery
        bquery1 = bquery.split(')AND(')[0][1:]
        bquery2 = bquery.split(')AND(')[1][:-1]
        #//////POST方法中的post_data_dic和head参数值
        post_data_dic = {
        'SearchTerm':	bquery,
        'searchMode':	'Bool',
        'RelRequestPath':	'search/basic',
        'PerformSearchSettingValue':	'3',
        'database_trh_PG4_NumVal':'',	
        'database_trh_PG4':'',	
        'database_nfh_PT68':'',
        'database_lxh_PT83':'',	
        'database_lxh_PG1':'',	
        'database_eric_PT10':'',
        'database_eric_LA5':'',	
        'database_eric_AN':'',	
        'database_eric_AG2':'',	
        'database_cmedm_SB8':'',	
        'database_cmedm_PT15':'',	
        'database_cmedm_CT3':'',	
        'database_a9h_PT82':'',	
        'database_a9h_PG4_NumVal':'',	
        'database_a9h_PG4':'',	
        'database_8gh_PT82':'',	
        'common_SO':'',	
        'common_DT1_ToYear':'',	
        'common_DT1_ToMonth':'',	
        'common_DT1_FromYear':'',
        'common_DT1':'',	
        'ajax':	'enabled',
        '__VIEWSTATE':'',	
        '__vid':	vid,
        '__sid':	sid,
        '__EVENTTARGET':'',	
        '__EVENTARGUMENT':'',	
        '__CUSTOMVIEWSTATE': CUSTOMVIEWSTATE	
            }

        head = [
            'Host: web.a.ebscohost.com',
            'User-Agent: Mozilla/5.0 (Windows NT 5.1; rv:30.0) Gecko/20100101 Firefox/30.0',
            'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language: zh-cn,zh;q=0.8,en-us;q=0.5,en;q=0.3',
            'Accept-Encoding: gzip, deflate',
            'Referer: http://web.a.ebscohost.com/ehost/search/basic?sid=' + sid + '&vid=' + vid + '&hid=' + hid,
            'Connection: keep-alive',
            'Content-Type: application/x-www-form-urlencoded'

            ]

        url = 'http://web.b.ebscohost.com/ehost/Search/PerformSearch?sid=' + sid + '&vid=' + vid

        time.sleep(2)
        pc = pycurl.Curl()
        pc.setopt(pycurl.COOKIEFILE, 'cookie.txt')#把cookie保存在该文件中  
        pc.setopt(pycurl.COOKIEJAR, 'cookie.txt') 
        pc.setopt(pycurl.POST, 1)
        pc.setopt(pycurl.HEADER, 1)
        pc.setopt(pycurl.URL, url)
        pc.setopt(pycurl.VERBOSE,1)
        pc.setopt(pycurl.FOLLOWLOCATION, 0)
        pc.setopt(pycurl.MAXREDIRS, 5)
        pc.setopt(pycurl.HTTPPROXYTUNNEL,1)
        pc.setopt(pc.HTTPHEADER,  head)
        pc.fp = StringIO.StringIO()
        pc.setopt(pc.POSTFIELDS,  urllib.urlencode(post_data_dic))
        pc.setopt(pc.WRITEFUNCTION, pc.fp.write)
        pc.perform()
        html = pc.fp.getvalue()
        location = re.findall('Location: (.*?)\r', html)[0]
        print 'location',location
        if '/Legacy/Views/static/html/Error.htm' in location:
            print '请更新检索首页中的sid,vid,hid,CUSTOMVIEWSTATE的参数值'
            return ''

        if '/ehost/error?sid=' in location:  #说明出现异常，这时我们要模拟浏览器让程序自动解决异常。
            ls = exceptSolution(html,location,pc)
            CUSTOMVIEWSTATE = re.findall('id="__CUSTOMVIEWSTATE" value="(.*?)" />',''.join(ls).replace('\n',''))
            CUSTOMVIEWSTATE = ''.join(CUSTOMVIEWSTATE)
            print 'CUSTOMVIEWSTATE',CUSTOMVIEWSTATE
            vid = re.findall('id="__vid" value="(.*?)" />',''.join(ls).replace('\n',''))
            vid = ''.join(vid)
            print 'vid',vid
            sid = re.findall('id="__sid" value="(.*?)" />',''.join(ls).replace('\n',''))
            sid = ''.join(sid)
            print 'sid',sid
            hid = re.findall('vid=%s&amp;hid=(.*?)"'%(vid),''.join(ls).replace('\n',''))
            hid = ''.join(hid)
            print 'hid',hid
            #print pc.fp.getvalue()
            ebsco_main(vid,sid,hid,CUSTOMVIEWSTATE)
            
        source = 'http://web.a.ebscohost.com'
        newUrl = source + location
        #print 'newUrl',newUrl
        time.sleep(2)
        pc.setopt(pycurl.URL, newUrl)
        pc.setopt(pycurl.HTTPHEADER,  ['Content-Type: application/x-www-form-urlencoded'])  #important!
        pc.setopt(pc.WRITEFUNCTION, pc.fp.write)
        pc.perform()
        #print pc.fp.getvalue()
        b = open('EBSCO1.html','w')
        b.write(pc.fp.getvalue())
        b.close()
        #print pc.fp.getvalue()
        downloadNextPage(num,newUrl)  #翻页抓取
        downloadPageContents(bquery,Crawler_term_nums,each_term_num,break_flag,bquery_temp,bquery1,bquery2)
        Crawler_term_nums += 1
        f = open('EBSCO_Crawlered_records.txt','a')
        f.write(str(Crawler_term_nums) + ' ' + bquery_temp + ' ' + str(each_term_num) + '\n')
        f.close()
        f = open('bp_log.txt','w')
        f.write(str(Crawler_term_nums))
        f.close()
        each_term_num = 0 #归0
        num = 2 #初始化
        break_flag = 0
       #time.sleep(2)

    print 'start running:',t2
    print 'final:',time.ctime()
    print 'total:',time.time() - t1
    
ebsco_main(vid,sid,hid,CUSTOMVIEWSTATE)  #抓取程序入口
