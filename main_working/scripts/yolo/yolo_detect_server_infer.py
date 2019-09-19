# -*- coding: utf-8 -*-
# --------------------------------------------------------
from __future__ import division
from ctypes import *
import os
import time
import math
import random
import cv2
import json
import exifread

CUSTOM = "illegalBuilding"
CLS_NAME = ["roof_illegal", "stock_land"]

NAME_DATA = os.path.split(__file__)[0] + "/darknet/cfg/" + "illegalBuilding.data"
YOLO_CFG = os.path.split(__file__)[0] + "/darknet/cfg/" + "yolov3-illegalBuilding.cfg"
YOLO_WEIGHTS = os.path.split(__file__)[0] + "/darknet/backup/" + "illegalBuilding/yolov3-illegalBuilding_2000.weights"

def sample(probs):
    s = sum(probs)
    probs = [a/s for a in probs]
    r = random.uniform(0, 1)
    for i in range(len(probs)):
        r = r - probs[i]
        if r <= 0:
            return i
    return len(probs)-1

def c_array(ctype, values):
    arr = (ctype*len(values))()
    arr[:] = values
    return arr

class BOX(Structure):
    _fields_ = [("x", c_float),
                ("y", c_float),
                ("w", c_float),
                ("h", c_float)]

class DETECTION(Structure):
    _fields_ = [("bbox", BOX),
                ("classes", c_int),
                ("prob", POINTER(c_float)),
                ("mask", POINTER(c_float)),
                ("objectness", c_float),
                ("sort_class", c_int)]


class IMAGE(Structure):
    _fields_ = [("w", c_int),
                ("h", c_int),
                ("c", c_int),
                ("data", POINTER(c_float))]

class METADATA(Structure):
    _fields_ = [("classes", c_int),
                ("names", POINTER(c_char_p))]

    
lib = CDLL(os.path.split(__file__)[0] + "/darknet/libdarknet.so", RTLD_GLOBAL)
lib.network_width.argtypes = [c_void_p]
lib.network_width.restype = c_int
lib.network_height.argtypes = [c_void_p]
lib.network_height.restype = c_int

predict = lib.network_predict
predict.argtypes = [c_void_p, POINTER(c_float)]
predict.restype = POINTER(c_float)

set_gpu = lib.cuda_set_device
set_gpu.argtypes = [c_int]

make_image = lib.make_image
make_image.argtypes = [c_int, c_int, c_int]
make_image.restype = IMAGE

get_network_boxes = lib.get_network_boxes
get_network_boxes.argtypes = [c_void_p, c_int, c_int, c_float, c_float, POINTER(c_int), c_int, POINTER(c_int)]
get_network_boxes.restype = POINTER(DETECTION)

make_network_boxes = lib.make_network_boxes
make_network_boxes.argtypes = [c_void_p]
make_network_boxes.restype = POINTER(DETECTION)

free_detections = lib.free_detections
free_detections.argtypes = [POINTER(DETECTION), c_int]

free_ptrs = lib.free_ptrs
free_ptrs.argtypes = [POINTER(c_void_p), c_int]

network_predict = lib.network_predict
network_predict.argtypes = [c_void_p, POINTER(c_float)]

reset_rnn = lib.reset_rnn
reset_rnn.argtypes = [c_void_p]

load_net = lib.load_network
load_net.argtypes = [c_char_p, c_char_p, c_int]
load_net.restype = c_void_p

do_nms_obj = lib.do_nms_obj
do_nms_obj.argtypes = [POINTER(DETECTION), c_int, c_int, c_float]

do_nms_sort = lib.do_nms_sort
do_nms_sort.argtypes = [POINTER(DETECTION), c_int, c_int, c_float]

free_image = lib.free_image
free_image.argtypes = [IMAGE]

letterbox_image = lib.letterbox_image
letterbox_image.argtypes = [IMAGE, c_int, c_int]
letterbox_image.restype = IMAGE

load_meta = lib.get_metadata
lib.get_metadata.argtypes = [c_char_p]
lib.get_metadata.restype = METADATA

load_image = lib.load_image_color
load_image.argtypes = [c_char_p, c_int, c_int]
load_image.restype = IMAGE

rgbgr_image = lib.rgbgr_image
rgbgr_image.argtypes = [IMAGE]

predict_image = lib.network_predict_image
predict_image.argtypes = [c_void_p, IMAGE]
predict_image.restype = POINTER(c_float)


def getExifGPS(file_name):
    GPS = [0 for i in range(3)]
    fd = open(file_name, 'rb')
    tags = exifread.process_file(fd)
    fd.close()
    """显示图片所有的exif信息"""
    #print("showing res of getExif: \n")
    for tag, value in tags.items():
        #print("tag: ", tag, "value: ", value)
        # if re.match('Image Make', tag):
        #     print(value)
        # if re.match('Image DateTime', tag):
        #     print(value)
        if tag == "GPS GPSLatitude":
            #print(type(value), value)
            value = str(value)[1 : (len(str(value))-1)]
            value = value.split(',')
            # print(value[0].find('/'))
            # print(value[1].find('/'))
            # print(value[2].find('/'))
            if value[0].find('/') != -1:
                value0 = value[0].split('/')
                value0 = float(value0[0])/float(value0[1])
            else:
                value0 = float(value[0])
            #print(value0)                
            if value[1].find('/') != -1:
                value1 = value[1].split('/')
                value1 = float(value1[0])/float(value1[1])
            else:
                value1 = float(value[1])
            #print(value1)             
            if value[2].find('/') != -1:
                value2 = value[2].split('/')
                value2 = float(value2[0])/float(value2[1])
            else:
                value2 = float(value[2])
            #print(value2)             
            GPS[0] = round(value0 + value1/60 + value2/3600, 2)
        if tag == "GPS GPSLongitude":
            # print(type(value), value)
            value = str(value)[1 : (len(str(value))-1)]
            value = value.split(',')
            # print(value[0].find('/'))
            # print(value[1].find('/'))
            # print(value[2].find('/'))
            if value[0].find('/') != -1:
                value0 = value[0].split('/')
                value0 = float(value0[0])/float(value0[1])
            else:
                value0 = float(value[0])
            #print(value0)                
            if value[1].find('/') != -1:
                value1 = value[1].split('/')
                value1 = float(value1[0])/float(value1[1])
            else:
                value1 = float(value[1])
            #print(value1)             
            if value[2].find('/') != -1:
                value2 = value[2].split('/')
                value2 = float(value2[0])/float(value2[1])
            else:
                value2 = float(value[2])
            #print(value2)             
            GPS[1] = round(value0 + value1/60 + value2/3600, 2)
        if tag == "GPS GPSAltitude":
            #print(type(value), value)
            value = str(value)
            if value.find('/') != -1:
                value = value.split('/')
                value = float(value[0])/float(value[1])
            else:
                value = float(value)
            #print("value: ", value)
            GPS[2] = round(value, 2)
    return GPS
        

def save_pic_and_json(in_img_name, out_img_name, res, cls_name, save_mode, route_id):  

    if save_mode == 0:
        GPS_name = os.path.splitext(in_img_name)[0] + ".txt"
        print("GPS_name: ", GPS_name)
        try:
            with open(GPS_name, "r") as f:
                GPS = f.readline()
                GPS = GPS.split(",")
        except IOError:
            GPS = [0, 0, 0]

    print("save_mode: ", save_mode)
    #if save_mode == 1:
	#print("11111111111111111111111111111111111111111111111111111111111111111")
    GPS = getExifGPS(in_img_name)
	#print("222222222222222222222222222222222222222222222222222222222222222222")
    #print("GPS: ", GPS)

    class_det_num = [0 for i in range(len(cls_name))]
    scale_size = 640

    a = time.time()
    try:
	#print("##################################################################################")
	#print(in_img_name)
    	img = cv2.imread(in_img_name)
    except cv2.error as e:
	print(e)
	print("cv2 error")
	return 0
    b = time.time()
    #print("imread: {:.3f}s".format(b-a))

    #scale_size = 640
    #h_scale = img.shape[0] / scale_size
    #w_scale = img.shape[1] / scale_size
    scale_index = 1
    w_scale_size = int(img.shape[1] / scale_index)
    h_scale_size = int(img.shape[0] / scale_index)
    w_scale = scale_index
    h_scale = scale_index

    c = time.time()
    resize_img = cv2.resize(img, (w_scale_size, h_scale_size))
    d = time.time()
    #print("resize: {:.3f}s".format(d-c))

    out_img_temp_name = os.path.split(__file__)[0] + "/out_img/" + os.path.split(in_img_name)[1]
    print("out_img_temp_name: ", out_img_temp_name)

    e = time.time()
    cv2.imwrite(out_img_temp_name, resize_img)  
    f = time.time()
    #print("imwrite: {:.3f}s".format(f-e))

    det_num = len(res)
    # print("res: ", res)    
    for i in range(det_num):
	print("score: ", res[i][1])
	
        """cv2.rectange 会持续保存之前画过的内容"""
        im = cv2.imread(out_img_temp_name)
	#print(im)
	#print("99999999999999999999999")
        """Python 3 新增\E4\BA?bytes 类型，用于代表字节串,字节串（bytes）由多个字节组成,以字节为单位进行操作,可以与str之间相互转换"""
        if res[i][0] == cls_name[0].encode("utf-8"):
            class_det_num[0] +=1
            x1=(res[i][2][0]-res[i][2][2]/2)/w_scale  
            y1=(res[i][2][1]-res[i][2][3]/2)/h_scale  
            x2=(res[i][2][0]+res[i][2][2]/2)/w_scale
            y2=(res[i][2][1]+res[i][2][3]/2)/h_scale  
            #im = cv2.imread(out_img_name)  
            cv2.rectangle(im, (int(x1),int(y1)), (int(x2),int(y2)), (0,0,255), 3) 
	    #print(im)
	    #print("7777777777777777777777") 
            #This is a method that works well.   
            #cv2.imwrite(out_img_name, im)  
        if res[i][0].decode("utf-8") == cls_name[1]:
            class_det_num[1] += 1
            x1=(res[i][2][0]-res[i][2][2]/2)/w_scale  
            y1=(res[i][2][1]-res[i][2][3]/2)/h_scale  
            x2=(res[i][2][0]+res[i][2][2]/2)/w_scale    
            y2=(res[i][2][1]+res[i][2][3]/2)/h_scale   
            cv2.rectangle(im, (int(x1),int(y1)), (int(x2),int(y2)), (0,0,255), 3)

        out_img_sub_name_no_ext = os.path.splitext(out_img_name)[0]
        out_img_sub_name_no_ext = out_img_sub_name_no_ext[:(len(out_img_sub_name_no_ext)-2)]
        out_img_sub_name = out_img_sub_name_no_ext + "_" + str(i+1) + "_N" + '.jpg'
        print("out_img_sub_name: ", out_img_sub_name)
	#print("im_info: ", im)
	if im:
            cv2.imwrite(out_img_sub_name, im)
       
        json_sub_name = out_img_sub_name_no_ext + "_" + str(i+1) + '.json'
        print("json_sub_name: ", json_sub_name)
        json_sub_self_name = os.path.split(json_sub_name)[1]
        json_sub_self_name_no_ext = os.path.splitext(json_sub_self_name)[0]
   	 
        json_dict = {
            "JSON_ID":json_sub_self_name_no_ext, "Image_Stream_N":out_img_sub_name, "GPS":GPS, 
            "N_Obj":res[i][0].decode("utf-8"), "C_Obj":round(res[i][1],4), 
            "LOC_Obj":{"N_x":int(res[i][2][0]), "N_y":int(res[i][2][1]), "N_w":int(res[i][2][2]), "N_h":int(res[i][2][3])},
            "Route_ID":route_id
            }
        #print("json_dict: ", json_dict)
        """convert dict to str"""
        json_str = json.dumps(json_dict)
        with open(json_sub_name, "w") as f:
	    if json_str and im:
                f.write(json_str)
            f.close
    
 
    #cv2.imwrite(out_img_name, im)  

    #cv2.imshow('yolo_det_img', cv2.imread(out_img_name))  
    #cv2.waitKey(0)  
    #cv2.destroyAllWindows()

    return class_det_num


def load_yolo_net():

    net = load_net(YOLO_CFG.encode("utf-8"), YOLO_WEIGHTS.encode("utf-8"), 0)
    meta = load_meta(NAME_DATA.encode("utf-8"))

    return net, meta



def detect_infer(net, meta, in_img_name, out_img_name, save_mode, route_id, thresh=0.1, hier_thresh=.5, nms=.45):
    
    res = []
    a = time.time()
    im = load_image(in_img_name.encode("utf-8"), 0, 0)
    print("im.shape: ", im.w, im.h)
    if im.w == 0 and im.h ==0:
	print("####################***************#################****************##############***********")
	return res
    b = time.time()
    print("read and resize image spend: {:.3f}s".format(b-a))

    num = c_int(0)
    pnum = pointer(num)
    print("start to detect!")
    c = time.time()
    predict_image(net, im)
    dets = get_network_boxes(net, im.w, im.h, thresh, hier_thresh, None, 0, pnum)
    d = time.time()
    print("net forward spend: {:.3f}s".format(d-c))

    num = pnum[0]
    if (nms): 
        do_nms_obj(dets, num, meta.classes, nms);

  #  res = []
    for j in range(num):
        for i in range(meta.classes):
            if dets[j].prob[i] > 0:
                b = dets[j].bbox
                res.append((meta.names[i], dets[j].prob[i], (b.x, b.y, b.w, b.h)))
    res = sorted(res, key=lambda x: -x[1])
    
    e = time.time()
    class_det_num = save_pic_and_json(in_img_name, out_img_name, res, CLS_NAME, save_mode, route_id)
    f = time.time()
    print("save image spend: {:.3f}s".format(f-e))
    
    for i, value in enumerate(class_det_num):
        print(CLS_NAME[i], value)
    

    free_image(im)
    free_detections(dets, num)
    
    return res

    











