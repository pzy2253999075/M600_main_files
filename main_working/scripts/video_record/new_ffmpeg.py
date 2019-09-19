import ffmpeg
process  = ( 
	ffmpeg.input('pipe:',format = 'rawvideo', pix_fmt = 'rgb24',s ='{}x{}'.format(1920,1080))
	.output('rtmp://pushlive.binyx.vip/live/m600?txSecret=f5809039373e5a9431ee76d8f947cd34&txTime=5D9F557F',pix_fmt = 'yuv420p',format = 'h264',preset = 'ultrafast',b= '2000k')
	.overwrite_output().run_async(pipe_stdin =True)
)





































