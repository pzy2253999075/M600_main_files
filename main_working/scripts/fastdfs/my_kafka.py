from kafka import KafkaProducer
from kafka.errors import KafkaError
from kafka import KafkaConsumer
import cv2
import threading 
import rospy
from std_msgs.msg import String
from fdfs_client.client import *



class FileUpload():
	def __init__(self,mbootstrap_servers):
		self.mbootstrap_servers = mbootstrap_servers
		self.init_kafka_producer()
		self.init_fdfs_client()
		self.initSubPub()
		self.myJson = {}

		

	def init_fdfs_client(self):
		self.fdfs_client = Fdfs_client('/etc/fdfs/client.conf.sample')
	

	def fdfs_upload_by_file(self,path):
		ret = self.fdfs_client.upload_by_filename(path)
		return ret['Remote file_id']
		
	

	def init_kafka_producer(self):
		self.producer  = KafkaProducer(
			bootstrap_servers = self.mbootstrap_servers,
			
		)
		self.pro_topic = "plep"
		self.pro_key = "push_warning"
		

	def send_kafka_message(self,mvalue):
		try:
			future = self.producer.send(topic = self.pro_topic,value = str(mvalue).encode('utf8'),key = self.pro_key)
			record_metadata =  future.get(timeout = 10)
			print (record_metadata)
		except KafkaError as e:
			print (e+"faile to push kafka  "+mvalue)
		
	def init_kafka_consumer(self):
		self.consumer = KafkaConsumer(
			bootstrap_server = self.mbootstrap_servers,
			group_id = "test"
		)
		self.consumer.subscribe(topics = [self.pro_topic])


	def initSubPub(self):
		self.testSub = rospy.Subscriber("/kafka_push",String,self.kafkaPushCallback,queue_size = 10)
		

	def kafkaPushCallback(self,filename):
		if(self.readJson("Json/"+filename.data)):	
			pictureBUpload = self.fdfs_upload_by_file("picture/"+filename.data+'_B')
			pictureNUpload = self.fdfs_upload_by_file("picture/"+filename.data+'_N')
			self.myJson["Remote_File_ID_B"] = pictureBUpload
			self.myJson["Remote_File_ID_N"] = pictureNUpload
			self.send_kafka_message(self.myJson)
		else:
			pictureNUpload = self.fdfs_upload_by_file("picture/"+filename.data)
			self.myJson["Remote_File_ID_N"] = pictureNUpload
			self.send_kafka_message(self.myJson)

	def readJson(self,filepath):
		with open (filepath,mode = 'r') as f:
			getValue  = json.load(f)
			self.myJson = getValue
			if(self.myJson.has_key("Remote_File_ID_B")):
				return 1
			else:
				return 0	
	

if __name__ == "__main__":
	rospy.init_node("test_kafka")
	kafkaTest = FileUpload("172.31.226.82:9092")
	rospy.spin()
	
	















































