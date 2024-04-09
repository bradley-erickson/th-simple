#! /bin/bash
less /etc/sysctl.conf
sysctl -a
sysctl -w net.core.somaxconn=512
sysctl -w vm.overcommit_memory=1
sysctl -p
sysctl -a
redis-server --daemonize yes
