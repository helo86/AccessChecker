#!/usr/bin/env python

from pypsexec.client import Client
import os
import time
import sys
import paramiko
import nmap
import fileinput
import socket
import re
import getpass
import warnings
warnings.filterwarnings(action='ignore',module='.*paramiko.*')

domain = raw_input("Domain: ")
user = raw_input("Username: ")
password = getpass.getpass("Password: ")
executable = "hostname"
arguments = "/all"
port = 22
ipList = []
linuxPCs = []
windowsPCs = []

#Extract IPs
hostfile = list(open('hosts.txt', 'r').read().split('\n'))
for entry in hostfile:
        ips = re.findall(r'[0-9]+(?:\.[0-9]+){3}', entry)
        for ip in ips:
                ipList.append(ip)

#NMAP
nm = nmap.PortScanner()

for ip in ipList:
    try:
        nm.scan(ip, arguments='-O')
        print("Server: " + ip + " " + nm[ip].hostname())
        operatingOS = nm[ip]['osmatch'][0]['osclass'][0]['osfamily']
        print("OS: " + operatingOS)

        if operatingOS == 'Linux':
            linuxPCs.append(ip)

        if operatingOS == 'Windows':
            windowsPCs.append(ip)
    except:
        print("Host: " + ip + " not accessible")

print("\nTesting all Linux server for access")
for serverL in linuxPCs:
    try: # if Linux
        client = paramiko.SSHClient()
        #client.load_system_host_keys()
        client.set_missing_host_key_policy(paramiko.WarningPolicy)
        client.connect(ip, port=port, username=user, password=password)
        stdin, stdout, stderr = client.exec_command(executable)
        print("Success | Server: " + serverL + " Hostname: " + stdout.read())
    except:
        print("Could not connect to host over SSH: " + serverL)
    finally:
        client.close()

#  crackmapexec smb hostW -d domain -u user -p password -X 'whoami'
print("\nTesting all Windows server for access")
for serverW in windowsPCs:
    c = Client(ip, username=domain+"\/"+user, password=password, encrypt=False)
    try:
        c.connect()
        c.create_service()
        stdout = c.run_executable("cmd.exe", arguments="whoami")
        output = []
        output = stdout[0].decode("utf-8")
        print(output.split("\r\n")[1:3])
        c.remove_service()
    except:
        print("Could not connect to host over pyPSexec: " + serverW)
    finally:
        c.disconnect()
