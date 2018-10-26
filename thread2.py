#!/usr/bin/python
# -*- coding:utf-8 -*-

import time
from time import ctime
import threading,thread
import re
import mysql.connector as con



def splitFile(fileLocation, targetFoler):
	file_handler = open(fileLocation, 'r')
	num=5000000
	countFile = 0
	i=0
	while True:
		line =file_handler.readline()
		if not line:
        	       	break
		countFile = countFile + 1
		file_writer = open(targetFoler + 'file_'+str(countFile)+'.txt', 'a+')
		file_writer.writelines(line)
		while i<num:
			file_writer.writelines(file_handler.readline())
			i+=1
		file_writer.close()
		print 'file ' + str(countFile) + ' generated at: '+ str(ctime())
		i=0
	file_handler.close()
	return countFile
class myThread(threading.Thread):
	flag1=False
	flag2=False
	def __init__(self, threadName, name,lock):
		threading.Thread.__init__(self)
		self.threadName = threadName
		self.name = name
		self.lock=lock

	def run(self):  
		print "Starting " + self.threadName
		index=0
		l1=r"-([0-9a-z!.]+)-', <function ([0-9a-zA-Z]+)"
		l2=r"T]', ([0-9][.][0-9]*)"
		l3=r".*line [0-9]+, in ([a-zA-Z]+)\\n.*"
		list1=[]
		i=j=0
		trace=[]
		try:
			conn = con.connect(user='root',password='root',database='test1',use_unicode=True)
                	cursor =conn.cursor()
                	log=open(self.name)
			for line in log:
				#匹配CallBack结果
				found1=re.findall(l1,line)
				#匹配[T]结果
				found2=re.findall(l2,line)
				#匹配Traceback
#				found3=re.findall(l3,line)
				#找到CallBack所在行数
				if found1 != None and len(found1) !=0:
					if i-j==0:
						index =index+1
						i+=1;
						list1.append(found1)
				#匹配到[T]
				if found2 != None and len(found2) !=0:
					if i-j==1:
						index =index+1
						j+=1
						list1.append(found2)
				# 匹配到Traceback
				if "Traceback" in line:
					found=re.findall(l3,line)
					if found !=None and len(found)!=0:
						# 将错误信息放到list中追加到t列表
						text=line[30:-3]
						if len(text)>5000000:
 	                                               continue
                                                trace.append([found[0],1,text])
                        lock.acquire()
			# 批量插入错误信息
                        cursor.executemany('insert into error (f_name,f_time,cont) values (%s,%s,%s)on duplicate key update f_time=f_time+1',trace)
                        conn.commit()
                        lock.release()
			temp=[]
			if len(list1)%2==0: 
                        	for l in range(0,len(list1),2):
                        		li=list(list1[l])
                               		temp.append([li[0][1]]+list1[l+1])
			else:
				for l in range(0,len(list1)-1,2):
                                        li=list(list1[l])
                                        temp.append([li[0][1]]+list1[l+1])
			cursor.executemany("insert into temp (f_name,f_time) value(%s,%s)",temp)
			conn.commit()
			print 'Exist....'+self.threadName
		except Exception,e:
			print 'error'
		finally:
			cursor.close()
if __name__ == '__main__':
	print 'Start At: ' + str(ctime())
	result=splitFile('./2018-08-12.log', './test/')
	lock = thread.allocate_lock()
	threads = []
	for i in range(result):
		fileName='./test/file_'+str(i+1)+'.txt'
		threads.append(myThread('Thread'+str(i), fileName,lock))
	for t in threads:
		t.start()
	for t in threads:
		t.join()
	conn = con.connect(user='root',password='root',database='test1',use_unicode=True)
	cursor =conn.cursor()
	cursor.execute("select count(*) from temp")
	tote=cursor.fetchone()
	cursor.execute("select f_name,max(f_time),min(f_time),count(*)/%s as port,count(*),sum(f_time)/count(*),sum(f_time) from temp group by f_name",(tote[0],))
	tup=cursor.fetchall()
	cursor.executemany("insert into time (f_name,f_maxtime,f_mintime,f_port,f_num,f_avgtime,f_time) value(%s,%s,%s,%s,%s,%s,%s)",tup)
	conn.commit()
	cursor.close()
	print 'End At: ' + str(ctime())
	print "MainThread Exit..............."

	print("111111111111111111111111111111")
