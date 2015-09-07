#-*- coding: utf-8 -*-
import os

from tornado.options import define

join = os.path.join
dirname = os.path.dirname

base_dir = os.path.abspath(dirname(dirname(__file__)))

define('port', default = 6666, type = int, help = 'app listen port')
define('debug', default = False, type = bool, help = 'is debuging?')
define('sitename', default = "container manager", help = 'site name')
define('domain', default = "letv.com", help = 'domain name')

define('send_email_switch', default = True, type = bool, help = 'the flag of if send error email')
define('admins', default = ("xuyanwei <xuyanwei@letv.com>","zhoubingzheng <zhoubingzheng@letv.com>", "zhangzeng <zhangzeng@letv.com>",), help = 'admin email address')
define('smtp_host', default = "10.205.91.22", help = 'smtp host')
define('smtp_port', default = 587, help = 'smtp port')
define('smtp_user', default = "mcluster", help = 'smtp user')
define('smtp_password', default = "Mcl_20140903!", help = 'smtp password')
define('smtp_from_address', default='mcluster@letv.com', help = 'smtp from address')
define('smtp_duration', default = 10000, type = int, help = 'smtp duration')
define('smtp_tls', default = False, type = bool, help = 'smtp tls')


define("base_dir", default=base_dir, help="project base dir")
define("container_manager_property",default=join(base_dir, "config","containerMonitorAgent.property"), help="container manager config file")
define("data_node_property",default=join(base_dir,"config","dataNode.property"), help="data node config file")
define("server_cluster_property",default=join(base_dir,"config","serverCluster.property"), help="server cluster config file")


define("alarm_serious", default="tel:sms:email", help="alarm level is serious")
define("alarm_general", default="sms:email", help="alarm level is general")
define("alarm_nothing", default="nothing", help="no alarm")

define("disk_number_sh", default=join(base_dir, "shell", "disk_number.sh"), help="get disk number script")
define("network_io_sh", default=join(base_dir, "shell", "network_io.sh"), help="get network io script")