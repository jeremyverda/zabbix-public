#!/usr/bin/env python3
'''
Author : Jeremy Verda
URL : jeremyverda.net
Description : 
This module is intended to get the Pure Storage Array monitoring information : 
    * Writes per second
    * Microsecond per write operation
    * Output per second
    * San Microsecond per read operation
    * Read per second
    * Input per second
    * Microsecond per read operation
    * San microsecond per write operation
    * Queue depth
'''
import purestorage
import urllib3
import sys
import subprocess
import os 

'''Get the argument from Zabbix'''
ip = str(sys.argv[1]) #IP of the Pure Storage Array
token = str(sys.argv[2]) #API Token
host = str(sys.argv[3]) #Host name (for the sender)
zabbixIP = str(sys.argv[4]) #Zabbix Proxy or Server IP (for the sender)

'''
Disable the SSL Warning from the output
'''
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

'''Get data'''
arrayConnect = purestorage.FlashArray(ip,api_token=token)
arrayMonitoring = arrayConnect.get(action="monitor")

'''Export data'''
arrayValues = arrayMonitoring[0]
arrayInputPerSec = str(arrayValues["input_per_sec"])
arrayOutputPerSec = str(arrayValues["output_per_sec"])
arrayQueueDepth = str(arrayValues["queue_depth"])
arrayReadPerSec = str(arrayValues["reads_per_sec"])
arraySanUsecPerReadOp = str(arrayValues["san_usec_per_read_op"])
arraySanUsecPerWriteOp = str(arrayValues["san_usec_per_write_op"])
arrayUsecPerReadOp = str(arrayValues["usec_per_read_op"])
arrayUsecPerWriteOp = str(arrayValues["usec_per_write_op"])
arrayWritePerSec = str(arrayValues["writes_per_sec"])

'''Will disable the output to console'''
FNULL = open(os.devnull, 'w')

'''Send data'''
subprocess.call(["zabbix_sender","-z",zabbixIP,"-s",host,"-k","pure.array.input.per.second","-o",arrayInputPerSec],stdout=FNULL,stderr=subprocess.STDOUT)
subprocess.call(["zabbix_sender","-z",zabbixIP,"-s",host,"-k","pure.array.output.per.second","-o",arrayOutputPerSec],stdout=FNULL,stderr=subprocess.STDOUT)
subprocess.call(["zabbix_sender","-z",zabbixIP,"-s",host,"-k","pure.array.queue.depth","-o",arrayQueueDepth],stdout=FNULL,stderr=subprocess.STDOUT)
subprocess.call(["zabbix_sender","-z",zabbixIP,"-s",host,"-k","pure.array.read.per.sec","-o",arrayReadPerSec],stdout=FNULL,stderr=subprocess.STDOUT)
subprocess.call(["zabbix_sender","-z",zabbixIP,"-s",host,"-k","pure.array.san.usec.per.read","-o",arraySanUsecPerReadOp],stdout=FNULL,stderr=subprocess.STDOUT)
subprocess.call(["zabbix_sender","-z",zabbixIP,"-s",host,"-k","pure.array.san.usec.per.write","-o",arraySanUsecPerWriteOp],stdout=FNULL,stderr=subprocess.STDOUT)
subprocess.call(["zabbix_sender","-z",zabbixIP,"-s",host,"-k","pure.array.usec.per.read","-o",arrayUsecPerReadOp],stdout=FNULL,stderr=subprocess.STDOUT)
subprocess.call(["zabbix_sender","-z",zabbixIP,"-s",host,"-k","pure.array.usec.per.write","-o",arrayUsecPerWriteOp],stdout=FNULL,stderr=subprocess.STDOUT)
subprocess.call(["zabbix_sender","-z",zabbixIP,"-s",host,"-k","pure.array.write.per.sec","-o",arrayWritePerSec],stdout=FNULL,stderr=subprocess.STDOUT)

'''Send 1 to give a result to Zabbix'''
print(1)