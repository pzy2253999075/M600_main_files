#! /usr/bin/env python3
import subprocess
import rospy
from std_msgs.msg import Bool
import os 
import signal
import threading
import json
import mmap
from dji_sdk.msg import ScriptCtr
#import asyncio
import time



class ScriptCtrNode():
	def __init__(self):
		self.initSubPub()
		self.init_mmap()
		#self.init_asyncio()
		self.pubScriptStatusThread()

	def init_mmap(self):
		self.mmap_data = "predict=4,kafka=4,fdfs=4,dataRC=4,onlive=4"
		self.mmapPath = "/home/dji/DJI_Onboard_Sdk/src/Onboard-SDK-ROS/dji_sdk/script/mmap_info.txt"
		self.fileSize = os.path.getsize(self.mmapPath)
		self.myMmap = mmap.mmap(os.open(self.mmapPath,os.O_RDWR),self.fileSize)
		self.myMmap.seek(0)
		self.myMmap.write(self.mmap_data.encode())

	def getVauleFromMmap(self,key):
  		self.myMmap.seek(self.myMmap.find(key.encode(),0)+len(key)+1)
  		temp = self.myMmap.read(1)
  		return int(temp)


	def setValueToMmap(self,key,value):
  		self.myMmap.seek(self.myMmap.find(key.encode(),0)+len(key)+1)
  		self.myMmap.write(str(value).encode())


	def init_asyncio(self):
		new_loop  = asyncio.new_event_loop()
		asyncio.set_event_loop(new_loop)
		self.asyncio_loop = asyncio.get_event_loop()
		

	

	async def checkIfStartSuccess(self,key,time_sp):
		await asyncio.sleep(time_sp)
		if self.getVauleFromMmap(key) == 1:
			print("faile to open " + str(key))
			self.setValueToMmap(key,5)



	def initSubPub(self):
		self.predSub = rospy.Subscriber("m600_preCtr",Bool,self.preCtrCallback,queue_size = 10)
		self.kafkaPushSub  = rospy.Subscriber("m600_kakfaPush",Bool,self.kafkaPushCallback,queue_size = 10)
		self.fdfsPushSub = rospy.Subscriber("m600_fdfsPush",Bool,self.fdfsPushCallback,queue_size = 10)
		self.dataRecord = rospy.Subscriber("m600_dataRecord",Bool,self.dataRecordCallback,queue_size = 10)
		self.onliveSub = rospy.Subscriber("m600_onlive_ctr",Bool,self.onliveCallback,queue_size = 10)
		self.videoSave = rospy.Publisher("m600_video_save",Bool,queue_size = 10)
		self.scriptCtrStatusPub = rospy.Publisher("m600_script_ctr_status",ScriptCtr,queue_size = 10)
		self.scriptStatusMsg = ScriptCtr()
		#self.da=WaypointList()
		self.scriptCtrStatusPubRate  = rospy.Rate(1)


	def onliveCallback(self,boolMsg):
		if boolMsg.data is True:
			getOnliveValue = self.getVauleFromMmap('onlive')
			if getOnliveValue == 4 or getOnliveValue == 5:
				self.setValueToMmap('onlive',1)
				subprocess.Popen('gnome-terminal -x bash -c "python /home/dji/DJI_Onboard_Sdk/src/Onboard-SDK-ROS/dji_sdk/script/video_record/onlive.py;exec bash"',shell = True)


				time.sleep(10)
				#new_loop  = asyncio.new_event_loop()
				#asyncio.set_event_loop(new_loop)
				#self.asyncio_loop = asyncio.get_event_loop()
				#self.asyncio_loop.run_until_complete(self.checkIfStartSuccess("onlive",10))
				#time.sleep(5)
				if self.getVauleFromMmap('onlive')== 1:
					self.setValueToMmap('onlive',5)
				
		else:
			if self.getVauleFromMmap('onlive')== 2:
				self.setValueToMmap('onlive',3)





	def preCtrCallback(self,boolMsg):
		if boolMsg.data is True:
			getPreCtrValue = self.getVauleFromMmap('predict')
			if getPreCtrValue== 4 or getPreCtrValue == 5:
				self.setValueToMmap('predict',1)
				subprocess.Popen('gnome-terminal -x bash -c "echo dji | sudo -S /bin/bash /home/dji/DJI_Onboard_Sdk/src/Onboard-SDK-ROS/dji_sdk/script/V0.1_01_02_0/V0.1_01_02_0.sh InputDir OutputDir Route_ID;exec bash"',shell = True)		
				#new_loop  = asyncio.new_event_loop()
				#asyncio.set_event_loop(new_loop)
				#self.asyncio_loop = asyncio.get_event_loop()
				#self.asyncio_loop.run_until_complete(self.checkIfStartSuccess("predict",10))
				time.sleep(20)
				if self.getVauleFromMmap('predict')== 1:
					self.setValueToMmap('predict',5)
				
		else:
			if self.getVauleFromMmap('predict')== 2:
				self.setValueToMmap('predict',3)
			

	def kafkaPushCallback(self,boolMsg):
		if boolMsg.data is True:
			getKafkaPushValue = self.getVauleFromMmap('kafka')
			if getKafkaPushValue== 4 or getKafkaPushValue ==5:
				self.setValueToMmap('kafka',1)
				subprocess.Popen('gnome-terminal -x bash -c "python /home/dji/DJI_Onboard_Sdk/src/Onboard-SDK-ROS/dji_sdk/script/fastdfs/kafkaUpload.py /home/dji/DJI_Onboard_Sdk/src/Onboard-SDK-ROS/dji_sdk/script/V0.1_01_02_0/output http://172.31.226.82:8004/plep/api/kafka/send/push_warning_addition;exec bash"',shell = True)


				#new_loop  = asyncio.new_event_loop()
				#asyncio.set_event_loop(new_loop)
				#self.asyncio_loop = asyncio.get_event_loop()
				#self.asyncio_loop.run_until_complete(self.checkIfStartSuccess("kafka",10))
				time.sleep(5)
				if self.getVauleFromMmap('kafka')== 1:
					self.setValueToMmap('kafka',5)	
				
		else:
			if self.getVauleFromMmap('kafka')== 2:
				self.setValueToMmap('kafka',3)


	def fdfsPushCallback(self,boolMsg):
		if boolMsg.data is True:
			getFdfsPushValue = self.getVauleFromMmap('fdfs')
			if getFdfsPushValue== 4 or getFdfsPushValue == 5:
				self.setValueToMmap('fdfs',1)
				subprocess.Popen("python fdfspath",shell = True)

				#new_loop  = asyncio.new_event_loop()
				#asyncio.set_event_loop(new_loop)
				#self.asyncio_loop = asyncio.get_event_loop()
				#self.asyncio_loop.run_until_complete(self.checkIfStartSuccess("fdfs",10))
				time.sleep(5)
				if self.getVauleFromMmap('fdfs')== 1:
					self.setValueToMmap('fdfs',5)	
				
		else:
			if self.getVauleFromMmap('fdfs')== 2:
				self.setValueToMmap('fdfs',3)


	def dataRecordCallback(self,boolMsg):
		if boolMsg.data is True:
			getDataRecordValue = self.getVauleFromMmap('dataRC')
			if getDataRecordValue== 4 or getDataRecordValue== 5:
				self.setValueToMmap('dataRC',1)
				myBool =  Bool()
				myBool.data = True
				self.videoSave.publish(myBool)

		#		print("55555555556+6666")
				#new_loop  = asyncio.new_event_loop()
				#asyncio.set_event_loop(new_loop)
				#self.asyncio_loop = asyncio.get_event_loop()
				#self.asyncio_loop.run_until_complete(self.checkIfStartSuccess("dataRC",10))
				time.sleep(5)


		#		print("qwertyuiopasdfghjklzxcvbnm")
				if self.getVauleFromMmap('dataRC')== 1:
					self.setValueToMmap('dataRC',5)	
				
		#else:
		#	if self.getVauleFromMmap('dataRC')== 2:
		#		self.setValueToMmap('dataRC',3)
		#		myBool =  Bool()
		#		myBool.data = False
		#		self.videoSave.publish(myBool)


	def pubScriptStatusLoop(self):
		print("111222")
		while(not rospy.is_shutdown()):
			print("11111")
			kafkaStatus = self.getVauleFromMmap("kafka")
			fdfsStatus = self.getVauleFromMmap("fdfs")
			predictStatus = self.getVauleFromMmap("predict")
			dataRecordStatus = self.getVauleFromMmap("dataRC")
			onliveCtrStatus = self.getVauleFromMmap("onlive")
			self.scriptStatusMsg.kafkaPushCtrStatus.data = kafkaStatus
			self.scriptStatusMsg.fdfsPushCtrStatus.data = fdfsStatus
			self.scriptStatusMsg.predictCtrStatus.data = predictStatus
			self.scriptStatusMsg.dataRecordCtrStatus.data = dataRecordStatus
			self.scriptStatusMsg.onliveCtrStatus.data =  onliveCtrStatus
			self.scriptCtrStatusPub.publish(self.scriptStatusMsg)
			self.scriptCtrStatusPubRate.sleep()
			
	def pubScriptStatusThread(self):
		self.pubScriptThread  = threading.Thread(target = self.pubScriptStatusLoop)
		self.pubScriptThread.start()


	def pubScriptStatusThreadDel(self):
		self.pubScriptThread.join()
		self.asyncio_loop.close()
		#self.myMmap.close()
		
if __name__ == '__main__':
	rospy.init_node("ScriptCtr")
	myScriptCtr =  ScriptCtrNode()
	rospy.spin()
	myScriptCtr.pubScriptStatusThreadDel()






































