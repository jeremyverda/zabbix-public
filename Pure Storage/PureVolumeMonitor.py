#!/usr/bin/env python3
'''
Author : Jeremy Verda
URL : jeremyverda.net
Description :
This module is intended to get the Pure Storage volume monitoring information : 
    * Writes per second
    * Microsecond per write operation
    * Output per second
    * San Microsecond per read operation
    * Read per second
    * Input per second
    * Microsecond per read operation
    * San microsecond per write operation
'''
import purestorage
import urllib3
import sys
import subprocess
import os

try:
    '''Get the argument from Zabbix'''
    ip = str(sys.argv[1]) #IP of the Pure Storage Array
    token = str(sys.argv[2]) #API Token
    volume = str(sys.argv[3]) #Volume Name
    host = str(sys.argv[4]) #Host name (for the sender)
    zabbixIP = str(sys.argv[5]) #Zabbix Proxy or Server IP (for the sender)

    '''
    Disable the SSL Warning from the output
    '''
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    '''Get data'''
    arrayConnect = purestorage.FlashArray(ip,api_token=token)
    volumeMonitoring = arrayConnect.get_volume(volume=volume,action="monitor")
    volumeInfo = arrayConnect.get_volume(volume=volume)

    '''Export data'''
    arrayValues = volumeMonitoring[0]
    arrayInputPerSec = str(arrayValues["input_per_sec"])
    arrayOutputPerSec = str(arrayValues["output_per_sec"])
    arrayReadPerSec = str(arrayValues["reads_per_sec"])
    arraySanUsecPerReadOp = str(arrayValues["san_usec_per_read_op"])
    arraySanUsecPerWriteOp = str(arrayValues["san_usec_per_write_op"])
    arrayUsecPerReadOp = str(arrayValues["usec_per_read_op"])
    arrayUsecPerWriteOp = str(arrayValues["usec_per_write_op"])
    arrayWritePerSec = str(arrayValues["writes_per_sec"])
    arrayVolumeSize = str(volumeInfo["size"])

    '''Will disable the output to console'''
    FNULL = open(os.devnull, 'w')

    '''Send data'''
    subprocess.call(["zabbix_sender","-z",zabbixIP,"-s",host,"-k","pure.volume.input.per.second["+volume+"]","-o",arrayInputPerSec],stdout=FNULL,stderr=subprocess.STDOUT)
    subprocess.call(["zabbix_sender","-z",zabbixIP,"-s",host,"-k","pure.volume.output.per.second["+volume+"]","-o",arrayOutputPerSec],stdout=FNULL,stderr=subprocess.STDOUT)
    subprocess.call(["zabbix_sender","-z",zabbixIP,"-s",host,"-k","pure.volume.read.per.sec["+volume+"]","-o",arrayReadPerSec],stdout=FNULL,stderr=subprocess.STDOUT)
    subprocess.call(["zabbix_sender","-z",zabbixIP,"-s",host,"-k","pure.volume.san.usec.per.read["+volume+"]","-o",arraySanUsecPerReadOp],stdout=FNULL,stderr=subprocess.STDOUT)
    subprocess.call(["zabbix_sender","-z",zabbixIP,"-s",host,"-k","pure.volume.san.usec.per.write["+volume+"]","-o",arraySanUsecPerWriteOp],stdout=FNULL,stderr=subprocess.STDOUT)
    subprocess.call(["zabbix_sender","-z",zabbixIP,"-s",host,"-k","pure.volume.usec.per.read["+volume+"]","-o",arrayUsecPerReadOp],stdout=FNULL,stderr=subprocess.STDOUT)
    subprocess.call(["zabbix_sender","-z",zabbixIP,"-s",host,"-k","pure.volume.usec.per.write["+volume+"]","-o",arrayUsecPerWriteOp],stdout=FNULL,stderr=subprocess.STDOUT)
    subprocess.call(["zabbix_sender","-z",zabbixIP,"-s",host,"-k","pure.volume.write.per.sec["+volume+"]","-o",arrayWritePerSec],stdout=FNULL,stderr=subprocess.STDOUT)
    subprocess.call(["zabbix_sender","-z",zabbixIP,"-s",host,"-k","pure.volume.size["+volume+"]","-o",arrayVolumeSize],stdout=FNULL,stderr=subprocess.STDOUT)

    '''Send 1 to give a result to Zabbix'''
    print(1)

except:
    '''
    Sending 0 to Zabbix instead of a Python error.
    Like that the items won't be considered as "unsupported"
    '''
    print(0)
