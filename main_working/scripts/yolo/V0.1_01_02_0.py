# -*- coding: utf-8 -*-
# --------------------------------------------------------

import os
import time
import argparse
import shutil
import sys
#sys.path.append("/home/dji/DJI_Onboard_Sdk/src/Onboard-SDK-ROS/dji_sdk/script/V0.1_01_02_0/")
sys.path.append("./dataProcess/")
import dataProcess
sys.path.append("./yoloDetect_v0.1/")
import yolo_detect
import threading
import mmap 


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

def save_mode_thread(args):
    while(True):
        if getVauleFromMmap() == 3 or getVauleFromMmap() == 4:
            break;
        dataProcess.dataProcess(args)
	time.sleep(10)
  
        

if __name__ == "__main__":

    init_mymmap()
    parser = argparse.ArgumentParser()

    parser.add_argument('--InputDir', default="./input/", required = True, help="keep imgs or video in InputDir")
    parser.add_argument('--OutputDir', default="./output/", required = True, help="save results to OutputDir")
    parser.add_argument('--Route_ID', default="123456789", required = True, help="Route_ID")


    args = parser.parse_args()
    print("args: ", args)

    index = -1
    save_mode = 1

    dataProcessThread = threading.Thread(target = save_mode_thread,args=[args.InputDir,])
    yolo_detect_thread = threading.Thread(target = yolo_detect.detect_img_list,args=[save_mode, args.Route_ID, args.OutputDir,])
    yolo_detect_thread.start()
    dataProcessThread.start()
    
   
    yolo_detect_thread.join()
    #save_mode = dataProcess.dataProcess(args.InputDir)
    #print("save_mode: ", save_mode)
    #index = yolo_detect.detect_img_list(save_mode, args.Route_ID, args.OutputDir)
    dataProcessThread.join()
    if index == 0:
        shutil.rmtree("./dataProcess/img_ori/")
        os.mkdir("./dataProcess/img_ori/")
        shutil.rmtree("./dataProcess/img_keep/")
        os.mkdir("./dataProcess/img_keep/")
        shutil.rmtree("./yoloDetect_v0.1/out_img/")
        os.mkdir("./yoloDetect_v0.1/out_img/")
        shutil.rmtree("./input/")
        os.mkdir("./input/")


    










