#!/bin/bash

abs_path="/home/dji/DJI_Onboard_Sdk/src/Onboard-SDK-ROS/dji_sdk/scripts/V0.1_01_02_0/"
echo $abs_path"/dataProcess"

if [ ! -d $abs_path"/dataProcess" ] || [ ! -d $abs_path"/yoloDetect_v0.1" ] || [ ! -d $abs_path"/input" ] || [ ! -d $abs_path"/output" ];then
	echo "lack necessary dir!" 
	exit 1
else
	echo "find the necessary dir!"
fi

if [ ! -f $abs_path"/V0.1_01_02_0.py" ];then
	echo "lack necessary file!" 
	exit 1
else
	echo "find the necessary file!"
fi


# echo "download data to Input from UAV!"

# download_dir=$1

# wget -O $abs_path"/input/download_data.tar" $download_dir
# #tar -xvf $abs_path/input/download_data.tar ./input
# cd $abs_path/input
# tar -xvf download_data.tar
# rm download_data.tar
# cd ../

# if [ $# -ne 3 ];then
# 	echo "the number of parameters is wrong!"
# 	exit 1
# else
# 	if [ ! -d ./input/ ] || [ ! -d ./output/ ];then
# 		echo "the content of parameters is wrong!"
# 		exit 1
# 	else
# 		echo "run the py-program"
# 		python V0.1_01_02_0.py --InputDir ./input/ --OutputDir ./output/ --Route_ID $3  
# 	fi
# fi


# echo "upload data fome Output to UAV!"

# upload_dir=$2
# #python upload_server.py ./output $upload_dir





echo "download data to Input from UAV!"

#download_dir="http://172.31.226.82:9001/group1/M00/00/BE/wKgADV1o4lmALSx6BGaEKATgXws158.tar"

#wget -O $abs_path"/input/download_data.tar" $download_dir
#tar -xvf ./input/download_data.tar ./input
cd $abs_path/input
#tar -xvf download_data.tar
#rm download_data.tar
cd ../


if [ $# -ne 3 ];then
	echo "the number of parameters is wrong!"
	exit 1
else
	if [ $1 != "InputDir" ] || [ $2 != "OutputDir" ] || [ $3 != "Route_ID" ];then
		echo "the content of parameters is wrong!"
		exit 1
	else
		echo "run the py-program"
		python V0.1_01_02_0.py --$1 ./input/ --$2 ./output/ --$3 "000168074259e9ab6187a9d4442da280" 
	fi
fi



#echo "upload data fome Output to UAV!"
#upload_dir="http://172.31.226.82:8004/plep/api/kafka/send/push_warning_addition"
#python upload_server.py ./output $upload_dir















