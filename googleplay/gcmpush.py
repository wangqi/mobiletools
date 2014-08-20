#!/usr/local/bin/python3.3 
# -*- coding: utf8 -*-

from time import strftime,gmtime,time
import boto.sns, json, sys, csv
#import MySQLdb
from boto.sns import SNSConnection

##################################################################
# 
# By using the URI interface to push message to AWS service.
# Message format:
#
#  { "GCM":"{\"data\":{\"default\":\"<content>\", \"title\":\"<title>\"}}" }
#
# export AWS_ACCESS_KEY_ID=ua937U9kiGh/cBTXlBoCMb9z0+b5IRyYJ8/Ie0vD
# export AWS_SECRET_ACCESS_KEY=AKIAJOW7H3KCZ76YKOMA
#
##################################################################
def connect_sns(region, aws_keyid, aws_accesskey):
	conn = boto.sns.connect_to_region(region, 
		aws_access_key_id=aws_keyid, 
		aws_secret_access_key=aws_accesskey,debug=0)
	return conn

##################################################################
#
# Add an endpoint before publishing
#
##################################################################
def add_endpoint(conn, app_arn, token, uid):
	try:
		endpoint = conn.create_platform_endpoint(platform_application_arn=app_arn, token=token, custom_user_data=uid)
		#print(endpoint)
		return endpoint
	except:
		print("Failed to add endpoint for uid: " + uid)

##################################################################
# 
# Publish a single message to an endpoint.
#
##################################################################
def publish(conn, subject, endpoint, msg, var):
	if var != None:
		msg = msg.format(*var)
	#print(msg)
	try:
		conn.publish(message=msg,
			target_arn=endpoint['CreatePlatformEndpointResponse']['CreatePlatformEndpointResult']['EndpointArn']
			, message_structure='json')
	except Exception as err:
		print('failed to send to endpoint:{}', endpoint)

##################################################################
# 
# Read user list from the data file. The file has the following format
#  uid, token, username ...
# The fields after token will be used to format the message content
#
##################################################################
def read_user(userfile):
	users = dict()
	for row in csv.reader(open(userfile, 'rU'), delimiter=','):
		if len(row) < 2:
			continue
		token = row[0]
		uid = row[1]
		variables=list()
		if len(row)>2:
			variables=row[2:]
		userdict = {}
		userdict['uid'] = uid
		userdict['var'] = variables
		users[token] = userdict
	#print(users)
	return users

##################################################################
# 
# Read user list from the database
#
##################################################################
def read_user_db(mysql_host, mysql_user, mysql_pass, mysql_db, mysql_query):
	try:
		users = dict()
		conn=MySQLdb.connect(host=mysql_host,user=mysql_user,passwd=mysql_pass,port=3306)
		cur=conn.cursor()
		conn.select_db(mysql_db)
		count=cur.execute(mysql_query)
		print('there has %s rows record' % count)

		results=cur.fetchall()
		for r in results:
			token = r[0]
			uid =  r[1]
			nickname = r[2]
			variables=[nickname]
			userdict = {}
			userdict['uid'] = uid
			userdict['var'] = variables
			users[token] = userdict
			print(users)
		return users
	except Exception as err:
		print("Mysql query error: %s"%err)

###########################################################
# Read the aws config file and push config file to prepare 
# pushing.
#   select nickname, uid, login_time, init_time, pushtoken
#   from user u, push_token p
#   where u.gid = p.uid
#   and p.uid = '316779620332537'
###########################################################
if __name__ == "__main__":
	reload(sys)
	sys.setdefaultencoding('utf8')
	if len(sys.argv) < 4:
		print('Usage: <configfile> <messagefile> <datafile>')
		sys.exit(-1)
	configfile = sys.argv[1]
	messagefile = sys.argv[2]
	datafile = sys.argv[3]
	readFromFile = True
	if datafile == '--mysql':
		readFromFile = False
	with open(configfile, 'r') as awsfile:
		awsconfig = json.load(awsfile)
	subject = awsconfig.get('aws_subject')
	aws_topic_arn = awsconfig.get('aws_topic_arn')
	aws_keyid = awsconfig.get('aws_keyid')
	aws_region = awsconfig.get('aws_region')
	aws_accesskey = awsconfig.get('aws_accesskey')
	mysql_host = awsconfig.get('mysql_host')
	mysql_user = awsconfig.get('mysql_user')
	mysql_pass = awsconfig.get('mysql_pass')
	mysql_db = awsconfig.get('mysql_db')
	mysql_query = awsconfig.get('mysql_query')
	debug = awsconfig.get('debug')
	print('-- aws config ---')
	print('aws_topic_arn:\t%s '%aws_topic_arn)
	print('aws_region:\t%s '%aws_region)
	print('aws_keyid:\t%s '%aws_keyid)
	print('aws_accesskey:\t%s '%aws_accesskey)
	print('mysql_host:\t%s '%mysql_host)
	print('mysql_user:\t%s '%mysql_user)
	print('mysql_pass:\t%s '%mysql_pass)
	print('mysql_db:\t%s '%mysql_db)
	print('mysql_query:\t%s '%mysql_query)
	print('debug:\t%s '%debug)
	
	boto.set_stream_logger('push')

	with open(messagefile, 'r') as msgfile:
		msgconfig = json.load(msgfile)
	title = msgconfig.get('title')
	message = msgconfig.get('message')
	print('title:\t%s'%title)
	print('message:\t%s'%message)
	
	message = u'{{"GCM":"{{\\"data\\":{{\\"default\\":\\"%s\\", \\"title\\":\\"%s\\"}}}}"}}' % (message,title)
	if readFromFile:
		users = read_user(datafile)
	else:
		users = read_user_db(mysql_host, mysql_user, mysql_pass, mysql_db, mysql_query)
	conn = connect_sns(aws_region, aws_keyid, aws_accesskey)
	line = 0
	for token in users.keys():
		userdict = users.get(token)
		uid = userdict.get('uid')
		var = userdict.get('var')
		print('token={0},uid={1}'.format(token,uid))
		endpoint = add_endpoint(conn, aws_topic_arn, token, uid)
		publish(conn, 'Subject', endpoint, message, var)
		line+=1
		print("line:%s, uid:%s"%(line,uid))



