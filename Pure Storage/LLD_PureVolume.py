#!/usr/bin/env python3
'''
Author : Jeremy Verda
URL : jeremyverda.net
Description :
This module is intended to discover all the volumes on the Pure Storage Array
'''
import purestorage
import urllib3
import sys

try:
    '''Get the argument from Zabbix'''
    ip = str(sys.argv[1]) #IP of the Pure Storage Array
    token = str(sys.argv[2]) #API Token

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
    print("Error while getting volumes information due to an error with the arguments (Token,IP,...)")
except:
    print("Unknow error while getting volumes information")
