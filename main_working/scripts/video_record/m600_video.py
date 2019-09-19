import subprocess as sp
import cv2
import time
import mmap
import os
import signal
import sys
from func_timeout import func_set_timeout ,FunctionTimedOut
from cv_bridge import CvBridge,CvBridgeError
from sensor_msgs.msg import Image
import rospy
import threading
from threading import Lock
from sensor_msgs.msg import NavSatFix
from std_msgs.msg import Float32
import datetime
import piexif
from PIL import Image as pImage
from fractions import Fraction 
import ffmpeg
import re

#rtmpUrl = "rtmp://send3a.douyu.com/live/976948rsDWcEbFyY?wsSecret=61d5a86470678bd04cb3a86557f6926e&wsTime=5d6c9f66&wsSeek=off&wm=0&tw=0&roirecognition=0"
#rtmpUrl = "rtmp://livepush.binyx.vip/live/m600?txSecret=3c2ac4fd2c7c135b00986ca3dee2b798&txTime=5D6E8DFF"
class M600VideoScript():
	def __init__(self):
		#self.rtmpUrl = 'rtmp://47.106.127.177:1935/stream/m600'
		self.rtmpUrl = 'rtmp://pushlive.binyx.vip/live/m600?txSecret=f5809039373e5a9431ee76d8f947cd34&txTime=5D9F557F'
		self.on_init()
		
	def __del__(self):
		self.on_destroy()


	def init_mymmap(self):
  		self.mmapPath = "/home/dji/DJI_Onboard_Sdk/src/Onboard-SDK-ROS/dji_sdk/scripts/mmap_info.txt"
  		self.myMmap = mmap.mmap(os.open(self.mmapPath,os.O_RDWR),os.path.getsize(self.mmapPath))
    	 



	def getVauleFromMmap(self,key):
 		self.myMmap.seek(self.myMmap.find(key,0)+len(key)+1)
  		temp = self.myMmap.read(1)
  		return temp


	def setValueToMmap(self,key,value):
  		self.myMmap.seek(self.myMmap.find(key,0)+len(key)+1)
  		self.myMmap.write(str(value))



	def ffmpeg_test(self):
		self.process  = ( 
			ffmpeg.input('pipe:',format = 'rawvideo', pix_fmt = 'rgb24',s ='{}x{}'.format(1920,1080))
			.output('rtmp://pushlive.binyx.vip/live/m600?txSecret=f5809039373e5a9431ee76d8f947cd34&txTime=5D9F557F',pix_fmt = 'yuv420p',format = 'h264',preset = 'ultrafast',b='2000k',r = 30)
			.overwrite_output().run_async(pipe_stdin =True)
		)




	def init_ffmpeg_1080(self):
		self.timeout_count_1080 = 0
		self.ffmpeg_command = ['ffmpeg',
				'-y',
       				'-f', 'rawvideo',
        			'-vcodec','rawvideo',
        			'-pix_fmt', 'bgr24',
        			'-s', "{}x{}".format(1920,1080),
				#'-aspect',str(1.77777),
        			'-r', str(30),
        			'-i', '-',
        			'-c:v', 'libx264',
				'-stimeout',str(3000),
        			'-pix_fmt', 'yuv420p',
        			'-preset', 'ultrafast',
				'-b:v','2000k',
				#'-bufsize','200000k',
        			'-f', 'flv', 
        			self.rtmpUrl]
			
		self.ffmpeg_1080 = sp.Popen(self.ffmpeg_command, stdin=sp.PIPE,preexec_fn = os.setsid)
		print("dwadwadwadawda")




	def init_ffmpeg_720(self):
		self.timeout_count_720 = 0
		self.ffmpeg_command = ['ffmpeg',
				'-y',
       				'-f', 'rawvideo',
        			'-vcodec','rawvideo',
        			'-pix_fmt', 'bgr24',
        			'-s', "{}x{}".format(1280,720),
				#'-aspect',str(1.77777),
        			'-r', str(30),
        			'-i', '-',
        			'-c:v', 'libx264',
				'-stimeout',str(3000),
       				'-pix_fmt', 'yuv420p',
        			'-preset', 'ultrafast',
				'-b:v','1000k',
				#'-bufsize','200000k',
        			'-f', 'flv', 
        			self.rtmpUrl]
			
		self.ffmpeg_720 = sp.Popen(self.ffmpeg_command, stdin=sp.PIPE,preexec_fn = os.setsid)
		print("dwadwadwadawda")

	

	def init_ffmpeg_540(self):
		self.timeout_count_540 = 0
		self.ffmpeg_command = ['ffmpeg',
				'-y',
       				'-f', 'rawvideo',
        			'-vcodec','rawvideo',
        			'-pix_fmt', 'bgr24',
        			'-s', "{}x{}".format(960,540),
				#'-aspect',str(1.77777),
        			'-r', str(30),
        			'-i', '-',
        			'-c:v', 'libx264',
				'-stimeout',str(3000),
       				'-pix_fmt', 'yuv420p',
        			'-preset', 'ultrafast',
				'-b:v','500k',
				#'-bufsize','200000k',
        			'-f', 'flv', 
        			self.rtmpUrl]
			
		self.ffmpeg_540 = sp.Popen(self.ffmpeg_command, stdin=sp.PIPE,preexec_fn = os.setsid)
		print("dwadwadwadawda")




	def initSubPub(self):
		self.video_image_sub  = rospy.Subscriber("/camera/image_raw",Image,self.revImageCallback,queue_size = 10)
		self.gpsSub = rospy.Subscriber("dji_sdk/gps_position",NavSatFix,self.updateGps,queue_size = 10)
		self.haboSub = rospy.Subscriber("/dji_sdk/height_above_takeoff",Float32,self.updateHABO,queue_size = 10)
		self.image_data = None
		self.network_ping_count = 0
		self.gpsData =NavSatFix()
		self.haboData = Float32()
		self.image_use_lock = Lock()
		self.network_ping_count_lock = Lock()
		self.on_live_pub_rate = rospy.Rate(30)
		self.str_file_write_rate = rospy.Duration(3)
		self.predict_pic_save_rate = rospy.Duration(0.5)
		self.cvBridge = CvBridge()
	
######callbacks	

	def revImageCallback(self,immsg):
		self.image_data = immsg

	def updateGps(self,gpsMsg):
		self.gpsData =  gpsMsg

	def updateHABO(self,haboMsg):
		self.haboData = haboMsg


##############  image_turn and the option to send image to rtmp_servers
	def rosImage2OpencvMat(self):
		try:
			self.image_use_lock.acquire()
			mat = None
			if(self.image_data is not None):
				mat = self.cvBridge.imgmsg_to_cv2(self.image_data,"bgr8")
				#print("mat")
				#print(mat)
		finally:	
			self.image_use_lock.release()
		return mat 
				

	@func_set_timeout(3)
	def writeIntoPipe_1080(self,frame):
		try:
    			self.ffmpeg_1080.stdin.write(frame.tostring())
			print("1080")
		except IOError as e:
			print(e)
			time.sleep(5)
			print("ooooooooooooooooooooooooooooooooooooooooooooooo")
			#raise e
			#os.killpg(self.ffmpeg_1080.pid,signal.SIGTERM)
			#self.ffmpeg_1080 = sp.Popen(self.ffmpeg_command, stdin=sp.PIPE,preexec_fn = os.setsid)


	@func_set_timeout(3)
	def writeIntoPipe_720(self,frame):
		try:
    			self.ffmpeg_720.stdin.write(frame.tostring())
			print("720")
		except IOError as e:
			print(e)
			time.sleep(5)
			#os.killpg(self.ffmpeg_720.pid,signal.SIGTERM)
			#self.ffmpeg_720 = sp.Popen(self.ffmpeg_command, stdin=sp.PIPE,preexec_fn = os.setsid)


	@func_set_timeout(3)
	def writeIntoPipe_540(self,frame):
		try:
    			self.ffmpeg_540.stdin.write(frame.tostring())
			print("540")
		except IOError as e:
			print(e)
			time.sleep(5)
			#os.killpg(self.ffmpeg_540.pid,signal.SIGTERM)
			#self.ffmpeg_540 = sp.Popen(self.ffmpeg_command, stdin=sp.PIPE,preexec_fn = os.setsid)




	def networingHealthThread(self):
		totally_lost = True
		while(not rospy.is_shutdown()):
			res = os.popen("ping www.baidu.com -w 3") 
			res1 = res.read()
			try:
				self.network_ping_count_lock.acquire()
				for line in res1.splitlines():
					ifmatch = re.match(r'rtt.*=.*/(.*)/.*/.*',line)
					if ifmatch:
						self.network_ping_count =  float(ifmatch.group(1))
						totally_lost = False
						if (self.network_ping_count) <=100.0:
							self.network_health_flag = 1
						elif (self.network_ping_count) <=500.0:
							self.network_health_flag = 2	
						elif (self.network_ping_count) <=2000.0:
							self.network_health_flag = 3
						else:
							totally_lost = True
						break
				if totally_lost == True:
				
					self.network_health_flag = 4
					self.network_ping_count = -1
					print("totally lost")
				else:
					print("not totally lost")
					totally_lost = True
			finally:
				self.network_ping_count_lock.release()


#######networking_health_rc_thread


	def network_health_rc_thread(self):	
		with open("/home/dji/new_disk/network_health/"+datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')+'.txt',"a") as f:
			while(not rospy.is_shutdown()):
				f.writelines(str(self.gpsData.latitude)+','+str(self.gpsData.longitude)+','+str(self.haboData.data)+' '+str(self.network_ping_count)+'\n')
				f.flush()
				time.sleep(3)		



#########init_kinds_of_threads
	def onLiveLoopThread(self):
		while(not rospy.is_shutdown()):
			if self.onliveAlreadyEnd == True:
				self.setValueToMmap("onlive",4)
				self.onliveAlreadyEnd = False
				self.onliveAlreadyStart = True
			while(self.getVauleFromMmap("onlive") == str(2) or self.getVauleFromMmap("onlive") == str(1)):
				if self.onliveAlreadyStart == True:
					self.setValueToMmap("onlive",2)
					self.onliveAlreadyStart = False
					self.onliveAlreadyEnd = True
				frame = self.rosImage2OpencvMat()
				if(frame is not None):
					try:
						count_temp = 0
						if self.network_health_flag == 1:
							count_temp = 1 
							self.writeIntoPipe_1080(frame)
						elif self.network_health_flag == 2:
							count_temp = 2
							self.writeIntoPipe_720(frame)
						elif self.network_health_flag == 3:
							count_temp = 3
							self.writeIntoPipe_540(frame)
						elif self.network_health_flag == 4:
							count_temp = 4
							pass
						if(count_temp == 1):
							self.timeout_count_1080 = 0
						elif(count_temp == 2):
							self.timeout_count_720 = 0
						elif(count_temp == 3):
							self.timeout_count_540 = 0
						#self.process.stdin.write(frame.tostring())
					except 	FunctionTimedOut as e:
						if(count_temp ==1):
							self.timeout_count_1080 = self.timeout_count_1080+1
						elif(count_temp ==2):
							self.timeout_count_720 = self.timeout_count_720+1
						elif(count_temp ==3):
							self.timeout_count_540 = self.timeout_count_540+1
						print(e)
						if(self.timeout_count_1080 == 3):
							os.killpg(self.ffmpeg_1080.pid,signal.SIGTERM)
							time.sleep(1)
							self.init_ffmpeg_1080()
							time.sleep(1)
						elif(self.timeout_count_720 == 3):
							os.killpg(self.ffmpeg_720.pid,signal.SIGTERM)
							time.sleep(1)
							self.init_ffmpeg_720()
							time.sleep(1)
						elif(self.timeout_count_540 == 3):
							os.killpg(self.ffmpeg_540.pid,signal.SIGTERM)
							time.sleep(1)
							self.init_ffmpeg_540()
							time.sleep(1)
				self.on_live_pub_rate.sleep()



	def recordStrLoop(self,arg):
		with open ('/home/dji/new_disk/record/'+self.data_time_name+'.txt','a') as f:	
			while(not self.str_file_write_once):
				f.writelines(str(self.gpsData.latitude)+','+str(self.gpsData.longitude)+','+str(self.haboData.data)+'\n')
				f.flush()
				rospy.sleep(self.str_file_write_rate)


	def recordLoop(self):
		while(not rospy.is_shutdown()):
			if self.recordAlreadyEnd == True:
				self.setValueToMmap("dataRC",4)
				self.recordAlreadyEnd = False
				self.recordAlreadyStart = True
			while(self.getVauleFromMmap("dataRC") == str(1) or self.getVauleFromMmap("dataRC") == str(2)):
				if self.recordAlreadyStart == True:
					self.setValueToMmap("dataRC",2)
					self.recordAlreadyStart = False
					self.recordAlreadyEnd = True
				fourcc = cv2.cv.CV_FOURCC(*'XVID')
				self.data_time_name = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
				out = cv2.VideoWriter('/home/dji/new_disk/record/'+self.data_time_name+'.avi',fourcc,25,(1920,1080))
				self.str_file_write_once = True
				t = threading.Thread(target = self.recordStrLoop,name = "record str",args = [1,])
				
				now = time.time()
				while time.time() - now < 60 and self.getVauleFromMmap("dataRC") == str(2):
					frame = self.rosImage2OpencvMat()
					print("oooyu")
					if(frame is not None):
						print("access")
						out.write(frame)
						if self.str_file_write_once:
							self.str_file_write_once = False
							t.start()		
						#cv2.imshow('frame',frame)
						#cv2.waitKey(1)
				self.str_file_write_once = True
				t.join()
				out.release()			
				cv2.destroyAllWindows()




###########exifwrite

	def to_deg(self,value, loc): 
		if value < 0: 
			loc_value = loc[0] 
		elif value > 0: 
			loc_value = loc[1] 
 		else: 
 			loc_value = "" 
 		abs_value = abs(value) 
 		deg = int(abs_value) 
 		t1 = (abs_value-deg)*60 
 		min = int(t1) 
 		sec = round((t1 - min)* 60, 5) 
 		return (deg, min, sec, loc_value) 


	def change_to_rational(self,number): 
		f = Fraction(str(number)) 
 		return (f.numerator, f.denominator) 



	def get_gps_exif_bytes(self): 
		lat_deg = self.to_deg(self.gpsData.latitude, ["S", "N"]) 
		lng_deg = self.to_deg(self.gpsData.longitude, ["W", "E"]) 
		exiv_lat = (self.change_to_rational(lat_deg[0]), self.change_to_rational(lat_deg[1]), self.change_to_rational(lat_deg[2])) 
		exiv_lng = (self.change_to_rational(lng_deg[0]), self.change_to_rational(lng_deg[1]), self.change_to_rational(lng_deg[2])) 
		gps_ifd = { 
 		piexif.GPSIFD.GPSVersionID: (2, 0, 0, 0), 
 		piexif.GPSIFD.GPSAltitudeRef: 1, 
		piexif.GPSIFD.GPSAltitude: self.change_to_rational(round(self.haboData.data)), 
		piexif.GPSIFD.GPSLatitudeRef: lat_deg[3], 
 		piexif.GPSIFD.GPSLatitude: exiv_lat, 
 		piexif.GPSIFD.GPSLongitudeRef: lng_deg[3], 
 		piexif.GPSIFD.GPSLongitude: exiv_lng, 
		} 
		exif_dict = {"GPS": gps_ifd} 
		exif_bytes = piexif.dump(exif_dict)
		return exif_bytes


##############savepredictPic


	def savePredictPicThreadLoop(self):
		while(not rospy.is_shutdown()):
			while(self.getVauleFromMmap("predict") == str(2)):
				frame = self.rosImage2OpencvMat()
				if (frame is not None):
					img = pImage.fromarray(cv2.cvtColor(frame,cv2.COLOR_BGR2RGB))
					exif_bytes = self.get_gps_exif_bytes()
					img.save('/home/dji/DJI_Onboard_Sdk/src/Onboard-SDK-ROS/dji_sdk/scripts/V0.1_01_02_0/input/'+datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')+'_N.jpg',exif = exif_bytes)
					#cv2.imwrite('/home/dji/DJI_Onboard_Sdk/src/Onboard-SDK-ROS/dji_sdk/scripts/V0.1_01_02_0/dataProcess/img_keep/'+datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')+'.jpg',frame)	
					#rospy.sleep(self.predict_pic_save_rate)
			rospy.sleep(self.predict_pic_save_rate)



	def init_threads(self):
		self.recordAlreadyEnd = True
		self.recordAlreadyStart = False
		self.onliveAlreadyEnd = True
		self.onliveAlreadyStart = False
		self.network_health_flag = 1
		self.onliveThread = threading.Thread(target = self.onLiveLoopThread)
		self.recordThread = threading.Thread(target = self.recordLoop)
		self.networkPingThread = threading.Thread(target = self.networingHealthThread)
		self.savePrePicThread = threading.Thread(target = self.savePredictPicThreadLoop)
		self.networkHealthSaveThread = threading.Thread(target = self.network_health_rc_thread)
		self.onliveThread.start()
		self.recordThread.start()
		self.networkPingThread.start()
		self.savePrePicThread.start()
		self.networkHealthSaveThread.start()



	def on_init(self):
		self.init_mymmap()
		#self.ffmpeg_test()
		self.init_ffmpeg_1080()
		self.init_ffmpeg_720()
		self.init_ffmpeg_540()
		self.initSubPub()
		self.init_threads()
		

	def on_destroy(self):
		self.onliveThread.join()
		self.recordThread.join()
		self.savePrePicThread.join()
		self.networkPingThread.join()
		self.networkHealthSaveThread.join()
		self.myMmap.close()
		os.killpg(self.ffmpeg_1080.pid,signal.SIGTERM)
		os.killpg(self.ffmpeg_720.pid,signal.SIGTERM)
		os.killpg(self.ffmpeg_540.pid,signal.SIGTERM)


if __name__ == '__main__':
	rospy.init_node("M600VideoScript")
	myNode = M600VideoScript()
	rospy.spin()
	del myNode
	

















