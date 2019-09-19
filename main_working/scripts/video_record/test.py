import subprocess
import os
import re

#def pingThread():
#	subprocess.Popen("ping www.baidu.com -c",shell = True,preexec_fn = os.setsid)
	
res = os.popen("ping www.baidu.com -w 3")
res1 = res.read()
totally_lost = True
print(res1)
for line in res1.splitlines():
	ifmatch = re.match(r'rtt.*=.*/(.*)/.*/.*',line)
	if ifmatch:
		print( ifmatch.group(1))
		totally_lost = False
if totally_lost == True:
	print("totally_lost")
			




















































































