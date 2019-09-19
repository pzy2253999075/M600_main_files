from kafka import KafkaProducer
from kafka.errors import KafkaError
from kafka import KafkaConsumer
import cv2
import threading 
from fdfs_client.client import *
import base64
import httplib
import urllib
import json
import requests
import sys
import signal
import mmap
import os
import time



class KafkaUpload():
	def __init__(self,filepath):
		self.init_mmap()
		#self.mbootstrap_servers = mbootstrap_servers
		#self.myJson = {}
		self.saveone = True
		#self.readPathLoopFlag = True
		self.readFilePathLoopThread(filepath)
	

	def init_mmap(self):
		self.mmapPath = "/home/dji/DJI_Onboard_Sdk/src/Onboard-SDK-ROS/dji_sdk/scripts/mmap_info.txt"
		self.fileSize = os.path.getsize(self.mmapPath)
		self.myMmap = mmap.mmap(os.open(self.mmapPath,os.O_RDWR),self.fileSize)
		self.pushcount = 0

	def getVauleFromMmap(self):
  		self.myMmap.seek(self.myMmap.find("kafka",0)+len("kafka")+1)
  		temp = self.myMmap.read(1)
  		return int(temp)


	def setValueToMmap(self,value):
  		self.myMmap.seek(self.myMmap.find("kafka",0)+len("kafka")+1)
  		self.myMmap.write(str(value))
		


	#def init_fdfs_client(self):
	#	self.fdfs_client = Fdfs_client('/etc/fdfs/client.conf.sample')
	

	#def fdfs_upload_by_file(self,path):
	#	ret = self.fdfs_client.upload_by_filename(path)
	#	return ret['Remote file_id']
		

	def imageToBase64(self,filepath):
		try:
			with open(filepath,'rb') as f:
				base64_str = base64.b64encode(f.read())
				return base64_str
		except Exception as e:
			print("fail to read picture")
			print(e)
			return 0

	
	#def testKafka(self,filename):
	#	re = self.imageToBase64("./666.png")
	#	temp  =  {"picture":"dwadad"}
	#	#self.send_kafka_message(temp)
	#	self.httpUpload("http://172.31.226.82:8004/plep/api/kafka/send/push_warning",temp)

	#def init_kafka_producer(self):
	#	self.producer  = KafkaProducer(
	#		bootstrap_servers = self.mbootstrap_servers
	#		#compression_type = "snappy"
	#	)
	#	self.pro_topic = "plep"
	#	self.pro_key = "push_warning"
		

	#def send_kafka_message(self,mvalue):
	#	try:
	#		self.producer.send(topic = b'plep',value = b'dw13854aw',key = b'push_warning')
	#		#record_metadata =  future.get(timeout = 10)
	#		#print (record_metadata)
	#		print("succeed")
	#	except KafkaError as e:
	#		#print (e+"faile to push kafka  "+mvalue)
	#		pass

	#def init_kafka_consumer(self):
	#	self.consumer = KafkaConsumer(
	#		bootstrap_server = self.mbootstrap_servers,
	#		group_id = "test"
	#	)
	#	self.consumer.subscribe(topics = [self.pro_topic])
		

	def kafkaPush(self,filepath):
		res = self.readJson(filepath+'.json')
		if(res == 1):	
			pictureBUpload = self.imageToBase64(filepath+'_B.jpg')
			pictureNUpload = self.imageToBase64(filepath+'_N.jpg')
			if(pictureBUpload is not 0 and pictureNUpload is not 0):
				self.myJson["Image_Stream_B"] = pictureBUpload
				self.myJson["Image_Stream_N"] = pictureNUpload
				self.httpUpload(sys.argv[2],self.myJson,filepath,3)
			else:
				pass
		elif(res == 0):
			pictureNUpload = self.imageToBase64(filepath+'_N.jpg')
			if (pictureNUpload is not 0):
				#print(pictureNUpload)
				self.myJson["Image_Stream_N"] = pictureNUpload
				self.httpUpload(sys.argv[2],self.myJson,filepath,2)
			else:
				pass			
		elif(res == 2):
			pass
			

	
	def readJson(self,filepath):
		with open (filepath,mode = 'r') as f:
			try:
				getValue  = json.load(f)
			except ValueError as e:
				print("value error **********")
				return 2
			self.myJson = getValue
			if(self.myJson.has_key("Image_Stream_B")):
				return 1
			else:
				return 0
	


	def httpUpload(self,url,data,path_to_rm,rmTag):
		#print(data)
		try:
			response = requests.post(url,data = json.dumps(data).encode(),
			headers = {'Content-type':'application/json'},timeout = 10)
			if(response is not None):
				#if (self.saveone):
				#self.count = self.count +1
				#f = open('./test'+str(self.count)+'.txt',"a")
				#f.write(json.dumps(data).encode())
				#f.close()
				#self.saveone = False
				my_response = response.text.encode('utf-8')
				my_response = json.loads(my_response)
				if  my_response['success'] == True:
					print(my_response)
					#self.count = self.count+1
					self.removeFile(path_to_rm,rmTag)
					print("http post succeed")
					self.pushcount+=1
				else:
					print("fail to post http request")

		except requests.exceptions.ConnectTimeout as e:
			print(e)
			print("*******connectionTimeout******please check your network health or url is right")
		
		except requests.exceptions.ConnectionError as e:
			print(e)
			print("********connectionError*******")
		time.sleep(30)
		

	def removeFile(self,filepath,params):
		if params  == 3:
			os.remove(filepath+'.json')
			os.remove(filepath+'_B.jpg')
			os.remove(filepath+'_N.jpg')
		elif params == 2:
			os.remove(filepath+'.json')
			os.remove(filepath+'_N.jpg')


	def readFilePathLoopThread(self,filepath):
		self.m_thread = threading.Thread(target = self.readFilePathLoop,args = (filepath,))
		self.m_thread.start()
		self.m_thread.join()
		self.setValueToMmap(4)
		f = open("pushcount.txt", "a")
		f.writelines(str(self.pushcount)+'\n')
		f.close()		


	def joinMyThread(self):
		self.m_thread.join()


	def readFilePathLoop(self,filepath):
		self.setValueToMmap(2)
		self.count = 0
		while(True):
			if(self.getVauleFromMmap() == 3):
				break
			files = os.listdir(filepath)
			if len(files) is 0:
				continue
			for mfile in files:
				if  os.path.splitext(mfile)[1] == '.json':
					self.kafkaPush(filepath+'/'+os.path.splitext(mfile)[0])
					#if self.count == 10:
						#return;	
						



if __name__ == "__main__":
	mKafkaUpload = KafkaUpload(sys.argv[1])
	#kafkaTest.joinMyThread()
	































































































