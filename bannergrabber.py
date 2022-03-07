#!/bin/python
import socket
import sys
import os

#grab the banner
def grab_banner(ip_address,port):
    try:
        s=socket.socket()
        s.connect((ip_address,int(port)))
        banner = s.recv(1024).decode("utf-8")
        print (ip_address + ',' + str(port) + ',' + str(banner))
    except BaseException as e:
        print (e)
    return

if __name__ == "__main__":
    if len(sys.argv) > 1:
        grab_banner(sys.argv[1],sys.argv[2])
    else:
        print("usage: IP ADDRESS PORT")
    exit()
