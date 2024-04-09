sysctl -w net.core.somaxconn=512
sysctl vm.overcommit_memory=1
redis-server --daemonize yes
