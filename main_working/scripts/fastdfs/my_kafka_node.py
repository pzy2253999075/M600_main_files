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
import rospy


class FileUpload():
	def __init__(self,mbootstrap_servers,filepath):
		self.mbootstrap_servers = mbootstrap_servers
		self.myJson = {}
		self.readPathLoopFlag = True
		self.readFilePathLoopThread(filepath)
		
	
	def initSubPub(self):
		self.	



	def init_fdfs_client(self):
		self.fdfs_client = Fdfs_client('/etc/fdfs/client.conf.sample')
	

	def fdfs_upload_by_file(self,path):
		ret = self.fdfs_client.upload_by_filename(path)
		return ret['Remote file_id']
		

	def imageToBase64(self,filepath):
		try:
			with open(filepath,'rb') as f:
				base64_str = base64.b64encode(f.read())
				return base64_str
		except Exception as e:
			print("fail to read picture")
			print(e)
			return 0

	
	def testKafka(self,filename):
		re = self.imageToBase64("./666.png")
		temp  =  {"picture":"dwadad"}
		#self.send_kafka_message(temp)
		self.httpUpload("http://172.31.226.82:8004/plep/api/kafka/send/push_warning",temp)

	def init_kafka_producer(self):
		self.producer  = KafkaProducer(
			bootstrap_servers = self.mbootstrap_servers
			#compression_type = "snappy"
		)
		self.pro_topic = "plep"
		self.pro_key = "push_warning"
		

	def send_kafka_message(self,mvalue):
		try:
			self.producer.send(topic = b'plep',value = b'dw13854aw',key = b'push_warning')
			#record_metadata =  future.get(timeout = 10)
			#print (record_metadata)
			print("succeed")
		except KafkaError as e:
			#print (e+"faile to push kafka  "+mvalue)
			pass

	def init_kafka_consumer(self):
		self.consumer = KafkaConsumer(
			bootstrap_server = self.mbootstrap_servers,
			group_id = "test"
		)
		self.consumer.subscribe(topics = [self.pro_topic])
		

	def kafkaPush(self,filepath):
		if(self.readJson(filepath+'.json')):	
			pictureBUpload = self.imageToBase64(filepath+'_B.jpg')
			pictureNUpload = self.imageToBase64(filepath+'_N.jpg')
			if(pictureBUpload is not 0 and pictureNUpload is not 0):
				self.myJson["Remote_File_ID_B"] = pictureBUpload
				self.myJson["Remote_File_ID_N"] = pictureNUpload
				self.httpUpload("http://172.31.226.82:8004/plep/api/kafka/send/push_warning_addition",self.myJson,filepath,3)
			else:
				pass
		else:
			pictureNUpload = self.imageToBase64(filepath+'_N.jpg')
			if (pictureNUpload is not 0):
				self.myJson["Remote_File_ID_N"] = pictureNUpload
				self.httpUpload("http://172.31.226.82:8004/plep/api/kafka/send/push_warning_addition",self.myJson,filepath,2)
			else:
				pass			
			
	def readJson(self,filepath):
		with open (filepath,mode = 'r') as f:
			getValue  = json.load(f)
			self.myJson = getValue
			if(self.myJson.has_key("Remote_File_ID_B")):
				return 1
			else:
				return 0

	def uploadVideoAndTxt(self,filename):
		self.fdfs_upload_by_file("TxT/"+filename+'.txt')
		self.fdfs_upload_by_file("VIDEO/"+filename+'.mov')	
	


	def httpUpload(self,url,data,path_to_rm,rmTag):
		#print(data)
		print(type(data))
		response = requests.post(url,data = json.dumps(data).encode(),
		headers = {'Content-type':'application/json'})
		
		#print(response.text)
		#print(type(response.text))
		my_response = response.text.encode('utf-8')
		my_response = json.loads(my_response)
		print(type(my_response))
		
		if response is not None and  my_response['success'] == True:
			self.removeFile(path_to_rm,rmTag)
			print("http post succeed")
		else:
			print("fail to post http request")



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
		

	def joinMyThread(self):
		self.m_thread.join()


	def readFilePathLoop(self,filepath):
		while(self.readPathLoopFlag):
			files = os.listdir(filepath)
			#print(self.readPathLoopFlag)
			#print(files)
			if len(files) is 0:
				continue
			for mfile in files:
				if  os.path.splitext(mfile)[1] == '.json':
					self.kafkaPush(filepath+'/'+os.path.splitext(mfile)[0])
						
			
	def setReadPathLoopFlag(self,flag):
		self.readPathLoopFlag = flag


	def getReadPathLoopFlag(self):
		return self.readPathLoopFlag


	def signal_quit(self,parma1,param2):
		self.setReadPathLoopFlag(False)


if __name__ == "__main__":
	kafkaTest = FileUpload("172.31.226.82:9092",sys.argv[1])
	while(kafkaTest.getReadPathLoopFlag()):
			#print(kafkaTest.getReadPathLoopFlag())
			time.sleep(1)
			signal.signal(signal.SIGINT,kafkaTest.signal_quit)

	kafkaTest.joinMyThread()
	#while 
	#mode = input("input 1 to upload picture and json,or 2 to upload video and txt:\n")
	#if(mode == 1):
		#filename = input("input the filename:\n")
		#kafkaTest.uploadVideoAndTxt(filename)
	#	kafkaTest.testKafka("./666.png")	
	#elif(mode == 2):
	#	filename = input("input the filename:\n")
	#	kafkaTest.kafkaPush(filename)
	































































































