import numpy as py
import cv2
import rospy
from std_msgs.msg import Bool,Float32
import rospy
import datetime
import threading
import time
from sensor_msgs.msg import NavSatFix 


class Record():
	
	def __init__(self):
		self.initSubPub()
		self.waitLoop()


	def initSubPub(self):
		self.isStart = False
		self.synPubOnceFlag = True
		self.gpsData =None
		self.haboData = None
		self.isStartSub = rospy.Subscriber("/m600_video_save",Bool,self.isStartCallback,queue_size = 10)
		self.gpsSub = rospy.Subscriber("dji_sdk/gps_position",NavSatFix,self.updateGps,queue_size = 10)
		self.haboSub = rospy.Subscriber("/dji_sdk/height_above_takeoff",Float32,self.updateHABO,queue_size = 10)
	
	def isStartCallback(self,isStartMsg):
		self.isStart = isStartMsg.data
	
	def updateGps(self,gpsMsg):
		self.gpsData =  gpsMsg

	def updateHABO(self,haboMsg):
		self.haboData = haboMsg

	def recordStrLoop(self,arg):
		f = open(datetime.datetime.now().strftime('stringInfo/+''%Y-%m-%d %H:%M:%S')+'.txt','a')	
		while(self.isStart):
			if (self.gpsData == None or self.haboData ==None):
				print("could not read data")
				continue 
			f.writelines(str(self.gpsData.latitude)+','+str(self.gpsData.longitude)+','+str(self.haboData.data)+'\n')
			time.sleep(arg)
		f.close()


	def waitLoop(self):
		while(not rospy.is_shutdown()):
			if self.isStart:
				cap = cv2.VideoCapture(0);
				fourcc = cv2.VideoWriter_fourcc(*'X264')
				frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
				frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
				out = cv2.VideoWriter(datetime.datetime.now().strftime('video/+''%Y-%m-%d %H:%M:%S')+'.avi',fourcc,25,(frame_width,frame_height))
				t = threading.Thread(target = self.recordStrLoop,name = "record str",args = (1,))
				self.synPubOnceFlag = True
				while self.isStart:
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
			


if __name__=='__main__':

	rospy.init_node("record_and_save")
	myRecordNode = Record()
	rospy.spin()
		
































