import json
with open('my.json',mode='r') as f1:
	setting = json.load(f1)
	for i in setting:
		if setting[i]:
			print(setting[i])
	
