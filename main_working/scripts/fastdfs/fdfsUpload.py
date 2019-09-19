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


class FdfsUpload():
	def __init__(self,filepath):
		self.init_mmap()
		self.init_fdfs_client()
		self.myJson = {"JSON_ID":"","Video_Remote_Id":"","Gps_Remote_Id":"","Route_ID":""}
		self.readFilePathLoopThread(filepath)
			

	def init_mmap(self):
		self.mmapPath = "/home/dji/DJI_Onboard_Sdk/src/Onboard-SDK-ROS/dji_sdk/scripts/mmap_info.txt"
		self.fileSize = os.path.getsize(self.mmapPath)
		self.myMmap = mmap.mmap(os.open(self.mmapPath,os.O_RDWR),self.fileSize)


	def getVauleFromMmap(self):
  		self.myMmap.seek(self.myMmap.find("fdfs",0)+len("fdfs")+1)
  		temp = self.myMmap.read(1)
  		return int(temp)


	def setValueToMmap(self,value):
  		self.myMmap.seek(self.myMmap.find("fdfs",0)+len("fdfs")+1)
  		self.myMmap.write(str(value))



	def init_fdfs_client(self):
		self.fdfs_client = Fdfs_client('/etc/fdfs/client.conf.sample')
	


	def fdfs_upload_by_file(self,path):
		try:
			print("f1")
			ret = self.fdfs_client.upload_by_filename(path)
			if ret is not None and ret['Status'] == "Upload successed":
				print("f2")
				return ret['Remote file_id']
			else:
				print("f3")
				return False
		except Exception as e:
			print(e)
			print("eee")
			return False
	

	def imageToBase64(self,filepath):
		try:
			with open(filepath,'rb') as f:
				base64_str = base64.b64encode(f.read())
				return base64_str
		except Exception as e:
			print("fail to read picture")
			print(e)
			return 0



	def kafkaPush(self,filepath):
		ret1 = self.fdfs_upload_by_file(filepath+'.avi')
		print("456789023")
		ret2 = self.fdfs_upload_by_file(filepath+'.txt')
		if(ret1 is not 0 and ret1 is not 0):
			self.myJson['Video_Remote_Id'] = ret1 
			self.myJson['Gps_Remote_Id'] = ret2
			self.httpUpload(sys.argv[2],self.myJson,filepath)

	
	def readJson(self,filepath):
		with open (filepath,mode = 'r') as f:
			getValue  = json.load(f)
			self.myJson = getValue
			if(self.myJson.has_key("Image_Stream_B")):
				return 1
			else:
				return 0

	

	def httpUpload(self,url,data,path_to_rm):
		print(type(data))
		try:
			response = requests.post(url,data = json.dumps(data).encode("utf-8"),
			headers = {'Content-type':'application/json'},timeout = 5.0)
			if(response is not None):
				my_response = response.text.encode('utf-8')
				my_response = json.loads(my_response)
				if  my_response['success'] == True:
					#self.removeFile(path_to_rm)
					print("http post succeed")
				else:
					print("fail to post http request")

		except requests.exceptions.ConnectTimeout as e:
			print(e)
			print("please check the url")
	
		

	def removeFile(self,filepath):
		os.remove(filepath+'.avi')
		os.remove(filepath+'.txt')


	def readFilePathLoopThread(self,filepath):
		self.m_thread = threading.Thread(target = self.readFilePathLoop,args = (filepath,))
		self.m_thread.start()
		self.m_thread.join()
		self.setValueToMmap(4)		


	def joinMyThread(self):
		self.m_thread.join()


	def readFilePathLoop(self,filepath):
		self.setValueToMmap(2)		
		while(True):
			if(self.getVauleFromMmap() == 3):
				break
			files = os.listdir(filepath)
			if len(files) is 0:
				continue
			for mfile in files:
				if  os.path.splitext(mfile)[1] == '.avi':
					self.kafkaPush(filepath+'/'+os.path.splitext(mfile)[0])
			
						



if __name__ == "__main__":
	mFdfsUpload = FdfsUpload(sys.argv[1])
	
	































































































