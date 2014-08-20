#!/usr/bin/python3
# -*- coding: utf-8 -*-

#################################################################################
#   Parse the IOS ranking html page.
#################################################################################

import glob
import io, sys, traceback
import json, math, csv
from bs4 import BeautifulSoup
import time
from datetime import datetime, date, timedelta

class App:
	name = ''
	publisher = ''
	rank = 0
	ranktype = ''
	href = ''

	def __init__(self, name, publisher, rank, ranktype, href):
		self.name = name
		self.publisher = publisher
		self.rank = rank
		self.ranktype = ranktype
		self.href = href

	def __str__(self):
		return "{0}\t{1}\t{2}\t{3}\t{4}".format(self.ranktype, self.rank, self.name, self.publisher, self.href)

#
# Every 'tr' element contains information about an app, which includes
#  the rank, name and publisher. 
# 
def parsetr(rank, tr):
	types = ['免费','收费','营收']
	index = 0
	apps = []
	for td in tr.find_all('td'):
		ranktype = types[index%3]
		span = td.find('span', class_='title-info')
		href = span.a['href']
		name = span['title']
		span = td.find('span', class_='add-info')
		publisher = span['title']
		#if ranktype == '营收':
		#	apps.append(App(name, publisher, rank, ranktype, href))
		apps.append(App(name, publisher, rank, ranktype, href))
		index+=1
	return apps

#
# Parse the whole html
#
def parsehtml(day, file):
	with open(file, 'r') as f:
		content = BeautifulSoup(f.read())
	table = content.find('tbody', id='storestats-top-table')
	rank = 0
	with open('iosrank.txt', 'a') as file:
		for tr in table.find_all('tr'):
			rank += 1
			apps = parsetr(rank,tr)
			for app in apps:
				print(day, app, sep='\t', file=file)


if __name__ == "__main__":
	if len(sys.argv) < 1:
		print("Usage: <dir>")
		sys.exit(-1)
	dir = sys.argv[1]
	files = glob.glob(dir + "/*.html")
	try:
		for file in files:
			day = file[-15:-5]
			print(file)
			parsehtml(day, file)
	except Exception as err:
		print("Error process file: " + file)
		print(err)

