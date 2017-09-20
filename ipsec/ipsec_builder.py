from ipaddress import *

def objgrp(trafficlist, customerid, location):
    converttoip = [IPv4Network(x) for x in trafficlist]

    print("\nobject-group network %s_%s_NETWORKS" % (customerid,location))
    for x in converttoip:
        if "/32" in str(x):
            print("network-object host " + str(x[0]))
        elif "/32" not in str(x):
            print("network-object " + x.with_netmask.replace("/"," "))

def ipsec(customerid,peerip,psk):
    ipsec = """
    crypto ikev1 enable outside
    crypto ikev1 policy 10
     authentication pre-share
     encryption aes-256
     hash sha
     group 2
     lifetime 86400
    crypto ipsec ikev1 transform-set {0}-AES-256 esp-aes-256 esp-sha-hmac
    crypto map {0}-MAP 10 match address {0}_L2L
    crypto map {0}-MAP 10 set peer {1}
    crypto map {0}-MAP 10 set ikev1 transform-set {0}-AES-256
    crypto map {0}-MAP 10 set security-association lifetime seconds 28800
    crypto map {0}-MAP interface outside
    tunnel-group {1} type ipsec-l2l
    tunnel-group {1} ipsec-attributes
     ikev1 pre-shared-key {2}
    access-list {0}_L2L remark ************ BEGIN {0} L2L ************
    access-list {0}_L2L extended permit ip object-group {0}_LOCAL_NETWORKS object-group {0}_REMOTE_NETWORKS
    access-list {0}_L2L remark ************ END {0} L2L ************
    nat (inside,outside) source static {0}_LOCAL_NETWORKS {0}_LOCAL_NETWORKS destination static {0}_REMOTE_NETWORKS {0}_REMOTE_NETWORKS
    """.format(str(customerid),str(peerip),str(psk))
    print(ipsec)


def Main():
    local = "LOCAL"
    remote = "REMOTE"
    customerid = input("\nplease enter the customer code: \n").upper()
    peerip = input("\nPlease enter the REMOTE peer IP: \n")
    print("Please enter FNTS hosted encryption domain source traffic ie:\n   10.100.20.40/32 \n   10.110.30.30/16 \n Press ENTER when done.\n")
    srctraffic = (input().split())
    print("\nPlease enter CUSTOMER hosted encryption domain destination traffic ie:\n   10.100.20.40/32 \n   10.110.30.30/16 \n Press Enter when done.\n")
    dsttraffic = (input().split())
    psk = input("\nPlease enter a PSK: \n")
    ipsec(customerid,peerip,psk)
    objgrp(srctraffic,customerid,local)
    objgrp(dsttraffic,customerid,remote)


Main()