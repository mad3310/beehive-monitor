#!/bin/bash

chmod +x /etc/init.d/container-monitor-agent
chkconfig --add container-monitor-agent
/etc/init.d/container-monitor-agent start | stop | restart

exit 0
