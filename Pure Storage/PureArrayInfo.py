#!/usr/bin/env python3
'''
Author : Jeremy Verda
URL : jeremyverda.net
Description :
This module is intended to get the Pure Storage Array information : 
    * Capacity
    * Hostname
    * Volumes size
    * Data Reduction ratio
    * Total used space
    * Shared Space
    * Thin Provisionning
    * Total reduction ratio
    * Number of snapshots
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
arraySpace = arrayConnect.get(space="true")
arrayInfo = arrayConnect.get()

'''Export data'''
arrayValues = arraySpace[0]
arrayCapacity = str(arrayValues["capacity"])
arrayVolumesSize = str(arrayValues["volumes"])
arrayDataReduction = str(arrayValues["data_reduction"])
arrayUsedSpace = str(arrayValues["total"])
arraySharedSpace = str(arrayValues["shared_space"])
arrayThinProvisioning = str(arrayValues["thin_provisioning"])
arrayTotalReduction = str(arrayValues["total_reduction"])
arrayHostname = arrayInfo["array_name"]
arrayVersion = str(arrayInfo["version"])

'''Will disable the output to console'''
FNULL = open(os.devnull, 'w')

'''Send data'''
subprocess.call(["zabbix_sender","-z",zabbixIP,"-s",host,"-k","pure.array.capacity","-o",arrayCapacity],stdout=FNULL,stderr=subprocess.STDOUT)
subprocess.call(["zabbix_sender","-z",zabbixIP,"-s",host,"-k","pure.array.volumes.size","-o",arrayVolumesSize],stdout=FNULL,stderr=subprocess.STDOUT)
subprocess.call(["zabbix_sender","-z",zabbixIP,"-s",host,"-k","pure.array.data.reduction","-o",arrayDataReduction],stdout=FNULL,stderr=subprocess.STDOUT)
subprocess.call(["zabbix_sender","-z",zabbixIP,"-s",host,"-k","pure.array.used.space","-o",arrayUsedSpace],stdout=FNULL,stderr=subprocess.STDOUT)
subprocess.call(["zabbix_sender","-z",zabbixIP,"-s",host,"-k","pure.array.shared.space","-o",arraySharedSpace],stdout=FNULL,stderr=subprocess.STDOUT)
subprocess.call(["zabbix_sender","-z",zabbixIP,"-s",host,"-k","pure.array.thin.provisioning","-o",arrayThinProvisioning],stdout=FNULL,stderr=subprocess.STDOUT)
subprocess.call(["zabbix_sender","-z",zabbixIP,"-s",host,"-k","pure.array.total.data.reduction","-o",arrayTotalReduction],stdout=FNULL,stderr=subprocess.STDOUT)
subprocess.call(["zabbix_sender","-z",zabbixIP,"-s",host,"-k","pure.array.hostname","-o",arrayHostname],stdout=FNULL,stderr=subprocess.STDOUT)
subprocess.call(["zabbix_sender","-z",zabbixIP,"-s",host,"-k","pure.array.version","-o",arrayVersion],stdout=FNULL,stderr=subprocess.STDOUT)

'''Send 1 to give a result to Zabbix'''
print(1)