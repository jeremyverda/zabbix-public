#!/usr/bin/env python3
'''
Author : Jeremy Verda
URL : jeremyverda.net
'''
'''Import all libs'''
import purestorage
import urllib3
import sys
import subprocess
import os

'''
LLD function
Will return all the volumes available on the Pure Storage Flash Array
'''
def pure_volume_lld():
    try:
        '''Get the argument from Zabbix'''
        ip = str(sys.argv[2]) #IP of the Pure Storage Array
        token = str(sys.argv[3]) #API Token

        '''
        Disable the SSL Warning from the output
        '''
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        '''Get data'''
        arrayConnect = purestorage.FlashArray(ip,api_token=token)
        volumeList = arrayConnect.list_volumes()

        '''Print data to console for Zabbix discovery'''
        json_data = '{\t"data":['
        temp = 1
        for i in volumeList:
            data = '{"{#VOLUMENAME}":'+'"'+i["name"]+'"}'
            if temp==0:
                json_data = json_data+',\n'
            else:
                temp = 0
            json_data = json_data+data
        json_data = json_data+'\t ]}'
        print(json_data)

    except purestorage.PureHTTPError as err:
        print("Error while getting volumes information : {0}".format(err.reason))    
    except purestorage.PureError as err:
        print("Error while getting volumes information : {0}".format(err.reason))
    except ValueError:
        print("Error while getting volumes information due to an error with the arguments (Token,IP)")
    except:
        print("Unknow error while getting volumes information")

'''
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
    * Phone Home
    * Remote Assist
'''
def pure_array_info():
    try:
        '''Get the argument from Zabbix'''
        ip = str(sys.argv[2]) #IP of the Pure Storage Array
        token = str(sys.argv[3]) #API Token
        host = str(sys.argv[4]) #Host name (for the sender)
        zabbixIP = str(sys.argv[5]) #Zabbix Proxy or Server IP (for the sender)

        '''
        Disable the SSL Warning from the output
        '''
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        '''Get data'''
        arrayConnect = purestorage.FlashArray(ip,api_token=token)
        arraySpace = arrayConnect.get(space="true")
        arrayInfo = arrayConnect.get()
        arrayPhoneHome = arrayConnect.get_phonehome()
        arrayRemoteAssist = arrayConnect.get_remote_assist_status()
        arrayValues = arraySpace[0]

        '''Will disable the output to console'''
        FNULL = open(os.devnull, 'w')

        '''Sending data'''
        if "capacity" in arrayValues:
            arrayCapacity = str(arrayValues["capacity"])
            subprocess.call(["zabbix_sender","-z",zabbixIP,"-s",host,"-k","pure.array.capacity","-o",arrayCapacity],stdout=FNULL,stderr=subprocess.STDOUT)
        if "volumes" in arrayValues:
            arrayVolumesSize = str(arrayValues["volumes"])
            subprocess.call(["zabbix_sender","-z",zabbixIP,"-s",host,"-k","pure.array.volumes.size","-o",arrayVolumesSize],stdout=FNULL,stderr=subprocess.STDOUT)
        if "data_reduction" in arrayValues:
            arrayDataReduction = str(arrayValues["data_reduction"])
            subprocess.call(["zabbix_sender","-z",zabbixIP,"-s",host,"-k","pure.array.data.reduction","-o",arrayDataReduction],stdout=FNULL,stderr=subprocess.STDOUT)
        if "total" in arrayValues:
            arrayUsedSpace = str(arrayValues["total"])
            subprocess.call(["zabbix_sender","-z",zabbixIP,"-s",host,"-k","pure.array.used.space","-o",arrayUsedSpace],stdout=FNULL,stderr=subprocess.STDOUT)
        if "shared_space" in arrayValues:
            arraySharedSpace = str(arrayValues["shared_space"])
            subprocess.call(["zabbix_sender","-z",zabbixIP,"-s",host,"-k","pure.array.shared.space","-o",arraySharedSpace],stdout=FNULL,stderr=subprocess.STDOUT)
        if "thin_provisioning" in arrayValues:
            arrayThinProvisioning = str(arrayValues["thin_provisioning"])
            subprocess.call(["zabbix_sender","-z",zabbixIP,"-s",host,"-k","pure.array.thin.provisioning","-o",arrayThinProvisioning],stdout=FNULL,stderr=subprocess.STDOUT)
        if "total_reduction" in arrayValues:
            arrayTotalReduction = str(arrayValues["total_reduction"])
            subprocess.call(["zabbix_sender","-z",zabbixIP,"-s",host,"-k","pure.array.total.data.reduction","-o",arrayTotalReduction],stdout=FNULL,stderr=subprocess.STDOUT)
        if "array_name" in arrayInfo:
            arrayHostname = arrayInfo["array_name"]
            subprocess.call(["zabbix_sender","-z",zabbixIP,"-s",host,"-k","pure.array.hostname","-o",arrayHostname],stdout=FNULL,stderr=subprocess.STDOUT)
        if "version" in arrayInfo:
            arrayVersion = str(arrayInfo["version"])
            subprocess.call(["zabbix_sender","-z",zabbixIP,"-s",host,"-k","pure.array.version","-o",arrayVersion],stdout=FNULL,stderr=subprocess.STDOUT)
        if "status" in arrayRemoteAssist:
            remoteAssist = arrayRemoteAssist["status"]
            subprocess.call(["zabbix_sender","-z",zabbixIP,"-s",host,"-k","pure.remote.assist","-o",remoteAssist],stdout=FNULL,stderr=subprocess.STDOUT)
        if "phonehome" in arrayPhoneHome:
            phoneHome = arrayPhoneHome["phonehome"]
            subprocess.call(["zabbix_sender","-z",zabbixIP,"-s",host,"-k","pure.phone.home","-o",phoneHome],stdout=FNULL,stderr=subprocess.STDOUT)

        '''Send 1 to give a result to Zabbix'''
        print(1)

    except:
        '''
        Sending 0 to Zabbix instead of a Python error.
        Like that the items won't be considered as "unsupported"
        '''
        print(0)

'''
This module is intended to get the Pure Storage volume monitoring information : 
    * Writes per second
    * Microsecond per write operation
    * Output per second
    * San Microsecond per read operation
    * Read per second
    * Input per second
    * Microsecond per read operation
    * San microsecond per write operation
    * Snapshots size
    * Data reduction
    * Total data reduction
    * Thin Provisioning
    * Used space
'''
def pure_volume_monitoring():
    try:
        '''Get the argument from Zabbix'''
        ip = str(sys.argv[2]) #IP of the Pure Storage Array
        token = str(sys.argv[3]) #API Token
        volume = str(sys.argv[4]) #Volume Name
        host = str(sys.argv[5]) #Host name (for the sender)
        zabbixIP = str(sys.argv[6]) #Zabbix Proxy or Server IP (for the sender)

        '''
        Disable the SSL Warning from the output
        '''
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        '''Get data'''
        arrayConnect = purestorage.FlashArray(ip,api_token=token)
        volumeMonitoring = arrayConnect.get_volume(volume=volume,action="monitor")
        volumeSpace = arrayConnect.get_volume(volume=volume,space="true")
        volumeInfo = arrayConnect.get_volume(volume=volume)
        arrayValues = volumeMonitoring[0]

        '''Will disable the output to console'''
        FNULL = open(os.devnull, 'w')

        '''Sending data'''
        if "input_per_sec" in arrayValues:
            arrayInputPerSec = str(arrayValues["input_per_sec"])
            subprocess.call(["zabbix_sender","-z",zabbixIP,"-s",host,"-k","pure.volume.input.per.second["+volume+"]","-o",arrayInputPerSec],stdout=FNULL,stderr=subprocess.STDOUT)
        if "output_per_sec" in arrayValues:    
            arrayOutputPerSec = str(arrayValues["output_per_sec"])
            subprocess.call(["zabbix_sender","-z",zabbixIP,"-s",host,"-k","pure.volume.output.per.second["+volume+"]","-o",arrayOutputPerSec],stdout=FNULL,stderr=subprocess.STDOUT)
        if "reads_per_sec" in arrayValues:
            arrayReadPerSec = str(arrayValues["reads_per_sec"])
            subprocess.call(["zabbix_sender","-z",zabbixIP,"-s",host,"-k","pure.volume.read.per.sec["+volume+"]","-o",arrayReadPerSec],stdout=FNULL,stderr=subprocess.STDOUT)
        if "san_usec_per_read_op" in arrayValues:
            arraySanUsecPerReadOp = str(arrayValues["san_usec_per_read_op"])
            subprocess.call(["zabbix_sender","-z",zabbixIP,"-s",host,"-k","pure.volume.san.usec.per.read["+volume+"]","-o",arraySanUsecPerReadOp],stdout=FNULL,stderr=subprocess.STDOUT)
        if "san_usec_per_write_op" in arrayValues:
            arraySanUsecPerWriteOp = str(arrayValues["san_usec_per_write_op"])
            subprocess.call(["zabbix_sender","-z",zabbixIP,"-s",host,"-k","pure.volume.san.usec.per.write["+volume+"]","-o",arraySanUsecPerWriteOp],stdout=FNULL,stderr=subprocess.STDOUT)
        if "usec_per_read_op" in arrayValues:
            arrayUsecPerReadOp = str(arrayValues["usec_per_read_op"])
            subprocess.call(["zabbix_sender","-z",zabbixIP,"-s",host,"-k","pure.volume.usec.per.read["+volume+"]","-o",arrayUsecPerReadOp],stdout=FNULL,stderr=subprocess.STDOUT)
        if "usec_per_write_op" in arrayValues:
            arrayUsecPerWriteOp = str(arrayValues["usec_per_write_op"])
            subprocess.call(["zabbix_sender","-z",zabbixIP,"-s",host,"-k","pure.volume.usec.per.write["+volume+"]","-o",arrayUsecPerWriteOp],stdout=FNULL,stderr=subprocess.STDOUT)
        if "writes_per_sec" in arrayValues:
            arrayWritePerSec = str(arrayValues["writes_per_sec"])
            subprocess.call(["zabbix_sender","-z",zabbixIP,"-s",host,"-k","pure.volume.write.per.sec["+volume+"]","-o",arrayWritePerSec],stdout=FNULL,stderr=subprocess.STDOUT)
        if "size" in volumeInfo:
            arrayVolumeSize = str(volumeInfo["size"])
            subprocess.call(["zabbix_sender","-z",zabbixIP,"-s",host,"-k","pure.volume.size["+volume+"]","-o",arrayVolumeSize],stdout=FNULL,stderr=subprocess.STDOUT)
        if "snapshots" in volumeSpace:
            volumeSnapshots = str(volumeSpace["snapshots"])
            subprocess.call(["zabbix_sender","-z",zabbixIP,"-s",host,"-k","pure.volume.snapshots.size["+volume+"]","-o",volumeSnapshots],stdout=FNULL,stderr=subprocess.STDOUT)
        if "data_reduction" in volumeSpace:
            volumeDataReduction = str(volumeSpace["data_reduction"])
            subprocess.call(["zabbix_sender","-z",zabbixIP,"-s",host,"-k","pure.volume.data.reduction["+volume+"]","-o",volumeDataReduction],stdout=FNULL,stderr=subprocess.STDOUT)
        if "thin_provisioning" in volumeSpace:
            volumeThinProvisioning = str(volumeSpace["thin_provisioning"])
            subprocess.call(["zabbix_sender","-z",zabbixIP,"-s",host,"-k","pure.volume.thin.provisioning["+volume+"]","-o",volumeThinProvisioning],stdout=FNULL,stderr=subprocess.STDOUT)
        if "total_reduction" in volumeSpace:
            volumeTotalReduction = str(volumeSpace["total_reduction"])
            subprocess.call(["zabbix_sender","-z",zabbixIP,"-s",host,"-k","pure.volume.total.data.reduction["+volume+"]","-o",volumeTotalReduction],stdout=FNULL,stderr=subprocess.STDOUT)
        if "volumes" in volumeSpace:
            volumeUsedSpace = str(volumeSpace["volumes"])
            subprocess.call(["zabbix_sender","-z",zabbixIP,"-s",host,"-k","pure.volume.used.space["+volume+"]","-o",volumeUsedSpace],stdout=FNULL,stderr=subprocess.STDOUT)

        '''Send 1 to give a result to Zabbix'''
        print(1)

    except:
        '''
        Sending 0 to Zabbix instead of a Python error.
        Like that the items won't be considered as "unsupported"
        '''
        print(0)

'''
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
def pure_array_monitoring():
    try:
        '''Get the argument from Zabbix'''
        ip = str(sys.argv[2]) #IP of the Pure Storage Array
        token = str(sys.argv[3]) #API Token
        host = str(sys.argv[4]) #Host name (for the sender)
        zabbixIP = str(sys.argv[5]) #Zabbix Proxy or Server IP (for the sender)

        '''
        Disable the SSL Warning from the output
        '''
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        '''Get data'''
        arrayConnect = purestorage.FlashArray(ip,api_token=token)
        arrayMonitoring = arrayConnect.get(action="monitor")
        arrayValues = arrayMonitoring[0]

        '''Will disable the output to console'''
        FNULL = open(os.devnull, 'w')

        '''Send data'''
        if "input_per_sec" in arrayValues:
            arrayInputPerSec = str(arrayValues["input_per_sec"])
            subprocess.call(["zabbix_sender","-z",zabbixIP,"-s",host,"-k","pure.array.input.per.second","-o",arrayInputPerSec],stdout=FNULL,stderr=subprocess.STDOUT)
        if "output_per_sec" in arrayValues:
            arrayOutputPerSec = str(arrayValues["output_per_sec"])
            subprocess.call(["zabbix_sender","-z",zabbixIP,"-s",host,"-k","pure.array.output.per.second","-o",arrayOutputPerSec],stdout=FNULL,stderr=subprocess.STDOUT)
        if "queue_depth" in arrayValues:
            arrayQueueDepth = str(arrayValues["queue_depth"])
            subprocess.call(["zabbix_sender","-z",zabbixIP,"-s",host,"-k","pure.array.queue.depth","-o",arrayQueueDepth],stdout=FNULL,stderr=subprocess.STDOUT)
        if "reads_per_sec" in arrayValues:
            arrayReadPerSec = str(arrayValues["reads_per_sec"])
            subprocess.call(["zabbix_sender","-z",zabbixIP,"-s",host,"-k","pure.array.read.per.sec","-o",arrayReadPerSec],stdout=FNULL,stderr=subprocess.STDOUT)
        if "san_usec_per_read_op" in arrayValues:
            arraySanUsecPerReadOp = str(arrayValues["san_usec_per_read_op"])
            subprocess.call(["zabbix_sender","-z",zabbixIP,"-s",host,"-k","pure.array.san.usec.per.read","-o",arraySanUsecPerReadOp],stdout=FNULL,stderr=subprocess.STDOUT)
        if "san_usec_per_write_op" in arrayValues:
            arraySanUsecPerWriteOp = str(arrayValues["san_usec_per_write_op"])
            subprocess.call(["zabbix_sender","-z",zabbixIP,"-s",host,"-k","pure.array.san.usec.per.write","-o",arraySanUsecPerWriteOp],stdout=FNULL,stderr=subprocess.STDOUT)
        if "usec_per_read_op" in arrayValues:
            arrayUsecPerReadOp = str(arrayValues["usec_per_read_op"])
            subprocess.call(["zabbix_sender","-z",zabbixIP,"-s",host,"-k","pure.array.usec.per.read","-o",arrayUsecPerReadOp],stdout=FNULL,stderr=subprocess.STDOUT)
        if "usec_per_write_op" in arrayValues:
            arrayUsecPerWriteOp = str(arrayValues["usec_per_write_op"])
            subprocess.call(["zabbix_sender","-z",zabbixIP,"-s",host,"-k","pure.array.usec.per.write","-o",arrayUsecPerWriteOp],stdout=FNULL,stderr=subprocess.STDOUT)
        if "writes_per_sec" in arrayValues:
            arrayWritePerSec = str(arrayValues["writes_per_sec"])
            subprocess.call(["zabbix_sender","-z",zabbixIP,"-s",host,"-k","pure.array.write.per.sec","-o",arrayWritePerSec],stdout=FNULL,stderr=subprocess.STDOUT)

        '''Send 1 to give a result to Zabbix'''
        print(1)

    except:
        '''
        Sending 0 to Zabbix instead of a Python error
        Like that the items won't be considered as unsupported
        '''
        print(0)

'''
LLD function
Will return all the hosts available on the Pure Storage Flash Array
'''
def pure_host_lld():
    try:
        '''Get the argument from Zabbix'''
        ip = str(sys.argv[2]) #IP of the Pure Storage Array
        token = str(sys.argv[3]) #API Token

        '''
        Disable the SSL Warning from the output
        '''
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        '''Get data'''
        arrayConnect = purestorage.FlashArray(ip,api_token=token)
        hostList = arrayConnect.list_hosts()

        '''Print data to console for Zabbix discovery'''
        json_data = '{\t"data":['
        temp = 1
        for i in hostList:
            data = '{"{#HOSTNAME}":'+'"'+i["name"]+'"}'
            if temp==0:
                json_data = json_data+',\n'
            else:
                temp = 0
            json_data = json_data+data
        json_data = json_data+'\t ]}'
        print(json_data)

    except purestorage.PureHTTPError as err:
        print("Error while getting hosts information : {0}".format(err.reason))    
    except purestorage.PureError as err:
        print("Error while getting hosts information : {0}".format(err.reason))
    except ValueError:
        print("Error while getting hosts information due to an error with the arguments (Token,IP)")
    except:
        print("Unknow error while getting hosts information")
'''
This module is intended to get the Pure Storage host monitoring information : 
    * Writes per second
    * Microsecond per write operation
    * Output per second
    * San Microsecond per read operation
    * Read per second
    * Input per second
    * Microsecond per read operation
    * San microsecond per write operation
'''
def pure_host_monitoring():
    try:
        '''Get the argument from Zabbix'''
        ip = str(sys.argv[2]) #IP of the Pure Storage Array
        token = str(sys.argv[3]) #API Token
        hostname = str(sys.argv[4]) #Host Name
        host = str(sys.argv[5]) #Host name (for the sender)
        zabbixIP = str(sys.argv[6]) #Zabbix Proxy or Server IP (for the sender)

        '''
        Disable the SSL Warning from the output
        '''
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        '''Get data'''
        arrayConnect = purestorage.FlashArray(ip,api_token=token)
        hostMonitoring = arrayConnect.get_host(host=hostname,action="monitor")

        '''Will disable the output to console'''
        FNULL = open(os.devnull, 'w')

        '''Sending data'''
        if "input_per_sec" in hostMonitoring:
            arrayInputPerSec = str(hostMonitoring["input_per_sec"])
            subprocess.call(["zabbix_sender","-z",zabbixIP,"-s",host,"-k","pure.host.input.per.second["+hostname+"]","-o",arrayInputPerSec],stdout=FNULL,stderr=subprocess.STDOUT)
        if "output_per_sec" in hostMonitoring:    
            arrayOutputPerSec = str(hostMonitoring["output_per_sec"])
            subprocess.call(["zabbix_sender","-z",zabbixIP,"-s",host,"-k","pure.host.output.per.second["+hostname+"]","-o",arrayOutputPerSec],stdout=FNULL,stderr=subprocess.STDOUT)
        if "reads_per_sec" in hostMonitoring:
            arrayReadPerSec = str(hostMonitoring["reads_per_sec"])
            subprocess.call(["zabbix_sender","-z",zabbixIP,"-s",host,"-k","pure.host.read.per.sec["+hostname+"]","-o",arrayReadPerSec],stdout=FNULL,stderr=subprocess.STDOUT)
        if "san_usec_per_read_op" in hostMonitoring:
            arraySanUsecPerReadOp = str(hostMonitoring["san_usec_per_read_op"])
            subprocess.call(["zabbix_sender","-z",zabbixIP,"-s",host,"-k","pure.host.san.usec.per.read["+hostname+"]","-o",arraySanUsecPerReadOp],stdout=FNULL,stderr=subprocess.STDOUT)
        if "san_usec_per_write_op" in hostMonitoring:
            arraySanUsecPerWriteOp = str(hostMonitoring["san_usec_per_write_op"])
            subprocess.call(["zabbix_sender","-z",zabbixIP,"-s",host,"-k","pure.host.san.usec.per.write["+hostname+"]","-o",arraySanUsecPerWriteOp],stdout=FNULL,stderr=subprocess.STDOUT)
        if "usec_per_read_op" in hostMonitoring:
            arrayUsecPerReadOp = str(hostMonitoring["usec_per_read_op"])
            subprocess.call(["zabbix_sender","-z",zabbixIP,"-s",host,"-k","pure.host.usec.per.read["+hostname+"]","-o",arrayUsecPerReadOp],stdout=FNULL,stderr=subprocess.STDOUT)
        if "usec_per_write_op" in hostMonitoring:
            arrayUsecPerWriteOp = str(hostMonitoring["usec_per_write_op"])
            subprocess.call(["zabbix_sender","-z",zabbixIP,"-s",host,"-k","pure.host.usec.per.write["+hostname+"]","-o",arrayUsecPerWriteOp],stdout=FNULL,stderr=subprocess.STDOUT)
        if "writes_per_sec" in hostMonitoring:
            arrayWritePerSec = str(hostMonitoring["writes_per_sec"])
            subprocess.call(["zabbix_sender","-z",zabbixIP,"-s",host,"-k","pure.host.write.per.sec["+hostname+"]","-o",arrayWritePerSec],stdout=FNULL,stderr=subprocess.STDOUT)

        '''Send 1 to give a result to Zabbix'''
        print(1)

    except:
        '''
        Sending 0 to Zabbix instead of a Python error.
        Like that the items won't be considered as "unsupported"
        '''
        print(0)   

'''
LLD function
Will return all the disks and NVRAM available on the Pure Storage Flash Array
'''
def pure_disk_lld():
    try:
        '''Get the argument from Zabbix'''
        ip = str(sys.argv[2]) #IP of the Pure Storage Array
        token = str(sys.argv[3]) #API Token

        '''
        Disable the SSL Warning from the output
        '''
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        '''Get data'''
        arrayConnect = purestorage.FlashArray(ip,api_token=token)
        diskList = arrayConnect.list_drives()

        '''Print data to console for Zabbix discovery'''
        json_data = '{\t"data":['
        temp = 1
        for i in diskList:
            data = '{"{#DISKNAME}":'+'"'+i["name"]+'"}'
            if temp==0:
                json_data = json_data+',\n'
            else:
                temp = 0
            json_data = json_data+data
        json_data = json_data+'\t ]}'
        print(json_data)

    except purestorage.PureHTTPError as err:
        print("Error while getting disks information : {0}".format(err.reason))    
    except purestorage.PureError as err:
        print("Error while getting disks information : {0}".format(err.reason))
    except ValueError:
        print("Error while getting disks information due to an error with the arguments (Token,IP)")
    except:
        print("Unknow error while getting disks information")

'''
This module is intended to get the Pure Storage disk monitoring information : 
    * Status
    * Capacity
    * Protocol
    * Type
    * Last Failure
'''
def pure_disk_monitoring():
    try:
        '''Get the argument from Zabbix'''
        ip = str(sys.argv[2]) #IP of the Pure Storage Array
        token = str(sys.argv[3]) #API Token
        disk = str(sys.argv[4]) #disk Name
        host = str(sys.argv[5]) #Host name (for the sender)
        zabbixIP = str(sys.argv[6]) #Zabbix Proxy or Server IP (for the sender)

        '''
        Disable the SSL Warning from the output
        '''
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        '''Get data'''
        arrayConnect = purestorage.FlashArray(ip,api_token=token)
        diskMonitoring = arrayConnect.get_drive(drive=disk)

        '''Will disable the output to console'''
        FNULL = open(os.devnull, 'w')

        '''Sending data'''
        if "status" in diskMonitoring:
            diskStatus = str(diskMonitoring["status"])
            subprocess.call(["zabbix_sender","-z",zabbixIP,"-s",host,"-k","pure.disk.status["+disk+"]","-o",diskStatus],stdout=FNULL,stderr=subprocess.STDOUT)
        if "capacity" in diskMonitoring:    
            diskCapacity = str(diskMonitoring["capacity"])
            subprocess.call(["zabbix_sender","-z",zabbixIP,"-s",host,"-k","pure.disk.capacity["+disk+"]","-o",diskCapacity],stdout=FNULL,stderr=subprocess.STDOUT)
        if "protocol" in diskMonitoring:
            diskProtocol = str(diskMonitoring["protocol"])
            subprocess.call(["zabbix_sender","-z",zabbixIP,"-s",host,"-k","pure.disk.protocol["+disk+"]","-o",diskProtocol],stdout=FNULL,stderr=subprocess.STDOUT)
        if "type" in diskMonitoring:
            diskType = str(diskMonitoring["type"])
            subprocess.call(["zabbix_sender","-z",zabbixIP,"-s",host,"-k","pure.disk.type["+disk+"]","-o",diskType],stdout=FNULL,stderr=subprocess.STDOUT)
        if "last_failure" in diskMonitoring:
            diskLastFailure = str(diskMonitoring["last_failure"])
            subprocess.call(["zabbix_sender","-z",zabbixIP,"-s",host,"-k","pure.disk.last.failure["+disk+"]","-o",diskLastFailure],stdout=FNULL,stderr=subprocess.STDOUT)
        
        '''Send 1 to give a result to Zabbix'''
        print(1)

    except:
        '''
        Sending 0 to Zabbix instead of a Python error.
        Like that the items won't be considered as "unsupported"
        '''
        print(0)   

'''main function'''
if __name__ == '__main__':
    if sys.argv[1] == "volumeLLD":
        pure_volume_lld()
    if sys.argv[1] == "arrayInfo":
        pure_array_info()
    if sys.argv[1] == "volumeMonitoring":
        pure_volume_monitoring()
    if sys.argv[1] == "arrayMonitoring":
        pure_array_monitoring()
    if sys.argv[1] == "hostLLD":
        pure_host_lld()
    if sys.argv[1] == "hostMonitoring":
        pure_host_monitoring()
    if sys.argv[1] == "diskLLD":
        pure_disk_lld()
    if sys.argv[1] == "diskMonitoring":
        pure_disk_monitoring()
