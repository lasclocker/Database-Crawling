#encoding:utf-8
import pycurl
import StringIO
import urllib
import time
import re
import os
import threading
from Queue import Queue
page = '100' #设定检索出来的页面显示100篇文章
downloadNum = 0
t = time.time()
class MuseCrawler:

    def extractContents(self,htmlTemp,url,DocumentType,term): #检索出来的文章分Journal和Book两类,利用re.findall提取所需信息
		dic = {}
		if DocumentType == 'Journal':
			dicMonth = {'January':'01','February':'02','March':'03','April':'04','May':'05','June':'06','July':'07','August':'08','September':'09','October':'10','November':'11','December':'12','Spring':'03','Summer':'06','Autumn':'09','Fall':'09','Winter':'12'}
			dicdate = {1:'01',2:'02',3:'03',4:'04',5:'05',6:'06',7:'07',8:'08',9:'09'}
			try:
				contents = re.findall('<!-- google -->(.*?)<!-- /google -->',htmlTemp)[0]
				Title = re.findall('<meta name="citation_title" content="(.*?)">',contents)[0]
			except Exception,e:
				print e
				return ''
			Authors = ''.join(re.findall('<meta name="citation_author" content="(.*?)">',contents))
			Abstract = ''.join(re.findall('<div class="abstract">(.*?)</div>',htmlTemp))
			Abstract = ''.join(re.findall('>(.*?)<',Abstract))
			Source = ''.join(re.findall('From: </span>(.*?)</div>',htmlTemp))
			Source = ''.join(re.findall('>(.*?)<',Source))
			Source = Source.replace('   ','')						
			dic['keyword'] = ''.join(re.findall('<strong>Keywords</strong><br>(.*?)</div>',htmlTemp))
			#print dic['keyword']			
			dic['url'] = url
			print dic['url']
			lineTemp = Title.split(':')
			if len(lineTemp) == 2:
				dic['title'] = lineTemp[1].strip('\(review\)')
				#print dic['title']
			else:
				dic['title'] = Title.strip('\(review\)')
				#print dic['title']
			dic['author'] = Authors
			#print dic['author']
			dic['soc'] = Source.split('Volume')[0]
			#print dic['soc']
			dic['type'] = DocumentType
			print dic['type']
			dic['content'] = Abstract.replace('In lieu of an abstract, here is a brief excerpt of the content:        ','')
			temp = ','.join(Source.split(',')[-2:]).split('pp')[0].split(' ')
			print temp
			try:			
				date = dicdate[int(temp[2].strip(','))]
				month = dicMonth[temp[3]]
				year = temp[4].split('/')[0].split('-')[0].split('|')[0]
				result = year + '-' + month + '-' + date
				print '***right***',result
				#num += 1
				dic['date'] = result
				f = open('museJournal.txt','a')
				f.write(str(dic) + '\n')
				f.close()
				#print line[0] + '\n' + dic['content']
				#print dic['soc']
				print dic['date']
			except Exception,e:
				try:
					date = dicdate[int(temp[2].strip(','))]
					if int(temp[3].split('/')[0].split('-')[0].split('|')[0]) > 1900 :
						yearMonth = temp[3].split('/')[0].split('-')[0].split('|')[0] + '-01-'
						result = yearMonth + date
						print '***right***',result
						#num += 1
						dic['date'] = result
						f = open('museJournal.txt','a')
						f.write(str(dic) + '\n')
						f.close()
						#print line[0] + '\n' + dic['content']
						#print dic['soc']
						print dic['date']
				except Exception,e:
					try:
						date = dicdate[int(temp[2].strip(','))]
						month = dicMonth[temp[3].split('-')[0]]
						year = temp[4].split('/')[0].split('-')[0].split('|')[0]
						result = year + '-' + month + '-' + date
						print '***right***',result
						#num += 1
						dic['date'] = result
						f = open('museJournal.txt','a')
						f.write(str(dic) + '\n')
						f.close()
						#print line[0] + '\n' + dic['content']
						#print dic['soc']
						print dic['date']
					except Exception,e:
						try:
							if int(temp[-3].split('/')[0].split('-')[0].split('|')[0]) > 1900:
								year = temp[-3].split('/')[0].split('-')[0].split('|')[0]
								month = dicMonth[temp[-4]]
								#date = dicdate[int(temp[-5].strip(','))]
								result = year + '-' + month + '-01'
								print '***right***',result
								#num += 1
								dic['date'] = result
								f = open('museJournal.txt','a')
								f.write(str(dic) + '\n')
								f.close()
								#print line[0] + '\n' + dic['content']
								#print dic['soc']
								print dic['date']
						except Exception,e:
							try:
								if int(temp[-3].split('/')[0].split('-')[0].split('|')[0]) > 1900:
									year = temp[-3].split('/')[0].split('-')[0].split('|')[0]
									result = year + '-01-01'
									print '***right***',result
									#num += 1
									dic['date'] = result
									f = open('museJournal.txt','a')
									f.write(str(dic) + '\n')
									f.close()
									#print line[0] + '\n' + dic['content']
									#print dic['soc']
									print dic['date']
							except Exception,e:
								try:
									if int(temp[-5].split('/')[0].split('-')[0].split('|')[0]) > 1900:
										year = temp[-5].split('/')[0].split('-')[0].split('|')[0]
										month = dicMonth[temp[-6]]
										result = year + '-' + month + '-01'
										print '***right***',result
										#num += 1
										dic['date'] = result
										f = open('museJournal.txt','a')
										f.write(str(dic) + '\n')
										f.close()
										#print line[0] + '\n' + dic['content']
										#print dic['soc']
										print dic['date']
								except Exception,e:
									pass
		elif DocumentType == 'Book':
			try:
				contents = re.findall('<div class="book_info">(.*?)</div>  <!-- book info -->',htmlTemp)[0]
				Title = re.findall('<h1 class="title"><span id="title_access_icon" class="access_no"></span>(.*?)</h1>',contents)[0]
			except Exception,e:
				print e
				return ''
			Authors = ''.join(re.findall('<p class="author">(.*?)</p>',contents))
			temp = Authors.replace('authored by ','')
			try:
				dic['author'] = re.findall('>(.*?)<',temp)[0]
			except Exception,e:
				dic['author'] = temp
			Abstract = ''.join(re.findall('<div class="description">      (.*?)      </div>',contents)).replace('<p>','').replace('</p>','').replace('<i>','').replace('</i>','')
			Keywords = ''
			dic['url'] = url
			dic['title'] = Title
			dic['type'] = DocumentType
			dic['keyword'] = Keywords
			dic['content'] = Abstract
			Source = ''.join(re.findall('<p class="publisher">Published by(.*?)</p>',htmlTemp))
			Source = ''.join(re.findall('>(.*?)</a>',Source))
			dic['soc'] = Source.split('Volume')[0]
			try:
				Date = re.findall('<p class="pubdate"><span>Publication Year:</span>(.*?)</p>',htmlTemp)[0]
				dic['date'] = Date + '-01-01'
			except Exception,e:
				dic['date'] = '00-00-00'
			f = open('museBook.txt','a')
			f.write(str(dic) + '\n')
			f.close()
		else:
			print 'documentType error!'
            
    def extractUrls(self,ls,Crawler_term_nums,maxNum,term,crawedNums):

        urls = re.findall('<div class="results_thumbnail">    \t<a href="(.*?)">',ls)
        documentTypes = re.findall('"This search result is for a (.*?)"',ls)
        for i in xrange(len(urls)):
            print '***Downdloading term: %s\t***Downdloading maxNum: %d\t***Downdloading nums: %d\t***Downdloading the num of terms are: %d\n'%(term,maxNum,Crawler_term_nums + 1,crawedNums)  #记录抓取的信息,待完善    
            url = 'http://muse.jhu.edu' + urls[i]
            print 'url--------------',url
            time.sleep(0.3)
            pc = pycurl.Curl()
            pc.setopt(pycurl.FOLLOWLOCATION, 1) #关键
            pc.setopt(pycurl.URL,url)
            pc.fp = StringIO.StringIO()
            pc.setopt(pc.WRITEFUNCTION, pc.fp.write)
            try:
                pc.perform()
            except Exception,e:
                print e
                if 'Failed to connect to muse.jhu.edu port 80: Timed out' in e:
                    continue
            htmlTemp = pc.fp.getvalue()
            print 'crawler success...'
            htmlTemp = htmlTemp.replace('\n','')
            documentType = documentTypes[i]
            empty = self.extractContents(htmlTemp,url,documentType,term)  #下载一篇文章的详细内容
            Crawler_term_nums += 1
        return Crawler_term_nums

class CrawlerButton:
	def crawlerMain(self,term1,term2,crawedNums):
		global t
		global downloadNum
		museCrawler = MuseCrawler()
		term = term1 + '+' + term2
		url = 'http://muse.jhu.edu/results'
		Crawler_term_nums = 0
		num = 1
		while num:
			if num == 1:
				post_data_dic = '[{initiatedSearch=1&type=ajax&startYear=&stopYear=&m=1&terms=content:' + term1 + ':AND&m=1&terms=content:' + term2 + ':AND&m=1&items_per_page=' + page + '}]' #来自上传流的请求头的内容
			else:
				post_data_dic = '[{type=ajax&startYear=&stopYear=&terms=content:' + term1 + ':AND&terms=content:' + term2 + ':AND&items_per_page=' + page + '&m=' + str(num) + '}]'
			head = [
				'X-Requested-With:	XMLHttpRequest',
				'User-Agent:	Mozilla/5.0 (Windows NT 5.1; rv:30.0) Gecko/20100101 Firefox/30.0',
				'Referer:	http://muse.jhu.edu/results',
				'Pragma:	no-cache',
				'Host:	muse.jhu.edu',
				'Content-Type:	application/x-www-form-urlencoded; charset=UTF-8',
				'Content-Length:    ' + str(len(post_data_dic)),  #此处最关键
				'Connection:	keep-alive',
				'Cache-Control:	no-cache',
				'Accept-Language:	zh-cn,zh;q=0.8,en-us;q=0.5,en;q=0.3',
				'Accept-Encoding:	gzip, deflate',
				'Accept:	*/*',
				'Cookie:    muse_last_search_id=1412819495368985; session=210.22.155.250.1412818127972039']

			pc = pycurl.Curl()
			pc.setopt(pycurl.POST, 1)
			pc.setopt(pycurl.URL, url)
			pc.setopt(pycurl.VERBOSE,1)
			pc.setopt(pycurl.FOLLOWLOCATION, 1)
			pc.setopt(pycurl.MAXREDIRS, 5)
			pc.setopt(pycurl.HTTPHEADER,  head)
			pc.fp = StringIO.StringIO()
			pc.setopt(pc.POSTFIELDS,  post_data_dic) #注意此处为post_data_dic
			pc.setopt(pc.WRITEFUNCTION, pc.fp.write)
			try:
				pc.perform()
			except Exception,e:
				print e
				time.sleep(5)
				f = open('exceptFile.txt','a') #记录漏掉的检索词
				f.write(term + '\n')
				f.close()
				f = open('exceptError.txt','a')
				f.write(str(e) + '\n')
				f.close()
				pass
			ls = pc.fp.getvalue()
			print 'Each page contains 100 papers,now crawled pages:\t',num/100 + 1
			ls = ''.join(ls).replace('\n','')
			if num == 1:
				ls1 = re.findall('<p class="result_count">(.*?)</p>',ls)
				ls2 = ''.join(ls1).replace(' ','').replace('\t','')
				ls3 = ls2.split('of')[-1]
				try:
				    maxNum = int(ls3) #获取检索出来的文章的总数
				except Exception,e:
				    print e
				    return ''    #说明没有搜到结果
				print 'ls3',ls3
				print '******maxNum results of the term(%s) are :'%(term),maxNum
			Crawler_term_nums = museCrawler.extractUrls(ls,Crawler_term_nums,maxNum,term,crawedNums)
			downloadNum += 1
			if downloadNum >= 1500: #设定抓取频率限制,1500篇/小时.
				temp = time.time() - t
				if temp < 3600:
					print '每小时的访问次数已大于1500次，程序将休息%ds'%(3600 - temp)
					time.sleep(3600 - temp)
					t = time.time()
					downloadNum = 0
			if Crawler_term_nums == maxNum: #当抓取完毕时,break
					break
			elif Crawler_term_nums >= 500: #限制抓取数量的上限,减少不必要的抓取
					break
			num += 100

           
class StartButton:
    
    def startFile(self):
		global queue
		global crawedNums
		crawlerButton = CrawlerButton()
		queue = Queue()
		crawedNums = 0
		if not os.path.exists('bp_log.txt'):
			f = open('bp_log.txt','w')
			f.write('0')
			f.close()
		bp = int(open('bp_log.txt','r').readlines()[0])
		crawedNums = bp
		ls = open('kws.txt','r').readlines()
		ls = ''.join(ls)
		ls = ls.split('\n')
	    
		for ls_s in ls[bp:]: #从断点处开始抓取
			queue.put(ls_s)
			while not queue.empty():
						ls_s = queue.get()
						print ls_s
						ls_st = ls_s.split('+')
						if len(ls_st) > 2:
							print 'The length of query words >= 3 ! Please be careful!'
							break
						elif len(ls_st) < 2:
							print 'The length of query words <2 ! Please be careful!'
							break
						else:
							term1 = ls_st[0]
							term2 = ls_st[1]
							empty = crawlerButton.crawlerMain(term1,term2,crawedNums)
							crawedNums += 1
							f = open('bp_log.txt','w')
							f.write(str(crawedNums))
							f.close()
							print 'Already craw nums are :',crawedNums
		print 'All terms have been crawed !'


startButton = StartButton()            
startButton.startFile() #启动抓取程序


