#! /bin/bash
less /etc/sysctl.conf
sysctl -w net.core.somaxconn=511
sysctl vm.overcommit_memory=1
redis-server --daemonize yes
