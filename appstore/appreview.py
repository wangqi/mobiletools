# -*- coding: utf-8 -*-
# 
# It is a small tool to download the AppStore's user reviews.
# 
import requests
import io, sys, traceback
import json, math, csv
from bs4 import BeautifulSoup
from datetime import datetime, date, time

headers  = {
    'User-Agent': "iTunes/11.1.3 (Macintosh; OS X 10.9.1) AppleWebKit/537.73.11",
    'X-Apple-Store-Front': '143465-2,17'
}

# The app review dictionary
app_review = dict()
#app_review_list = []
log_path = '.'

#
# List all the user reviews.
# 
# The following url will list the current version's reviews
#   https://itunes.apple.com/cn/customer-reviews/id710390597?dataOnly=true&displayable-kind=11&l=en&appVersion=current
#
# The following url will list all the version's reviews
#   https://itunes.apple.com/cn/customer-reviews/id710390597?dataOnly=true&displayable-kind=11&l=en&appVersion=all
#
def listsummary(appid):
	url = "https://itunes.apple.com/cn/customer-reviews/id{0}?dataOnly=true&displayable-kind=11&l=en&appVersion=all"
	url = url.format(appid)
	try:
		response = requests.get(url,headers=headers)
		response.encoding='utf8'
		json = response.json()
		# The total count of rating
		app_review['ratingCount'] = json.get('ratingCount')
		# The total count of reviews
		totalReview = json.get('totalNumberOfReviews')
		app_review['totalNumberOfReviews'] = totalReview
		# "ratingCountList": [
        #   127, 
        #   21, 
        #   42, 
        #   121, 
        #   2075
    	# ], 
		app_review['ratingCountList'] = json.get('ratingCountList')
		app_review['ratingAverage'] = json.get('ratingAverage')
		print(app_review)
		listreviews(appid, totalReview);
	except:
		print("The given appid {} is not found in iTunes Store".format(appid))

# Get the total reviews' list
#   https://itunes.apple.com/WebObjects/MZStore.woa/wa/userReviewsRow?id=710390597&displayable-kind=11&startIndex=0&endIndex=100&sort=1&appVersion=all
def listreviews(appid, total=100):
	if total == 0:
		return
	page = math.ceil(total/100)
	start = 0
	end = 100
	with open(log_path + '/review.csv', 'w') as outfile:
		for i in range(1, page+1):
			url = "https://itunes.apple.com/WebObjects/MZStore.woa/wa/userReviewsRow?id={0}&displayable-kind=11&startIndex={1}&endIndex={2}&sort=1&appVersion=all"
			url = url.format(appid, start, end)
			print("start:{}, end:{}, url:{}".format(start, end, url))
			try:
				response = requests.get(url, headers=headers)
				response.encoding='utf8'
				json = response.json()
				userReviewList = json.get("userReviewList")
				for review in userReviewList:
					try:
						r = dict()
						r['userReviewId'] = review.get('userReviewId')
						pubdate = review.get('date')
						pubdate = datetime.strptime(pubdate, '%Y-%m-%dT%H:%M:%SZ').strftime('%Y-%m-%d')
						r['date'] = pubdate
						r['name'] = review.get('name')
						r['rating'] = review.get('rating')
						r['title'] = review.get('title')
						r['voteCount'] = review.get('voteCount')
						r['body'] = review.get('body')
						reviewUrl = review.get('viewUsersUserReviewsUrl')
						userId = reviewUrl.split('=')[-1]
						userstat = getuserprofile(userId, r['name'], reviewUrl)
						#app_review_list.append(r)
						print(r['userReviewId'], r['date'], userId, r['name'], r['rating'], r['voteCount'], 
							r['title'], r['body'], userstat.get('publisher_count'), userstat.get('5star'), sep='\t', file=outfile)
						outfile.flush()
					except:
						print("Error to read review from: ", review)
						sys.exit(-1)
			except:
				print("Error to read the reviews for {}".format(appid))
			start = i*100+i
			end = min(total, (i+1)*100+i)
			if start >= end:
				break;

#
# Get the user's rating history
# 
def getuserprofile(reviewid, name, url):
	response = requests.get(url, headers=headers)
	response.encoding='utf8'
	soap = BeautifulSoup(response.text)
	mainblocks = soap.find_all('div', class_='main-block')
	stat = dict()
	stat['5star'] = 0
	publisher = set()
	with open(log_path + '/userreview.csv', 'a') as outfile: 
		for mainblock in mainblocks:
			try:
				div = mainblock.find('div', attrs={'adam-id':True})
				gamename = div.get('aria-label')
				artist = div.find('li', class_='artist')
				if artist != None:
					artist = artist.a.text
					publisher.add(artist)
				star = mainblock.find('div', class_='rating')['aria-label'][0]
				if star == '5':
					stat['5star'] = stat.get('5star') + 1
				reviewdate = mainblock.find('div', class_='review-date').text.strip()
				reviewdate = datetime.strptime(reviewdate, '%d %B %Y').strftime('%Y-%m-%d')
				print(reviewid, name, gamename, star, reviewdate, artist, sep='\t', file=outfile)
				outfile.flush()
			except Exception as err:
				print("Error to get user profile info: ", err)
	count = len(publisher)
	stat['publisher_count'] = count
	#print(stat)
	return stat


if __name__ == "__main__":
	if len(sys.argv) <= 1:
		print("You should specify a appid.")
		sys.exit(1)
	appid = sys.argv[1]
	listsummary(appid)
	#getuserprofile(1111, 'test', 'https://itunes.apple.com/cn/reviews?l=en&userProfileId=203495688')
