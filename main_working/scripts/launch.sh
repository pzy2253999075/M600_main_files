#!/bin/sh
### BEGIN INIT INFO
# Provides:          land.sh
# Required-start:    $local_fs $remote_fs $network $syslog
# Required-Stop:     $local_fs $remote_fs $network $syslog
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: starts the svnd.sh daemon
# Description:       starts svnd.sh using start-stop-daemon
### END INIT INFO

#gnome-terminal -t "m600_air_node" -x bash -c "roscore;exec bash";
echo dji| sudo -S usb_modeswitch -v 12d1 -p 1f01 -J
gnome-terminal -t "onboard_sdk_node" -x bash -c "source ~/DJI_Onboard_Sdk/devel/setup.bash;roslaunch dji_sdk sdk.launch;exec bash";
gnome-terminal -t "m600_air_node" -x bash -c "source ~/DJI_Onboard_Sdk/devel/setup.bash;rosrun dji_sdk m600_air;exec bash";
gnome-terminal -t "m600_gim_driver" -x bash -c "source ~/DJI_Onboard_Sdk/devel/setup.bash;rosrun dji_sdk m600_gimbal;exec bash";
gnome-terminal -t "m600_video_record" -x bash -c "source ~/DJI_Onboard_Sdk/devel/setup.bash;python /home/dji/DJI_Onboard_Sdk/src/Onboard-SDK-ROS/dji_sdk/scripts/video_record/m600_video.py;exec bash";
gnome-terminal -t "m600_script_ctr" -x bash -c "source ~/DJI_Onboard_Sdk/devel/setup.bash;python /home/dji/DJI_Onboard_Sdk/src/Onboard-SDK-ROS/dji_sdk/scripts/fu_script_ctr.py;exec bash";
sleep 10;
gnome-terminal -t "m600_video_src" -x bash -c "source ~/VideoStream/devel/setup.bash;roslaunch video_stream_opencv camera.launch;exec bash";






















