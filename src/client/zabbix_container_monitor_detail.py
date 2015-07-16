#-*- coding: utf-8 -*-

'''
Created on 2013-7-21

@author: asus
'''

import urllib2
import logging
import json
import datetime
import time

MCLUSTER_VIP = 'localhost'
TIME_FORMAT = '%Y-%m-%d %H:%M:%S'
WARNING_TIME_DIFF = 360

def check_monitor_detail(serious_dict, general_dict, nothing_dict):
    url = "http://%s:6666/monitor/status" % (MCLUSTER_VIP)
    f = urllib2.urlopen(url)
    encodedjson =  f.read()
    monitor_return_json_value = json.loads(encodedjson)
    
    reponse_code = monitor_return_json_value['meta']['code']
    if reponse_code != 200:
        serious_dict.setdefault(url, "due to response code error, please check email to find the reason!")
        return
    
    response_value = monitor_return_json_value['response']
    
    for monitor_type in response_value:
        for monitor_item in response_value[monitor_type]:
            monitor_type_item = monitor_type + "." + monitor_item
            return_code = response_value[monitor_type][monitor_item]['alarm']
            error_record = response_value[monitor_type][monitor_item]['error_record']
            return_message = response_value[monitor_type][monitor_item]['message']
            if error_record:
                error_record = ", error_record=%s" % str(error_record)
                return_message += str(error_record)
            create_time_str = response_value[monitor_type][monitor_item]['ctime']
            t = time.strptime(create_time_str, TIME_FORMAT)
            create_time = datetime.datetime(*t[:6]) 
#            print str(create_time)
            
            check_time = datetime.datetime.now()
#            print str(check_time)
            diff = (check_time-create_time).seconds
#            print diff
            
            if diff > WARNING_TIME_DIFF:
                serious_dict.setdefault(monitor_type_item,"please check async api, the data is out of date!")
            elif return_code == 'tel:sms:email':
                serious_dict.setdefault(monitor_type_item, return_message)
            elif return_code == 'sms:email':
                general_dict.setdefault(monitor_type_item, return_message)
            else:
                nothing_dict.setdefault(monitor_type_item, return_message)
    
    
def main():
    serious_dict = {}
    
    general_dict = {}
    
    nothing_dict = {}
    
    check_monitor_detail(serious_dict, general_dict, nothing_dict)
    
    print "detail_serious:%s" % serious_dict
    print "detail_general:%s" % general_dict
    print "detail_nothing:%s" % nothing_dict

if __name__ == "__main__":
    main()
