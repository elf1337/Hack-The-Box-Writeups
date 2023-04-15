#HackTheBox: Soccer

Default nmap 1000 tcp port scan
```bash
22/tcp   open  ssh             OpenSSH 8.2p1 Ubuntu 4ubuntu0.5 (Ubuntu Linux; protocol 2.0)
80/tcp   open  http            nginx 1.18.0 (Ubuntu)
9091/tcp open  xmltec-xmlmail?
```

Services:
# HTTP - [port 80]
Hostname: soccer.htb
fuzzing hidden-diretorys we get a file manager name 'tiny'
tiny - an opensource filemanager based on php
referance: https://tinyfilemanager.github.io/
docs: https://github.com/prasathmani/tinyfilemanager/wiki/Security-and-User-Management
Default username/password:

    admin/admin@123
    user/12345
# Foothold
upload a webshell gain shell on the target

# 9091
websocket 

# soc-player.soccer.htb
register account and signup
This is site use websocket for check confirming tickets through websocket running port 9091
websocket is vulnerable to blind-boolem-based-sqlinjection on id paramter
### Injection
Setup a local http server running on port 8081 which recevie payloads through id parameter from sqlmap and exract the value.send to the websocket and get back the result to sqlmap 

enumerate databases 
databaseName - 'soccer_db'
Columns  - id,email,username,password
Retrive username and passsword
player:PlayerOftheMatch2022

#ssh
take ssh as user player

#privilege escalation 
While searching for setuid file on this machine. we found an interesting one "doas"
(doas a dedicated openbsd application subexecutor is a program to execute commands as another user. The system administrator can configure it to give specified users privileges to execute specified commands). checking for the conf file of doas which has located on this box at /usr/local/etc/doas.conf tipically it has found on /etc/doas.conf. it has been configured to run /usr/bin/dstat as root "permit nopass player as root cmd /usr/bin/dstat".Dstat allows you to view all of your system resources instantly.

#exploit
we can create coustom python plugins for dstat
create a python script at /usr/local/share/dstat/dstat_pe.py
Run with doas to execute the script
doas /usr/bin/dstat --pe

