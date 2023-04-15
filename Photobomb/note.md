Hack The Box : Photobomb

**Inital Scan**

22/tcp open  ssh     OpenSSH 8.2p1 Ubuntu 4ubuntu0.5 (Ubuntu Linux; protocol 2.0)   
80/tcp open  http    nginx 1.18.0 (Ubuntu

Identified os version : **Ubuntu focal 20.4**

Port 80 is running a ruby based sinatra framework webapplication
referance:[https://sinatrarb.com/](https://sinatrarb.com/)

Creds from photobomb.js
```javascript
function init() {
  // Jameson: pre-populate creds for tech support as they keep forgetting them and emailing me
  if (document.cookie.match(/^(.*;)?\s*isPhotoBombTechSupport\s*=\s*[^;]+(.*)?$/)) {
    document.getElementsByClassName('creds')[0].setAttribute('href','http://pH0t0:b0Mb!@photobomb.htb/printer');
  }
}
window.onload = init;
```
```bash
http://pH0t0:b0Mb!@photobomb.htb/printer
```
Foothold

After login their is a download funtion and some options to customzie the photo
like dimientions,filetype.

Looking the download request the filetype parameter is vuln to blind RCE

I wrote a python script to injection the code and get a shell back to us

added to this repo **photobomob-rce.py**
