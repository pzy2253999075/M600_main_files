import numpy as py
import cv2
import rospy
from std_msgs.msg import Bool
import rospy
import datetime

#datetime.datetime.now().strftime('video/+''%Y-%m-%d %H:%M:%S')+

if __name__ == '__main__':
	rospy.init_node("66636")
	cap = cv2.VideoCapture(0);
	fourcc = cv2.VideoWriter_fourcc(*'X264')
	frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
	frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
	out = cv2.VideoWriter('ddwadw.avi',fourcc,20,(frame_width,frame_height))
	while(not rospy.is_shutdown()):
		print("dddddddd")
		ret, frame = cap.read()
		if ret ==True:
			print("access")
			#cv2.cvtColor(frame,cv2.COLOR_RGB2BGR)
			out.write(frame)	
			cv2.imshow('frame',frame)
			cv2.waitKey(1) 

	cap.release()
	out.release()
	cv2.destroyAllWindows()













































