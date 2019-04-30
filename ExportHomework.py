#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
import io
import logging
import os,sys,getopt
import time,datetime
import subprocess

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.select import By
import datetime
import time
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.select import Select
from pyquery import PyQuery as pq

import traceback

class Time_p:  
	def __init__(self):
		pass
		
	def getNowYearWeek(self): 
		timenow = datetime.datetime.now()  
		NowYearWeek = timenow.isocalendar()	 #(2017,44,4)
		return NowYearWeek	
		
	def getYearWeek(self,strdate):	
		date = datetime.datetime.strptime(strdate, '%Y-%m-%d')	
		YearWeek = date.isocalendar()  
		return YearWeek 
		
class Logger(object):
	def __init__(self, filename="Default.log"): 
		self.terminal = sys.stdout
		self.log = open(filename, "ab") #w-overwirte existing file,	 a- append

	def write(self, message):
		self.terminal.write(message)
		self.log.write(message)

	def flush(self):
		pass


def usageInfo():
	str="Usage:\tExportCoverity -f user -a password  -l link -d logdir\
		\n"
	return str
	
def getUsagePara():
	mUser=None
	mapplId=None
	mdateAfter=None   #reuse for logdir
	mlink=None
	try:
		opts, args = getopt.getopt(sys.argv[1:],"hf:a:l:d:",["user=","password=","link=","logdir="])
	except getopt.GetoptError:
		print  usageInfo()
		sys.exit(2)
	#print opts, args
	for opt, arg in opts:
		if opt == '-h':
			print usageInfo()
			sys.exit()
		elif opt in ("-f", "--user"):
			mUser = arg
		elif opt in ("-a", "--password"):
			mapplId = arg
		elif opt in ("-d", "--logdir"):
			mdateAfter=arg
		elif opt in ("-l", "link"):
			mlink=arg

	#print mUser,mapplId
	if mUser==None:
		print  usageInfo()
		sys.exit(3)
	return mUser,mapplId,mlink,mdateAfter
			  


				

# Get date list from begin_date to end_date
def get_date_list(begin_date, end_date):#e.g. get_date_list('2018-01-01','2018-02-28')
	dates = []
	# Get the time tuple : dt    
	dt = datetime.datetime.strptime(begin_date,"%Y-%m-%d")
	dt_end_date=datetime.datetime.strptime(end_date,"%Y-%m-%d")

	date = begin_date[:]
	#print date, dt_end_date
	#import pdb; pdb.set_trace()
	while dt <= dt_end_date:
		#if dt.strftime("%w") in ["1","2","3","4","5"]:# 获取起止日期时间段的所有工作日 (周一到周五)                     
		dates.append(date)
		dt += datetime.timedelta(days=1)
		date = dt.strftime("%Y-%m-%d")
	print dates
	return dates
	
	
class Homework:
	driver=None
	def __init__(self, filename="Default.log"): 
		import sys
		#print sys.getdefaultencoding()
		reload(sys)
		sys.setdefaultencoding( "utf8" )  #otherwise , get error "'ascii' codec can't encode characters in position 179-181: ordinal not in range(128)"
		#sys.setdefaultencoding( "gbk" )  #otherwise , get error "'ascii' codec can't encode characters in position 179-181: ordinal not in range(128)"
		(year,week,day)=Time_p().getNowYearWeek() #(2017,44,4)
		sys.stdout = Logger(str(year)+str(week)+"_Homework.log")  #private class , to write file and stdout
		print "=========Start at "+ datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") +"============="

		pass
	
	def enable_download_in_headless_chrome(self, browser, download_dir):
		#add missing support for chrome "send_command"  to selenium webdriver
		browser.command_executor._commands["send_command"] = ("POST", '/session/$sessionId/chromium/send_command')

		params = {'cmd': 'Page.setDownloadBehavior', 'params': {'behavior': 'allow', 'downloadPath': download_dir}}
		browser.execute("send_command", params)
		
	def initChrome(self,chromepath, log_filename,dir):
		chrome_options = Options()
		chrome_options.add_argument('--headless')
		chrome_options.add_argument('--disable-gpu')
		chrome_options.add_argument('--no-sandbox')
		chrome_options.add_argument('user-data-dir='+log_dir)


		#prefs = {, ,'safebrowsing.enabled':True,'browser.set_download_behavior.behavior': 'allow' }

		prefs = {'download.prompt_for_download': False,
					 'download.directory_upgrade': True,
					 'profile.default_content_settings.popups': 0,
					 'safebrowsing.enabled': True,
					 'safebrowsing.disable_download_protection': True}
		chrome_options.add_experimental_option('prefs', prefs) 


		self.driver = webdriver.Chrome(chrome_options=chrome_options,service_args=["--verbose", "--log-path="+log_filename])
		wait = WebDriverWait(self.driver, 10)

		self.enable_download_in_headless_chrome(self.driver, dir)
		
	def login(self, url,username,password):
		print "start to login..."
		x=self.driver.get(url=url)
		self.driver.find_element_by_id('ctl00_ContentPlaceHolder1_txtUserName').send_keys(username)
		self.driver.find_element_by_id('ctl00_ContentPlaceHolder1_txtPwd').send_keys(password)

		s=self.driver.find_element_by_id('ctl00_ContentPlaceHolder1_ddlType')
		Select(s).select_by_visible_text("学生")
		time.sleep(2)

		self.driver.save_screenshot("save_0.png")
		self.driver.find_element_by_id('ctl00_ContentPlaceHolder1_imgbtnlogin').click()
		time.sleep(5)
		self.driver.save_screenshot("save_1.png")
	
	def downloadPage(self, year, month, day):
		baseurl="http://zd.sharegreat.cn/exy/FWeb/SchoolWeb/StudentBag/StudentHomeWork.aspx?StudentID=yourstudentid&pdate="
		url2=baseurl+str(year) +'/'+str(month) +'/'+str(day)
		print 'start to downloading '+ url2
		self.driver.get(url=url2)
		time.sleep(15)
		self.driver.save_screenshot("save_2_"+str(day)+".png")
		html=self.driver.page_source
		#import pdb;pdb.set_trace()
		s="未布置"
		if s in html:
			return
		dir=str(year)+'_'+str(month)+'_'+str(day)
		if not os.path.exists(dir):
			os.mkdir(dir)
		filename=dir+'\index.html'
		f=open(filename,'wb')
		f.write(html)
		f.close
		self.getHomework(filename, dir)
	
	def getHomework(self,f,dir):
		doc=pq(filename=f, parser="html",encoding='utf8')
		homework= doc('.homework a')
		for i in homework.items():
			x=i.attr('href')
			if ((x!= None) and (x!='#')):
				y=x.encode('latin1').decode('utf8')
				#print y
				t=y.split('/')
				for i in t:
					tt=i
				print tt
				cmd=' wget --restrict-file-names=nocontrol -O '+dir+'\\tmpfile "'+y+'"'				
				#cmd1=cmd.encode('latin1').decode('utf8')  #pyquery default use latin1, something like ascii
				self.wgetfile(cmd,dir,tt)
				time.sleep(5)
			
	def wgetfile(self,cmd,dir, filename):
		try:
			#import pdb;pdb.set_trace()
			print cmd
			s=subprocess.call(cmd, shell=True)
			if s!=0:
				print 'error when doing '+ cmd
			else:
				print "success in " + cmd
				src=dir+'\\tmpfile'
				dst=dir+'\\'+filename
				print "move file from "+src, "to",dst
				if os.path.exists(dst):
					pass
				else:
					print os.rename(src,dst)
		except Exception as e:
			print 'FAIL with ' + e.message
			print traceback.print_exc()
			print traceback.format_exc()
			pass
			
	def downloadAll(self, begin_date,end_date):
		print "Start to download from "+begin_date+" to "+end_date
		datelist=get_date_list( begin_date,end_date)
		for i in datelist:
			print "===>working for " + i
			(y,m,d)=i.split('-')
			dy=int(y)
			dm=int(m)
			dd=int(d)
			self.downloadPage(dy,dm,dd)
		pass
		
		
	def close(self):
		self.driver.close()
		self.driver.quit()
		
if __name__ == "__main__":

	url="http://zd.sharegreat.cn/exy/FWeb/SchoolWeb/StudentBag/StudentHomeWork.aspx"
	username='username'
	password='password'
	log_dir='D:\prg\selenium\getHomework\log'      #must be created first

	#(username,password,url, log_dir)=getUsagePara()
	#print "your input is :", username,password,url,log_dir

	if log_dir==None:
		log_dir='D:\prg\selenium\getHomework\log'
	dir=log_dir+'\download'
	chromepath='D:\prg\selenium'
	log_filename=log_dir+'\chrome.log'
	
	#if 2>1:
	try:
		homework=Homework()
		homework.initChrome(chromepath,log_filename,dir)
		homework.login(url,username,password)
		#homework.downloadPage(2018,9,7)
		#homework.getHomework('2018_9_7\index.html','2018_9_7')
		homework.downloadAll('2019-1-1','2019-2-2')
	except Exception,e:
		print "Get exception with "+ e.message.encode("GBK","ignore")
		print traceback.print_exc()
		print traceback.format_exc()
	finally:
		homework.close()