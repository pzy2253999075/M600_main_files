# -*- coding: utf-8 -*-
# --------------------------------------------------------

import os
import time
import argparse
import json
import mmap
from yolo_detect_server_infer import *



myMmap = None
mmapPath = "/home/dji/DJI_Onboard_Sdk/src/Onboard-SDK-ROS/dji_sdk/scripts/mmap_info.txt"
stop_flag = None

def init_mymmap():
  global myMmap
  global mmapPath
  myMmap = mmap.mmap(os.open(mmapPath,os.O_RDWR),os.path.getsize(mmapPath))
    	
 
def getVauleFromMmap():
  global myMmap
  global mmapPath
  myMmap.seek(myMmap.find('predict',0)+len("predict")+1)
  temp = myMmap.read(1)
  return int(temp)


def setValueToMmap(value):
  global myMmap
  myMmap.seek(myMmap.find('predict',0)+len("predict")+1)
  myMmap.write(str(value))


def detect_img():
  net, meta = load_yolo_net()

  in_img_name = "./in_img/V0.1_01_02_2000080.jpg"

  out_img_name = "./out_img/det_V0.1_01_02_2000080.jpg"

  start = time.time()

  detect_infer(net, meta, in_img_name, out_img_name, save_mode=0)

  end = time.time()

  print("detect used time {:.3f}s \n".format(end - start))

  # cv2.imshow('yolo_detected_img', cv2.imread(out_img))  
  # cv2.waitKey(0)  
  # cv2.destroyAllWindows()  


def detect_img_list(save_mode, route_id, out_dir):
  net, meta = load_yolo_net()

  in_dir = "./dataProcess/img_keep"

  """如果是save_mode�?，则in_dir里面除了视频还有GPS文件"""

  ###############
  init_mymmap()
  setValueToMmap(2)
  ################


  while True:
    if getVauleFromMmap() == 3:
      break
    img_list = os.listdir(in_dir)
    img_num = len(img_list)
  
    for img_self_name in img_list:
      if os.path.splitext(img_self_name)[1] in [".jpg", ".JPG", ".JPEG", ".png", ".PNG", ".bmp"]:
        img_name = os.path.join(in_dir, img_self_name)
        out_img_name = out_dir + img_self_name
        print("img_name: ", img_name)
        print("out_img_name: ", out_img_name)
        im = cv2.imread(img_name)
	if im is None:
		print("none none none none ")
		os.remove(img_name)
		continue
        detect_infer(net, meta, img_name, out_img_name, save_mode, route_id)
        #print("succeed to detect **********************************************")
      	#@os.remove("./dataProcess/img_keep/"+img_self_name)

  setValueToMmap(4)
  return 0


# if __name__ == "__main__":

#     parser = argparse.ArgumentParser(description='yolo_detect')
#     parser.add_argument('--OutputDir', dest='OutputDir', default="../Output/", help="save results to OutputDir")
#     args = parser.parse_args()

#     save_mode = 0
#     detect_img_list(save_mode, args.OutputDir)


