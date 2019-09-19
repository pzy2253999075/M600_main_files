import subprocess as sp
import cv2
import time
import mmap
import os
import signal
import librtmp

rtmpUrl = "rtmp://send3a.douyu.com/live/976948rcHoxLK9jM?wsSecret=b0f7a5396f6246db14a2492ae1705021&wsTime=5d6f69b8&wsSeek=off&wm=0&tw=0&roirecognition=0"
conn = librtmp.RTMP(rtmpUrl,live =True)
conn.connect()
stream = conn.create_stream(writeable = True)

#rtmpUrl = "rtmp://send3a.douyu.com/live/976948rsDWcEbFyY?wsSecret=61d5a86470678bd04cb3a86557f6926e&wsTime=5d6c9f66&wsSeek=off&wm=0&tw=0&roirecognition=0"
#rtmpUrl = "rtmp://livepush.binyx.vip/live/m600?txSecret=3c2ac4fd2c7c135b00986ca3dee2b798&txTime=5D6E8DFF"

#myMmap = None
#mmapPath = "/home/dji/DJI_Onboard_Sdk/src/Onboard-SDK-ROS/dji_sdk/scripts/mmap_info.txt"

#def init_mymmap():
#  global myMmap
#  global mmapPath
#  myMmap = mmap.mmap(os.open(mmapPath,os.O_RDWR),os.path.getsize(mmapPath))
    	
 
#def getVauleFromMmap():
#  global myMmap
#  myMmap.seek(myMmap.find('onlive',0)+len("onlive")+1)
#  temp = myMmap.read(1)
#  return int(temp)


#def setValueToMmap(value):
#  global myMmap
#  myMmap.seek(myMmap.find('onlive',0)+len("onlive")+1)
#  myMmap.write(str(value))

#init_mymmap()
#rtmpUrl = "rtmp://www.binyx.vip:1935/stream/m600"
cap = cv2.VideoCapture(0)
# Get video information
#fps = cap.get(cv2.cv.CV_CAP_PROP_FPS)
#width = int(cap.get(cv2.cv.CV_CAP_PROP_FRAME_WIDTH))
#height = int(cap.get(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT))
print("aaaaaaaa")
# ffmpeg command
command = ['ffmpeg',
        '-y',
        '-f', 'rawvideo',
        '-vcodec','rawvideo',
        '-pix_fmt', 'bgr24',
        '-s', "{}x{}".format(640, 480),
        '-r', str(25),
        '-i', '-',
        '-c:v', 'libx264',
        '-pix_fmt', 'yuv420p',
        '-preset', 'ultrafast',
        '-f', 'flv', 
        rtmpUrl]

#p = sp.Popen(command, stdin=sp.PIPE,preexec_fn = os.setsid)
#setValueToMmap(2)
while(cap.isOpened()):
   # if getVauleFromMmap() == 3:
#	break;
    ret, frame = cap.read()
    if not ret:
        print("Opening camera is failed")
        break
    try:
	print("25")
	print(frame)
	stream.write(frame.tobytes())
    	#p.stdin.write(frame.tostring())
    except librtmp.RTMPError as e:
	print(e)
	print("321546")
os.killpg(p.pid,signal.SIGTERM)    
#setValueToMmap(4)

