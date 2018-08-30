# -*- coding: UTF-8 -*-
from urllib import request
from urllib import error
from urllib import parse
from http import cookiejar
from aip import AipOcr
from bs4 import BeautifulSoup
import re
import json
import time
import sys

class Robot(object):

	username = ''
	password = ''
	cookieFilename = 'cookie.txt'
	loginUrl = 'http://cas.teacher.com.cn/restLoginCheck'
	validateCodeUrl = 'http://sltyxw2017.w.px.teacher.com.cn/validateCode'
	userAgent = r'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.94 Safari/537.36'
	head = {'User-Agnet': userAgent, 'Connection': 'keep-alive'}
	host = 'http://sltyxw2017.w.px.teacher.com.cn'

	cookie = cookiejar.MozillaCookieJar(cookieFilename)
	
	cookie_support = request.HTTPCookieProcessor(cookie)
	opener = request.build_opener(cookie_support)

	APP_ID = '10140339'
	API_KEY = 'neoTgURPEEc2hxqWV00Tvq2S'
	SECRET_KEY = '******************************'
	aipOcr = AipOcr(APP_ID, API_KEY, SECRET_KEY)




	def __init__(self, username, password):

		self.username = username
		self.password = password
	def post(self, _url, _data = {}):
		self.cookie.load(self.cookieFilename, ignore_discard=True, ignore_expires=True)
		postData = parse.urlencode(_data).encode('utf-8')
		req = request.Request(url = _url, data = postData, headers = self.head)
		res = self.opener.open(req)
		self.cookie.save(ignore_discard=True, ignore_expires=True)
		return res.read()

	def get(self, url, querys = {}):
		self.cookie.load(self.cookieFilename, ignore_discard=True, ignore_expires=True)
		fullurl = url + "?" + parse.urlencode(querys)
		res = self.opener.open(fullurl)
		self.cookie.save(ignore_discard=True, ignore_expires=True)
		return res.read()
	def login(self):

		loginData = { 'username': self.username, 'password': self.password }
		return self.post(self.loginUrl, loginData)
	def index(self):
		return self.get('http://sltyxw2017.w.px.teacher.com.cn/home/student/130381')

	def validateCode(self):
		return self.get(self.validateCodeUrl)


	def getValidateCodeText(self, imgContent):
		return self.aipOcr.basicGeneral(imgContent)

	def getCourseList(self, indexHtml):
		soup = BeautifulSoup(indexHtml, "html.parser")
		results = []
		for link in soup.select("a.go"):
			href = link.get("href")
			if re.findall(r'.+/-2/.+', href):
				results.append(href)


		return results
	def getCourseDetailUrlByUrl(self, url):
		html = self.get(self.host + url).decode('utf-8')
		soup = BeautifulSoup(html, "html.parser")
		links = soup.select("a[target=frm_course_learn]");
		print(links)
		if not links:
			return None
		else:
			return links[0].get("href")

	def getCourseDetailInfo(self, url):
		html = self.get(self.host + url).decode('utf-8')
		id = re.findall(r'obj.id = (\d+);', html)[0]
		learningTime = int(re.findall(r'obj.learningTime=(\d+);', html)[0])
		courseId = re.findall(r'obj.courseId=(\d+);', html)[0]
		token = re.findall(r"var token='(\d+)'", html)[0]
		cumulativeTime = int(re.findall(r'value="(\d+)" id="cumulativeTime"', html)[0])
		return {
			"id": id,
			"courseId": courseId,
			"learningTime": learningTime,
			"token": token,
			"cumulativeTime": cumulativeTime
		}

	def updateTime(self, courseInfo):
		updateTimeUrl = 'http://sltyxw2017.w.px.teacher.com.cn/home/student/130381/course/updateLearnTime'
		upRes = self.post(updateTimeUrl, {
			"id":courseInfo["id"],
			"onceTime":20,
			"drawerId":courseInfo["courseId"],
			"validateType":"false",
			"token": courseInfo["token"]
		}).decode("utf-8")

		try:
			upRes = json.loads(upRes)
		except BaseException as e:
			print("[load json error]", e)
			upRes = {
				"error": upRes
			}
		return upRes


	def start(self):
		startTime = time.time();
		print("[LOGIN]", self.username)
		loginRes = self.login().decode('utf-8')
		print("[LOGIN RESULT]", loginRes)

		print("[ACTION]", "enter in the index page……")
		indexHtml = self.index().decode('utf-8')
		print("[ACTION]", "getting the course list……")
		courseUrlList = self.getCourseList(indexHtml)

		print("[ACTION]", "loop the course list to study one by one, skip finished……")

		for url in courseUrlList:
			detailUrl = self.getCourseDetailUrlByUrl(url)
			if detailUrl:

				print("[getting course info]", detailUrl)
				courseInfo = self.getCourseDetailInfo(detailUrl)
				print("[courseInfo result]", courseInfo)
				while courseInfo["cumulativeTime"] < courseInfo["learningTime"]:

					if time.time() - startTime > 60 * 60:
						startTime = time.time();
						print("[LOGIN]", self.username)
						loginRes = self.login().decode('utf-8')
						print("[LOGIN RESULT]", loginRes)

					print("[UPDATETIME start]", courseInfo)
					uptimeRes = self.updateTime(courseInfo)
					print("[UPDATETIME result]", uptimeRes)
					if uptimeRes.get("sum"):
						courseInfo["cumulativeTime"] = uptimeRes.get("sum")
						courseInfo["token"] = uptimeRes.get("token")
					else:
						print("[UPDATETIME Error]", uptimeRes["error"])
					print("[SLEEPING for 20 mins]……")
					secs = 0
					while secs < 1201:
						time.sleep(1)
						print ("\rsleep:", secs, " secs, live ", int(time.time() - startTime) , " secs from last login.", end = '')
						sys.stdout.flush()
						secs = secs + 1
					print("\n[WAKEUP]")


		print("[ALL DONE]!!!")

			





if __name__ == '__main__':
	robot = Robot('xaxp172959','******')

	robot.start()


		
