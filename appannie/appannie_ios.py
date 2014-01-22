#!/usr/bin/python3
# -*- coding: utf-8 -*-

#################################################################################
#   Download the IOS Top list for a given country at given period
#   For example, 
#        ./appannie_ios_grossing.py china 2013-01-01 2014-01-01
#   will download all the top 100 app in China between 2013-01-01 and 2014-01-01
#################################################################################

import requests
import io, sys, traceback
import json, math, csv
#from bs4 import BeautifulSoup
import time
from datetime import datetime, date, timedelta

headers  = {
    'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1700.19 Safari/537.36 OPR/19.0.1326.9 (Edition Next)",
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Encoding': 'gzip,deflate,sdch'
}

#
# Login AppAnnie with given user account
#
def login(cookie):
	session = requests.Session()
	#session.get('http://www.appannie.com/account/login/', headers=headers)
	#payload = {"username": username, "password": password, "remember_user":'on', "next":'/apps/ios/top/china/overall/?device=iphone'}
	#r = session.post("http://www.appannie.com/account/login/", data=payload, headers=headers, allow_redirects=True)
	session.headers.update({'cookie': cookie})
	return session;

#
# Download the IOS grossing list for given country
# 
def ios_grossing(session, country, startdate, enddate):
	day = startdate
	while (day < enddate):
		try:
			daystr = datetime.strftime(day, '%Y-%m-%d')
			url = "http://www.appannie.com/apps/ios/top/{0}/overall/?device=iphone&date={1}".format(country, daystr)
			print(url)
			r = session.get(url, headers=headers)
			filename = country + '-' + daystr + '.html'
			#output the html
			with open(filename, 'w') as f:
				print(r.text, file=f)
			day = day + timedelta(days=1)
			if r.status_code != 200 :
				print("Failed to read content. 503 error")
				sys.exit(-1)
			time.sleep(10)
		except:
			print("Error to access url: " + url)

if __name__ == "__main__":
	if len(sys.argv) < 4:
		print("Usage: <cookiefile> <country> <start-date> <end-date")
		sys.exit(-1)
	cookiefile = sys.argv[1]
	country = sys.argv[2]
	startdate = datetime.strptime(sys.argv[3], '%Y-%m-%d')
	enddate = datetime.strptime(sys.argv[4], '%Y-%m-%d')
	print("country: {}, startdate:{}, enddate:{}".format(country, startdate, enddate))
	with open(cookiefile, 'r') as cookiefile:
		content = cookiefile.read()
	session = login(content)
	ios_grossing(session, country, startdate, enddate)
