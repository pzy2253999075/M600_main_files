#ffmpeg -i /dev/video0 -f flv  "rtmp://send3a.douyu.com/live/976948rsDWcEbFyY?wsSecret=61d5a86470678bd04cb3a86557f6926e&wsTime=5d6c9f66&wsSeek=off&wm=0&tw=0&roirecognition=0"
#ffmpeg -i output.avi -vcodec libx264 -s 480*320 -b:v 800k -bufsize 2000k -f flv  "rtmp://send3a.douyu.com/live/976948rezLzVtZbw?wsSecret=bbbf5897b202b29914fdfa8cbc4ce846&wsTime=5d6c70cf&wsSeek=off&wm=0&tw=0&roirecognition=0"
#ffmpeg -i /dev/video0 -s 640*480 -vcodec libx264 -r 10 output.mp4
#ffmpeg -re -i ./output.mp4 -vcodec libx264 -acodec aac -strict -2 -b:v 2000k -f flv "rtmp://send3a.douyu.com/live/97694rtmp://www.binyx.vip:1935/stream/m6008rezLzVtZbw?wsSecret=bbbf5897b202b29914fdfa8cbc4ce846&wsTime=5d6c70cf&wsSeek=off&wm=0&tw=0&roirecognition=0"
ffmpeg -i /dev/video0 -f flv "rtmp://www.binyx.vip:1935/stream/m600"
