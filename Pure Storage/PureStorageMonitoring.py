#!/usr/bin/env python3
'''
Author : Jeremy Verda
URL : jeremyverda.net
'''
'''Import all libs'''
import purestorage
import urllib3
import sys
import os
from pyzabbix import ZabbixMetric, ZabbixSender
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

'''Disable SSL Warnings'''
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

'''
LLD function
Will return all the volumes available on the Pure Storage Flash Array
'''
def pure_volume_lld():
    try:
        '''Get the argument from Zabbix'''
        ip = str(sys.argv[2]) #IP of the Pure Storage Array
        token = str(sys.argv[3]) #API Token

        '''Get data'''
        arrayConnect = purestorage.FlashArray(ip,api_token=token,verify_https=False)
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
    except Exception as e:
        print("Unknow error while getting volumes information : "+str(e))

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

        '''Get data'''
        arrayConnect = purestorage.FlashArray(ip,api_token=token,verify_https=False)
        arraySpace = arrayConnect.get(space="true")
        arrayInfo = arrayConnect.get()
        arrayPhoneHome = arrayConnect.get_phonehome()
        arrayRemoteAssist = arrayConnect.get_remote_assist_status()
        arrayValues = arraySpace[0]

        '''Will disable the output to console'''
        FNULL = open(os.devnull, 'w')

        '''Sending data'''
        metrics = []
        if "capacity" in arrayValues:
            arrayCapacity = str(arrayValues["capacity"])
            m = ZabbixMetric(host,'pure.array.capacity',arrayCapacity)
            metrics.append(m)
        if "volumes" in arrayValues:
            arrayVolumesSize = str(arrayValues["volumes"])
            m = ZabbixMetric(host,'pure.array.volumes.size',arrayVolumesSize)
            metrics.append(m)
        if "data_reduction" in arrayValues:
            arrayDataReduction = str(arrayValues["data_reduction"])
            m = ZabbixMetric(host,'pure.array.data.reduction',arrayDataReduction)
            metrics.append(m)
        if "total" in arrayValues:
            arrayUsedSpace = str(arrayValues["total"])
            m = ZabbixMetric(host,'pure.array.used.space',arrayUsedSpace)
            metrics.append(m)
        if "shared_space" in arrayValues:
            arraySharedSpace = str(arrayValues["shared_space"])
            m = ZabbixMetric(host,'pure.array.shared.space',arraySharedSpace)
            metrics.append(m)
        if "thin_provisioning" in arrayValues:
            arrayThinProvisioning = str(arrayValues["thin_provisioning"])
            m = ZabbixMetric(host,'pure.array.thin.provisioning',arrayThinProvisioning)
            metrics.append(m)
        if "total_reduction" in arrayValues:
            arrayTotalReduction = str(arrayValues["total_reduction"])
            m = ZabbixMetric(host,'pure.array.total.data.reduction',arrayTotalReduction)
            metrics.append(m)
        if "array_name" in arrayInfo:
            arrayHostname = arrayInfo["array_name"]
            m = ZabbixMetric(host,'pure.array.hostname',arrayHostname)
            metrics.append(m)
        if "version" in arrayInfo:
            arrayVersion = str(arrayInfo["version"])
            m = ZabbixMetric(host,'pure.array.version',arrayVersion)
            metrics.append(m)
        if "status" in arrayRemoteAssist:
            remoteAssist = arrayRemoteAssist["status"]
            m = ZabbixMetric(host,'pure.remote.assist',remoteAssist)
            metrics.append(m)
        if "phonehome" in arrayPhoneHome:
            phoneHome = arrayPhoneHome["phonehome"]
            m = ZabbixMetric(host,'pure.phone.home',phoneHome)
            metrics.append(m)
        data = ZabbixSender(zabbixIP)
        data.send(metrics)
        '''Send 1 to give a result to Zabbix'''
        print(1)

    except Exception as e:
        '''
        Sending 0 to Zabbix instead of a Python error.
        Like that the items won't be considered as "unsupported"
        '''
        metrics = [ZabbixMetric(host,'pure.info.launcher.error',str(e))]
        data = ZabbixSender(zabbixIP)
        data.send(metrics)
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
        host = str(sys.argv[4]) #Host name (for the sender)
        zabbixIP = str(sys.argv[5]) #Zabbix Proxy or Server IP (for the sender)

        '''Get data'''
        arrayConnect = purestorage.FlashArray(ip,api_token=token,verify_https=False)
        volumeList = arrayConnect.list_volumes()
        metrics = []
        for i in volumeList:
            volume = i["name"]

            volumeMonitoring = arrayConnect.get_volume(volume=volume,action="monitor")
            volumeSpace = arrayConnect.get_volume(volume=volume,space="true")
            volumeInfo = arrayConnect.get_volume(volume=volume)
            arrayValues = volumeMonitoring[0]

            '''Will disable the output to console'''
            FNULL = open(os.devnull, 'w')

            '''Sending data'''
            if "input_per_sec" in arrayValues:
                arrayInputPerSec = str(arrayValues["input_per_sec"])
                m = ZabbixMetric(host,"pure.volume.input.per.second["+volume+"]",arrayInputPerSec)
                metrics.append(m)
            if "output_per_sec" in arrayValues:    
                arrayOutputPerSec = str(arrayValues["output_per_sec"])
                m = ZabbixMetric(host,"pure.volume.output.per.second["+volume+"]",arrayOutputPerSec)
                metrics.append(m)
            if "reads_per_sec" in arrayValues:
                arrayReadPerSec = str(arrayValues["reads_per_sec"])
                m = ZabbixMetric(host,"pure.volume.read.per.sec["+volume+"]",arrayReadPerSec)
                metrics.append(m)
            if "san_usec_per_read_op" in arrayValues:
                arraySanUsecPerReadOp = str(arrayValues["san_usec_per_read_op"])
                m = ZabbixMetric(host,"pure.volume.san.usec.per.read["+volume+"]",arraySanUsecPerReadOp)
                metrics.append(m)
            if "san_usec_per_write_op" in arrayValues:
                arraySanUsecPerWriteOp = str(arrayValues["san_usec_per_write_op"])
                m = ZabbixMetric(host,"pure.volume.san.usec.per.write["+volume+"]",arraySanUsecPerWriteOp)
                metrics.append(m)
            if "usec_per_read_op" in arrayValues:
                arrayUsecPerReadOp = str(arrayValues["usec_per_read_op"])
                m = ZabbixMetric(host,"pure.volume.usec.per.read["+volume+"]",arrayUsecPerReadOp)
                metrics.append(m)
            if "usec_per_write_op" in arrayValues:
                arrayUsecPerWriteOp = str(arrayValues["usec_per_write_op"])
                m = ZabbixMetric(host,"pure.volume.usec.per.write["+volume+"]",arrayUsecPerWriteOp)
                metrics.append(m)
            if "writes_per_sec" in arrayValues:
                arrayWritePerSec = str(arrayValues["writes_per_sec"])
                m = ZabbixMetric(host,"pure.volume.write.per.sec["+volume+"]",arrayWritePerSec)
                metrics.append(m)
            if "size" in volumeInfo:
                arrayVolumeSize = str(volumeInfo["size"])
                m = ZabbixMetric(host,"pure.volume.size["+volume+"]",arrayVolumeSize)
                metrics.append(m)
            if "snapshots" in volumeSpace:
                volumeSnapshots = str(volumeSpace["snapshots"])
                m = ZabbixMetric(host,"pure.volume.snapshots.size["+volume+"]",volumeSnapshots)
                metrics.append(m)
            if "data_reduction" in volumeSpace:
                volumeDataReduction = str(volumeSpace["data_reduction"])
                m = ZabbixMetric(host,"pure.volume.data.reduction["+volume+"]",volumeDataReduction)
                metrics.append(m)
            if "thin_provisioning" in volumeSpace:
                volumeThinProvisioning = str(volumeSpace["thin_provisioning"])
                m = ZabbixMetric(host,"pure.volume.thin.provisioning["+volume+"]",volumeThinProvisioning)
                metrics.append(m)
            if "total_reduction" in volumeSpace:
                volumeTotalReduction = str(volumeSpace["total_reduction"])
                m = ZabbixMetric(host,"pure.volume.total.data.reduction["+volume+"]",volumeTotalReduction)
                metrics.append(m)
            if "volumes" in volumeSpace:
                volumeUsedSpace = str(volumeSpace["volumes"])
                m = ZabbixMetric(host,"pure.volume.used.space["+volume+"]",volumeUsedSpace)
                metrics.append(m)
        data = ZabbixSender(zabbixIP)
        data.send(metrics)
        '''Send 1 to give a result to Zabbix'''
        print(1)

    except Exception as e:
        '''
        Sending 0 to Zabbix instead of a Python error.
        Like that the items won't be considered as "unsupported"
        '''
        metrics = [ZabbixMetric(host,"pure.volume.monitoring.launcher.error",str(e))]
        data = ZabbixSender(zabbixIP)
        data.send(metrics)
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

        '''Get data'''
        arrayConnect = purestorage.FlashArray(ip,api_token=token,verify_https=False)
        arrayMonitoring = arrayConnect.get(action="monitor")
        arrayValues = arrayMonitoring[0]

        '''Will disable the output to console'''
        FNULL = open(os.devnull, 'w')

        '''Send data'''
        metrics = []
        if "input_per_sec" in arrayValues:
            arrayInputPerSec = str(arrayValues["input_per_sec"])
            m = ZabbixMetric(host,"pure.array.input.per.second",arrayInputPerSec)
            metrics.append(m)
        if "output_per_sec" in arrayValues:
            arrayOutputPerSec = str(arrayValues["output_per_sec"])
            m = ZabbixMetric(host,"pure.array.output.per.second",arrayOutputPerSec)
            metrics.append(m)
        if "queue_depth" in arrayValues:
            arrayQueueDepth = str(arrayValues["queue_depth"])
            m = ZabbixMetric(host,"pure.array.queue.depth",arrayQueueDepth)
            metrics.append(m)
        if "reads_per_sec" in arrayValues:
            arrayReadPerSec = str(arrayValues["reads_per_sec"])
            m = ZabbixMetric(host,"pure.array.read.per.sec",arrayReadPerSec)
            metrics.append(m)
        if "san_usec_per_read_op" in arrayValues:
            arraySanUsecPerReadOp = str(arrayValues["san_usec_per_read_op"])
            m = ZabbixMetric(host,"pure.array.san.usec.per.read",arraySanUsecPerReadOp)
            metrics.append(m)
        if "san_usec_per_write_op" in arrayValues:
            arraySanUsecPerWriteOp = str(arrayValues["san_usec_per_write_op"])
            m = ZabbixMetric(host,"pure.array.san.usec.per.write",arraySanUsecPerWriteOp)
            metrics.append(m)
        if "usec_per_read_op" in arrayValues:
            arrayUsecPerReadOp = str(arrayValues["usec_per_read_op"])
            m = ZabbixMetric(host,"pure.array.usec.per.read",arrayUsecPerReadOp)
            metrics.append(m)
        if "usec_per_write_op" in arrayValues:
            arrayUsecPerWriteOp = str(arrayValues["usec_per_write_op"])
            m = ZabbixMetric(host,"pure.array.usec.per.write",arrayUsecPerWriteOp)
            metrics.append(m)
        if "writes_per_sec" in arrayValues:
            arrayWritePerSec = str(arrayValues["writes_per_sec"])
            m = ZabbixMetric(host,"pure.array.write.per.sec",arrayWritePerSec)
            metrics.append(m)
        data = ZabbixSender(zabbixIP)
        data.send(metrics)
        '''Send 1 to give a result to Zabbix'''
        print(1)

    except Exception as e:
        '''
        Sending 0 to Zabbix instead of a Python error
        Like that the items won't be considered as unsupported
        '''
        metrics = [ZabbixMetric(host,"pure.monitoring.launcher.error",str(e))]
        data = ZabbixSender(zabbixIP)
        data.send(metrics)
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

        '''Get data'''
        arrayConnect = purestorage.FlashArray(ip,api_token=token,verify_https=False)
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
    except Exception as e:
        print("Unknow error while getting hosts information : "+str(e))
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
        host = str(sys.argv[4]) #Host name (for the sender)
        zabbixIP = str(sys.argv[5]) #Zabbix Proxy or Server IP (for the sender)

        '''Get data'''
        arrayConnect = purestorage.FlashArray(ip,api_token=token,verify_https=False)
        hostList = arrayConnect.list_hosts()
        metrics = []
        for i in hostList:
            hostname = i["name"]
            hostMonitoring = arrayConnect.get_host(host=hostname,action="monitor")

            '''Sending data'''
            if "input_per_sec" in hostMonitoring:
                arrayInputPerSec = str(hostMonitoring["input_per_sec"])
                m = ZabbixMetric(host,"pure.host.input.per.second["+hostname+"]",arrayInputPerSec)
                metrics.append(m)
            if "output_per_sec" in hostMonitoring:    
                arrayOutputPerSec = str(hostMonitoring["output_per_sec"])
                m = ZabbixMetric(host,"pure.host.output.per.second["+hostname+"]",arrayOutputPerSec)
                metrics.append(m)
            if "reads_per_sec" in hostMonitoring:
                arrayReadPerSec = str(hostMonitoring["reads_per_sec"])
                m = ZabbixMetric(host,"pure.host.read.per.sec["+hostname+"]",arrayReadPerSec)
                metrics.append(m)
            if "san_usec_per_read_op" in hostMonitoring:
                arraySanUsecPerReadOp = str(hostMonitoring["san_usec_per_read_op"])
                m = ZabbixMetric(host,"pure.host.san.usec.per.read["+hostname+"]",arraySanUsecPerReadOp)
                metrics.append(m)
            if "san_usec_per_write_op" in hostMonitoring:
                arraySanUsecPerWriteOp = str(hostMonitoring["san_usec_per_write_op"])
                m = ZabbixMetric(host,"pure.host.san.usec.per.write["+hostname+"]",arraySanUsecPerWriteOp)
                metrics.append(m)
            if "usec_per_read_op" in hostMonitoring:
                arrayUsecPerReadOp = str(hostMonitoring["usec_per_read_op"])
                m = ZabbixMetric(host,"pure.host.usec.per.read["+hostname+"]",arrayUsecPerReadOp)
                metrics.append(m)
            if "usec_per_write_op" in hostMonitoring:
                arrayUsecPerWriteOp = str(hostMonitoring["usec_per_write_op"])
                m = ZabbixMetric(host,"pure.host.usec.per.write["+hostname+"]",arrayUsecPerWriteOp)
                metrics.append(m)
            if "writes_per_sec" in hostMonitoring:
                arrayWritePerSec = str(hostMonitoring["writes_per_sec"])
                m = ZabbixMetric(host,"pure.host.write.per.sec["+hostname+"]",arrayWritePerSec)
                metrics.append(m)
        data = ZabbixSender(zabbixIP)
        data.send(metrics)
        '''Send 1 to give a result to Zabbix'''
        print(1)

    except Exception as e:
        '''
        Sending 0 to Zabbix instead of a Python error.
        Like that the items won't be considered as "unsupported"
        '''
        metrics = [ZabbixMetric(host,"pure.host.monitoring.launcher.error",str(e))]
        data = ZabbixSender(zabbixIP)
        data.send(metrics)
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

        '''Get data'''
        arrayConnect = purestorage.FlashArray(ip,api_token=token,verify_https=False)
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
    except Exception as e:
        print("Unknow error while getting disks information : "+str(e))

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
        host = str(sys.argv[4]) #Host name (for the sender)
        zabbixIP = str(sys.argv[5]) #Zabbix Proxy or Server IP (for the sender)

        '''Get data'''
        arrayConnect = purestorage.FlashArray(ip,api_token=token,verify_https=False)
        diskList = arrayConnect.list_drives()
        metrics = []
        for i in diskList:
            disk = i["name"]
            diskMonitoring = arrayConnect.get_drive(drive=disk)

            '''Sending data'''
            
            if "status" in diskMonitoring:
                diskStatus = str(diskMonitoring["status"])
                m = ZabbixMetric(host,"pure.disk.status["+disk+"]",diskStatus)
                metrics.append(m)
            if "capacity" in diskMonitoring:    
                diskCapacity = str(diskMonitoring["capacity"])
                m = ZabbixMetric(host,"pure.disk.capacity["+disk+"]",diskCapacity)
                metrics.append(m)
            if "protocol" in diskMonitoring:
                diskProtocol = str(diskMonitoring["protocol"])
                m = ZabbixMetric(host,"pure.disk.protocol["+disk+"]",diskProtocol)
                metrics.append(m)
            if "type" in diskMonitoring:
                diskType = str(diskMonitoring["type"])
                m = ZabbixMetric(host,"pure.disk.type["+disk+"]",diskType)
                metrics.append(m)
            if "last_failure" in diskMonitoring:
                diskLastFailure = str(diskMonitoring["last_failure"])
                m = ZabbixMetric(host,"pure.disk.last.failure["+disk+"]",diskLastFailure)
                metrics.append(m)
        data = ZabbixSender(zabbixIP)
        data.send(metrics)
        '''Send 1 to give a result to Zabbix'''
        print(1)

    except Exception as e:
        '''
        Sending 0 to Zabbix instead of a Python error.
        Like that the items won't be considered as "unsupported"
        '''
        metrics = [ZabbixMetric(host,"pure.disk.monitoring.launcher.error",str(e))]
        data = ZabbixSender(zabbixIP)
        data.send(metrics)
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
