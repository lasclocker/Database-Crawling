#encoding:utf8
import pycurl
import StringIO
import re
import urllib
import time
dicMonth = {'January':'01','February':'02','March':'03','April':'04','May':'05','June':'06','July':'07','August':'08','September':'09','October':'10','November':'11','December':'12','Spring':'03','Summer':'06','Autumn':'09','Fall':'09','Winter':'12'}
class MuseCrawler:

    def writeFile(self,url,Title,Authors,Source,DocumentType,Keywords,Abstract,date,term):
        term1 = term.split(' or ')[0]
        term2 = term.split(' or ')[1]
        bquery = '(' + term1 + ')' + 'AND' + '(' + term2 + ')'
	print '***urlNew***',url
	print 'bquery------------',bquery
        print 'term1-------------%s\tterm2----------------%s'%(term1,term2)
        print 'Title-------------',Title
        print 'Authors-----------',Authors
        print 'Source-----------',Source
        print 'DocumentType-----------',DocumentType
        print 'Keywords-----------',Keywords
        print 'Abstract-----------',Abstract
	print 'date-------------',date
	dic = {}
	dic['soc'] = Source
	dic['date'] = date
	dic['keyword'] = Keywords
	dic['title'] = Title
	dic['url'] = url
	dic['author'] = Authors
	dic['content'] = Abstract
    	dic['type'] = DocumentType
        f = open('Original_' + bquery + '.txt','a') #过滤前所抓取的信息
        f.write(str(dic) + '\n')
        f.close()
        content = Title + Abstract
        #print 'content:\n',content
        if term1 in content and term2 in content: #过滤后所抓取的信息
            print '#########################hit########################'
            f = open(bquery + '.txt','a')
            f.write(str(dic) + '\n')
            f.close()

    def extractContents(self,htmlTemp,term): #检索出来的文章分Journal和Book两类,利用re.findall提取所需信息
#Classification Unknown, Memorandum of Telephone Conversation, November16, 1971, 1015 Local Time, 1 
           contents = re.findall('<tr valign="top"><td><b>Citation(.*?)<tr valign="top"><td><b>Full Text',htmlTemp)[0]
           print '***contents***',contents
           Title = re.findall('ahref="(.*?)</b><br>',contents)[0] #第一步，缩小范围
           Title = re.findall('>(.*?)<',Title)[0] #第二步，巧用><取出所需内容
           Title = Title.replace('[','').replace(']','').replace('(','')
	   url = re.findall('&ItemID=(.*?)"',contents)[0]
           url = 'http://nsarchive.chadwyck.com/cat/displayItemId.do?queryType=cat&ItemID=' + url 
	   try:
	   	Date = re.findall('</b><br>(.*?)pp.</td>',contents)[0]
	   except Exception,e:
	   	Date = re.findall('</b><br>(.*?)</td>',contents)[0]
           print '***Date***',Date
	   #date = re.findall('>(.*?)<',date)[0]
	   try:
		year = Date.split(',')[-2].replace(' ','')
	   	dt = Date.split(',')[-3].replace('c.','').split(' ')[-1]
           	month = Date.split(',')[-3].replace('c.','').split(' ')[-2]
	   	print '***month***',month
	   	month = dicMonth[month]
	   except Exception,e:
		try:
			year = Date.split(',')[-2].replace(' ','')
	       		dt = Date.split(',')[-3][-2:]
           		month = Date.split(',')[-3][:-2].replace(' ','')
			month = dicMonth[month]
		except Exception,e:
			try:
				year = Date.split(',')[-2].replace(' ','')
				dt = Date.split(',')[-3][-1:]
				month = Date.split(',')[-3][:-1].replace(' ','')
				month = dicMonth[month]
			except Exception,e:
				try:
					year = Date.split(',')[-2].replace(' ','')
					yearTemp = year
					year = yearTemp[-4:]
					month = yearTemp[:-4].replace(' ','')
					dt = '01'
					month = dicMonth[month]
				except Exception,e:
					print '***error**',e
					try:
						year = Date.split(',')[-3].replace(' ','')
						dt = Date.split(',')[-4].split(' ')[-1]
           					month = Date.split(',')[-4].split(' ')[-2]
						month = dicMonth[month]
					except Exception,e:
						try:
							year = Date.split(',')[-3].replace(' ','')
							dt = Date.split(',')[-4].replace(' ','')[-2:]
                                                	month = Date.split(',')[-4].replace(' ','')[:-2]
                                                	month = dicMonth[month]
						except Exception,e:
							try:
								year = Date.split(',')[-3].replace(' ','')
								dt = Date.split(',')[-4].replace(' ','')[-1:]
                                                        	month = Date.split(',')[-4].replace(' ','')[:-1]
                                                        	month = dicMonth[month]
							except Exception,e:
								try:
									year = Date.split(',')[-2].replace(' ','')						
									month = Date.split(',')[-3].split(' ')[-1]
									dt = '01'
                							month = dicMonth[month]
								except Exception,e:
									yearTemp = Date.split(',')[-2].replace(' ','').replace('c.','')
									try:
										if int(yearTemp) > 1900:
											year = yearTemp
                                                                                	month = '01'
                                                                                	dt = '01'
									except Exception,e:
										try:
											year = yearTemp[-4:]
											month = yearTemp[:-4]
											print '---month---',month
											dt = '01'
											month = dicMonth[month]
										except Exception,e:
											try:
												year = Date.split(',')[-1].replace(' ','')
									                	dt = Date.split(',')[-2].replace('c.','').split(' ')[-1]
									                	month = Date.split(',')[-2].replace('c.','').split(' ')[-2]
									                	print '***month***',month	
									                	month = dicMonth[month]
											except Exception,e:
												year = '00'
												month = '00'
												dt = '00'
											
	   if len(dt) == 1:
	   	dt = '0' + dt
	   date = year + '-' + month + '-' + dt
           print '***year***',year
           AuthorsContents = ''.join(re.findall('Individuals/<br>Organizations(.*?)</tr>',contents))
           Authors = ''.join(re.findall('>(.*?)<',AuthorsContents))         
           #Source = ''.join(re.findall('"top"><td><b>Location(.*?)</tr>',contents)) # Source 首先由 Location of Original 确定
           #Source = ''.join(re.findall('>(.*?)<',Source))
           #</a></b><br>Confidential, Memorandum, c. April, 1982,3 pp.</td></tr>
	   #if Source == '':
           Source = ''.join(re.findall('"top"><td><b>Origin(.*?)</tr>',contents)) # Source 其次由 Origin 确定
           Source = ''.join(re.findall('>(.*?)<',Source))
           DocumentType = ''
           Keywords = ''.join(re.findall('Subjects:(.*?)</td></tr>',contents))
           Keywords = ''.join(re.findall('>(.*?)<',Keywords))         
           Abstract = ''.join(re.findall('Abstract:(.*?)</tr>',contents))
           Abstract = ''.join(re.findall('>(.*?)<',Abstract))           
           self.writeFile(url,Title,Authors,Source,DocumentType,Keywords,Abstract,date,term)
            
    def extractUrls(self,term,totalNum,ResultsID,n):

        print '***Downdloading term: %s\t***Downdloading totalNum: %d\t***Downdloading nums: %d\t'%(term,totalNum,n)  #记录抓取的信息,待完善    
        url = 'http://nsarchive.chadwyck.com/cat/displayItem.do?queryType=cat&&ResultsID=' + ResultsID + '&ItemNumber=' + str(n)
        print 'url--------------',url
        head = [
            'Host: nsarchive.chadwyck.com',
            'User-Agent: Mozilla/5.0 (Windows NT 5.1; rv:33.0) Gecko/20100101 Firefox/33.0',
            'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language: zh-cn,zh;q=0.8,en-us;q=0.5,en;q=0.3',
            'Accept-Encoding: gzip, deflate',
            'Cookie: JSESSIONID=E17228D8DC1A574685F523C3BD1F6B76; UID=shang',
            'Connection: keep-alive']
        time.sleep(0.5)       #每次抓取其内容时，间隔0.5s
        pc = pycurl.Curl()
        pc.setopt(pycurl.COOKIEFILE, 'Cookie.txt')#把cookie保存在该文件中
        pc.setopt(pycurl.COOKIEJAR, 'Cookie.txt')
        pc.setopt(pycurl.HEADER, 1)
        pc.setopt(pycurl.URL, url)
        pc.setopt(pycurl.VERBOSE,1)
        pc.setopt(pycurl.FOLLOWLOCATION, 1)
        pc.setopt(pycurl.MAXREDIRS, 5)
        pc.setopt(pc.HTTPHEADER,  head)
        pc.fp = StringIO.StringIO()
        pc.setopt(pc.WRITEFUNCTION, pc.fp.write)
        try:
            pc.perform()
        except Exception,e:
            print '*****perform error*****',e
            #if ('Timed out' in str(e)) or ("couldn't connect to host" in str(e)): #如果是'Failed to connect to nsarchive.chadwyck.com port 80: Timed out'
                #time.sleep(5)
            return 1
        htmlTemp = pc.fp.getvalue()
        print 'crawler success...'
	#f = open('timetime.html','w')
	#f.write(htmlTemp)
	#f.close()
	#exit()
        #print htmlTemp
        htmlTemp = htmlTemp.replace('\n','')
        f = open('select.html','w')
        f.write(htmlTemp)
        f.close()
	#exit()
        if 'Your session has timed out' in htmlTemp:
            print 'Your session has timed out'
            return 1
        else:
            self.extractContents(htmlTemp,term)  #提取文章的详细内容
            return 0
    def crawler(self,term):
        url = 'http://nsarchive.chadwyck.com/cat/search.do?clear=true'
        print 'url',url
        head = [
        'Host: nsarchive.chadwyck.com',
        'User-Agent: Mozilla/5.0 (Windows NT 5.1; rv:33.0) Gecko/20100101 Firefox/33.0',
        'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language: zh-cn,zh;q=0.8,en-us;q=0.5,en;q=0.3',
        'Accept-Encoding: gzip, deflate',
        'Connection: keep-alive']
        pc = pycurl.Curl()
        pc.setopt(pycurl.COOKIEFILE, 'Cookie.txt')#把cookie保存在该文件中
        pc.setopt(pycurl.COOKIEJAR, 'Cookie.txt')
        pc.setopt(pycurl.HEADER, 1)
        pc.setopt(pycurl.URL, url)
        pc.setopt(pycurl.VERBOSE,1)
        pc.setopt(pycurl.FOLLOWLOCATION, 1)
        pc.setopt(pycurl.MAXREDIRS, 5)
        pc.setopt(pc.HTTPHEADER,  head)
        pc.fp = StringIO.StringIO()
        pc.setopt(pc.WRITEFUNCTION, pc.fp.write)
        pc.perform()
        htmlTemp = pc.fp.getvalue()
        #print htmlTemp
        htmlTemp = htmlTemp.replace('\n','')
        f = open('security.html','w')
        f.write(htmlTemp)
        f.close()
        time.sleep(0.2)

        url = 'http://nsarchive.chadwyck.com/cat/executeSearch.do'
        print 'url',url
        head = [
        'User-Agent:	Mozilla/5.0 (Windows NT 5.1; rv:33.0) Gecko/20100101 Firefox/33.0',
        'Referer:	http://nsarchive.chadwyck.com/cat/search.do?clear=true',
        'Host:	nsarchive.chadwyck.com',
        'Connection:	keep-alive',
        'Accept-Language:	zh-cn,zh;q=0.8,en-us;q=0.5,en;q=0.3',
        'Accept-Encoding:	gzip, deflate',
        'Accept:	text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
        ]
        post_data_dic = {
        'toYear':	'2014',
        'toMonth':	'12',
        'toDay':	'31',
        'title':'',	
        'subject':	'',
        'sortType':	'chronological',
        'searchTerm':	term,
        'recipient':	'',
        'queryType':	'cat',
        'participants':	'',
        'PageSize':	'',
        'pageSize':	'20', 
        'page':	'1', 
        'name':	'',
        'itemNumber':	'',
        'fromYear':	'1942',
        'fromMonth':	'01',
        'fromDay':	'01',
        'folder':	'cat',
        'docNumber':'',	
        'creator':''	        
        }
        pc = pycurl.Curl()
        pc.setopt(pycurl.COOKIEFILE, 'Cookie.txt')#把cookie保存在该文件中  
        pc.setopt(pycurl.COOKIEJAR, 'Cookie.txt')
        pc.setopt(pycurl.POST, 1)
        pc.setopt(pycurl.HEADER, 1)
        pc.setopt(pycurl.URL, url)
        pc.setopt(pycurl.VERBOSE,1)
        pc.setopt(pycurl.FOLLOWLOCATION, 1)
        pc.setopt(pycurl.MAXREDIRS, 5)
        pc.setopt(pc.HTTPHEADER,  head)
        pc.fp = StringIO.StringIO()
        pc.setopt(pc.POSTFIELDS,  urllib.urlencode(post_data_dic))
        pc.setopt(pc.WRITEFUNCTION, pc.fp.write)
        pc.perform()
        htmlTemp = pc.fp.getvalue()
        #print htmlTemp
        f = open('security1.html','w')
        f.write(htmlTemp)
        f.close()
        htmlTemp = htmlTemp.replace('\n','')
        try:
            ResultsID = re.findall('<a href="/cat/singleResults.do\?queryType=cat&&ResultsID=(.*?)&pageNumber&pageSize',htmlTemp)[0] #找到ResultsID的值
        except Exception,e:
            print e
            return 0,0
        totalNum = re.findall('<strong>(.*?)</strong> records',htmlTemp)[0] #找到文章总数
        print totalNum
        totalNum = int(totalNum)
        print 'Your search produced %s records',totalNum
        return totalNum,ResultsID
    
def goEntrance():
    
    downloadNum = 0 #设置两个变量，用于把抓取速度限制在1000次/小时以内
    t = time.time()
    museCrawler = MuseCrawler() #定义类实例化对象
    try:
        bp = int(open('bp_log.txt','r').readlines()[0])
    except Exception,e:  #若没有此文件，则新建一个
        print e
        f = open('bp_log.txt','w')
        f.close()
        bp = 0
    Crawler_term_nums = bp #断点
    ls = open('kws.txt','r').readlines()
    ls = ''.join(ls)
    ls = ls.split('\n')
    lst = []
    for ls_s in ls[bp:7]: #断点虚抓
	    print ls_s
            ls_s = ls_s.split('+')
            temp = ls_s[0] + ' ' + 'or' + ' ' + ls_s[1]
            lst.append(temp)    
    print len(lst)
    for term in lst:    
        print 'term',term
        totalNum,ResultsID = museCrawler.crawler(term) #抓取检索首页及有关键词的第一页
        if totalNum == 0: #说明此关键词没有检索到相关文章
            print 'No Results Found'
            continue
        downloadNum += 1
        n = 1
        while (n <= totalNum) and (n <= 1000):#最多只要前1000的内容.
            wrong = museCrawler.extractUrls(term,totalNum,ResultsID,n)
            if wrong:  #如果 'Failed to connect to nsarchive.chadwyck.com port 80: Timed out',则切断程序。
		time.sleep(60*2)
		continue
	    n += 1
            downloadNum += 1
            if downloadNum >= 1500:
                temp = time.time() - t
                if temp < 3600:
                    print '每小时的访问次数已大于1500次，程序将休息%ds'%(3600 - temp)
                    time.sleep(3600 - temp)
                    t = time.time()
                    downloadNum = 0
        Crawler_term_nums += 1
        f = open('bp_log.txt','w')
        f.write(str(Crawler_term_nums)) #记录已经抓取的关键词的个数
        f.close()

if __name__ == "__main__":
    
    t1 = time.ctime()
    goEntrance()
    t2 = time.ctime()
    print t1,t2
