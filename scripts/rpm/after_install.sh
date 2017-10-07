#!/bin/bash

chmod +x /etc/init.d/beehive-monitor
chkconfig --add beehive-monitor
/etc/init.d/beehive-monitor start | stop | restart

exit 0
