#!/usr/bin/env python
import numpy as py
import cv2
import rospy
from std_msgs.msg import Bool,Float32
import rospy
import datetime
import threading
import time
import mmap
import signal
import os
from sensor_msgs.msg import NavSatFix 


class DataRecord():
	
	def __init__(self):
		self.loop_flag = False
		self.synPubOnceFlag = False
		self.alreadyStart = True
		self.alreadyEnd = True
		self.initSubPub()
		self.init_mmap()
		self.recordLoopThread()
		



	def init_mmap(self):
		self.mmapPath = "/home/dji/DJI_Onboard_Sdk/src/Onboard-SDK-ROS/dji_sdk/scripts/mmap_info.txt"
		self.fileSize = os.path.getsize(self.mmapPath)
		self.myMmap = mmap.mmap(os.open(self.mmapPath,os.O_RDWR),self.fileSize)

	def getVauleFromMmap(self):
  		self.myMmap.seek(self.myMmap.find("dataRC",0)+len("dataRC")+1)
  		temp = self.myMmap.read(1)
  		return int(temp)


	def setValueToMmap(self,value):
  		self.myMmap.seek(self.myMmap.find("dataRC",0)+len("dataRC")+1)
  		self.myMmap.write(str(value))



	def initSubPub(self):
		self.gpsData =None
		self.haboData = None
		self.loopFlagSub = rospy.Subscriber("/m600_video_save",Bool,self.loop_flag_callback,queue_size = 10)
		self.gpsSub = rospy.Subscriber("dji_sdk/gps_position",NavSatFix,self.updateGps,queue_size = 10)
		self.haboSub = rospy.Subscriber("/dji_sdk/height_above_takeoff",Float32,self.updateHABO,queue_size = 10)
	

	def loop_flag_callback(self,boolMsg):
		self.loop_flag = boolMsg.data


	def updateGps(self,gpsMsg):
		self.gpsData =  gpsMsg

	def updateHABO(self,haboMsg):
		self.haboData = haboMsg

	def recordStrLoop(self,arg):
		f = open('/home/dji/DJI_Onboard_Sdk/src/Onboard-SDK-ROS/dji_sdk/script/video_record/record_data/'+self.data_time_name+'.txt','a')	
		while(self.loop_flag):
			if (self.gpsData == None or self.haboData ==None):
				print("could not read str data")
				continue 
			f.writelines(str(self.gpsData.latitude)+','+str(self.gpsData.longitude)+','+str(self.haboData.data)+'\n')
			time.sleep(arg)
		f.close()



	def recordLoop(self):
		while(not rospy.is_shutdown()):
			if self.alreadyEnd == True:
				self.setValueToMmap(4)
				self.alreadyEnd = False
				self.alreadyStart = True
			if self.loop_flag:
				if self.alreadyStart == True:
					self.setValueToMmap(2)
					self.alreadyStart = False
					self.alreadyEnd = True
				cap = cv2.VideoCapture(0);
				fourcc = cv2.VideoWriter_fourcc(*'X264')
				frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
				frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
				self.data_time_name = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
				out = cv2.VideoWriter('/home/dji/DJI_Onboard_Sdk/src/Onboard-SDK-ROS/dji_sdk/script/video_record/record_data/'+self.data_time_name+'.avi',fourcc,25,(frame_width,frame_height))
				t = threading.Thread(target = self.recordStrLoop,name = "record str",args = (1,))
				self.synPubOnceFlag = True
				now = time.time()
				while time.time() - now < 180 and self.loop_flag:
					ret, frame = cap.read()
					if ret ==True:
						print("access")
						out.write(frame)
						if self.synPubOnceFlag:
							t.start()
						self.synPubOnceFlag = False
						cv2.imshow('frame',frame)
						cv2.waitKey(1) 
				t.join()
				out.release()			
				cap.release()
				cv2.destroyAllWindows()
				


	def recordLoopThread(self):
		self.my_loop_thread = threading.Thread(target = self.recordLoop)
		self.my_loop_thread.start()
		
	def joinMyLoopThread(self):
		self.my_loop_thread.join()
		self.myMmap.close()





if __name__ == "__main__":
	rospy.init_node("video_re")
	myRecordNode = DataRecord()
	rospy.spin()
	myRecordNode.joinMyLoopThread()

































