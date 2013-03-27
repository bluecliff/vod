#!/usr/bin/python
#coding:utf-8

import urllib
from xml.dom import minidom
import os
import codecs
import re
import sys



class vod:
	def __init__(self):
		self.host="http://10.168.200.1/"
		self.totalxmlpath="mov/xml/"
		self.totalxml="Total.xml"
		self.filmurl="url.xml"
		self.mov="mov/"
		self.query="return.asp?info="

	def findByName(self,film):
		"""通过影片名等正规式找匹配的电影"""
		totalinfo=self.loadTotalXml()
		#film=film.decode()
		#pattern=re.compile(film)
		filmlist=[]
		for line in totalinfo:
			if re.search(film,line):
				filmlist.append(line)
		totalinfo.close()
		return filmlist


	def loadTotalXml(self):
		"""加载Total.xml"""
		if os.path.exists(self.totalxmlpath):
			pass
		else:
			os.makedirs(self.totalxmlpath)

		if os.path.exists(self.totalxmlpath+self.totalxml):
			pass
		else:
			remote=self.getURL(self.host+self.totalxmlpath+self.totalxml)
			local=codecs.open(self.totalxmlpath+self.totalxml,'w','utf-16')
			for line in remote.readlines():
				try:
					local.write(line.decode('gb2312'))
				except UnicodeDecodeError:
					continue
			remote.close()
			local.close()
		return codecs.open(self.totalxmlpath+self.totalxml,'r','utf-16')

	def getURL(self,xmlurl):
		"""获取url对象"""
		return urllib.urlopen(xmlurl)

	def getFilmList(self,filmname):
		"""根据给定的filmname对象获取该电影的所有集的hashname列表
			filmname是一个字符串对象，是Total.xml中的一项
		"""
		pattern=u'<b>.*</b>'
		res=re.search(pattern,filmname,re.S)
		if res:
			(beg,end)=res.span()
			#filmhash=filmname.replace(temp,'')
			filmhash=filmname[beg+3:end-4]
			content=self.getURL(self.host+self.mov+filmhash+'/'+self.filmurl).read().strip().decode('gb2312')
			res=re.search(pattern,content,re.S)
			if res:
				(beg,end)=res.span()
				content=content[beg+3:end-4]
				content=content.replace(u'\r\n',u'')
				hashlist=content.strip().strip(u',').split(u',')
				return hashlist
			else:
				return None

		else:
			return None
	
	def getFilmUrlList(self,hashlist):
		"""根据电影各集的hashname查找到各集对应的播放地址"""
		urllist=[]
		for item in hashlist:
			content=self.getURL(self.host+self.query+item).read().decode('gb2312')
			pattern=u'<url>.*</url>'
			res=re.search(pattern,content,re.S)
			if res:
				(beg,end)=res.span()
				url=content[beg+5:end-6]
				pattern=u'.*//.*?/'
				urllist.append(re.sub(pattern,self.host,url))
		return urllist

	def getFilmName(self,film):
		"""从info列表中取出影片名字"""
		pattern=u"<a>.*?</a>"
		res=re.search(pattern,film,re.S)
		if res:
			(beg,end)=res.span()
			return film[beg:end]

if __name__ == "__main__":
	reload(sys)
	sys.setdefaultencoding('utf-8')
	filmname=sys.argv[1].decode()
	v=vod()
	v.loadTotalXml()	
	filmlist=v.findByName(filmname)
	i=0
	if len(filmlist)==0:
		print "No this film"
		sys.exit()
	for film in filmlist:
		print i, v.getFilmName(film)
		i+=1
	i=input("input the no:")
	s = v.getFilmList(filmlist[i])
	if len(s) ==0:
		print "fail to find the URL of this film"
	else:
		for item in v.getFilmUrlList(s):
			if len(item)>0:
				print item
