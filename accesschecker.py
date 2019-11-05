#!/usr/bin/env python

from pypsexec.client import Client
import os
import time
import sys
import paramiko
import nmap
import fileinput
import socket
import warnings
warnings.filterwarnings(action='ignore',module='.*paramiko.*')

file = "hosts.txt"
user = 'helo'
password = 'M4gd4l3n4'
executable = "hostname"
arguments = "/all"
port = 22
linuxPCs = []
windowsPCs = []

#NMAP
nm = nmap.PortScanner()

with open(file) as ipFile:
    for ipLine in ipFile:
        ip = ipLine.strip()
        if ip: # just in case there was a blank line
            nm.scan(ip, arguments='-O')
            print("Server: " + ip + " " + nm[ip].hostname())
            operatingOS = nm[ip]['osmatch'][0]['osclass'][0]['osfamily']
            print("OS: " + operatingOS)

            if operatingOS == 'Linux':
                linuxPCs.append(ip)

            if operatingOS == 'Windows':
                windowsPCs.append(ip)

print("\nTesting all Linux server for access")
for serverL in linuxPCs:
    try: # if Linux
        client = paramiko.SSHClient()
        #client.load_system_host_keys()
        client.set_missing_host_key_policy(paramiko.WarningPolicy)
        client.connect(ip, port=port, username=user, password=password)
        stdin, stdout, stderr = client.exec_command(executable)
        print("Server: " + serverL + " Hostname: " + stdout.read())
    except:
        print("Could not connect to host over SSH: " + serverL)
    finally:
        client.close()

print("\nTesting all Windows server for access")    
for serverW in windowsPCs:
    c = Client(ip, username=user, password=password, encrypt=False)
    try:
    	c.connect()
    	c.create_service()
    	stdout = c.run_executable("cmd.exe", arguments="whoami")
        c.remove_service()
    except:
        print("Could not connect to host over pyPSexec: " + serverW)
    finally:
    	c.disconnect()
