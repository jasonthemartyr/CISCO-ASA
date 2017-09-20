# import ipaddress
import socket
import struct
from socket import inet_ntoa
from ipaddress import IPv4Address, IPv4Network, ip_network
from cassandra.cluster import Cluster
from netaddr import IPAddress

cluster = Cluster(['10.110.0.121'])
session = cluster.connect()
session.set_keyspace('fnts')

cmd = 'sh run'


def asahostname(asa):
    hostname = [str(line).replace("hostname", "")
                for line in asa if "hostname" in line and "logging" not in line]
    return hostname


def aclname(sourceip, dict):  # similar to aclname in ACL.py, returns ACL name
    # i.e. print(aclname(source_ip, asaintdict))
    for subnet, interface in dict.items():
        if IPv4Address(sourceip) in subnet:
            interfaces = interface
    if "interfaces" in locals():
        return interfaces
    else:
        return "outside"



def findkey(inputdict, value):  # return matching key
    # return {k for k, v in inputdict.items() if v == value}

    return next(k for k, v in inputdict.items() if v == value)


def cidr(prefix):
    return socket.inet_ntoa(struct.pack(">I", (0xffffffff << (32 - prefix)) & 0xffffffff))


def IPInfo(IPAddr, IPMask):
    if IPMask == "32":
        return ("host " + IPAddr)
    else:
        return (IPAddr + " " + str(cidr(int(IPMask))))


class Asafilter(object):
    def __init__(self, asa):
        self.asa = (asa.rpartition(cmd)[-1]).splitlines()
        self.asafiltered = Asafilter.asawordfilter(self.asa)
        self.asaint = Asafilter.asafilterint(self.asa)
        self.asagroup = Asafilter.asafiltergroup(self.asa)
        self.asalist = Asafilter.asafilteracl(self.asa)

    def asawordfilter(asa):
        asafilter = [str(line).replace('^M', '').replace(
            '#', '').replace('exit', '') for line in asa]
        return list(filter(None, asafilter))

    def asafilterint(asa):
     #function has issues with white spaces in sh run output
        asaint = []
        stringlist = [" shutdown", " description LAN/STATE Failover Interface", "management-only",
                      "channel-group 1 mode on"]

        asaiter = iter(asa)
        for line in asaiter:
            # if "0.0.0.0 0.0.0.0" in line:
            #     continue
           
            if line.startswith("interface "):
             
                #print(asaiter)
                checker = True
                #if any(desc in stringlist for desc in next(asaiter)):
                # for desc in next(asaiter):
                #
                #     nextline = desc
                nextline = next(asaiter)
                print(nextline)
                for string in stringlist:

                    if string in nextline:
                        checker = False
                        break
                if checker:

                #if any(stringlist in desc):
                    #print("print()")
                    nameif = (next(asaiter)).replace(" nameif ", "")
                    securitylvl = next(asaiter)
                    print(securitylvl)
                    iplvl = next(asaiter)
                    print(iplvl)
                    # ipadd = (((next(asaiter)).rpartition(" standby")[
                    #               0]).replace(" ip address ", "")).split()
                    ipadd = (((iplvl).rpartition(" standby")[
                                0]).replace(" ip address ", "")).split()
                    print(ipadd, line)
                    ipsubnet = IPAddress(ipadd[1]).netmask_bits()
                    ipcombined = str(ipadd[0]) + "/" + str(ipsubnet)
                    asaint.extend((ip_network(
                        ipcombined, strict=False), nameif))
                else:
                    print("else:")
                    pass

            if "route " in line and "outside" not in line:
                routes = line.split()
                intname = routes[1]
                asaroutes = routes[2]
                try:
                    asasubnet = IPAddress(routes[3]).netmask_bits()
                except IndexError:
                    asasubnet = str("255.255.255.0")

                asacombined = str(asaroutes) + "/" + str(asasubnet)
                try:
                    asaint.extend((IPv4Network(asacombined), intname))
                except:
                    # print("general error: ", sys.exc_info()[0])
                    continue
        print(asaint)
        return asaint

    def asafiltergroup(asa):
        asagroupdict = {}
        for group in asa:
            if (group.startswith("access-group ")):
                aclintname = (group.rpartition(" in interface")
                              [0]).replace("access-group ", "")
                aclname2 = group.rpartition("in interface ")[-1]
                asagroupdict[aclintname] = aclname2
        return asagroupdict

    def asafilteracl(asa):
        asaacl = []
        stringlist2 = ["mon", "remark", "mon_access_in"]
        asaiter = iter(asa)
        for line in asaiter:
            if line.startswith("access-list ") and not any(desc in line for desc in stringlist2):
                asaacl.append(line)
        return asaacl


def fwruleoutput(sourceip, sourcecidr, destip, destcidr, protocol, portnum, nodeid):
    """
    This function generates access-lists for CISCO ASA.
    Pulls running-config from Cassandra,
    filters on nodeID,
    and matches source IP to access-list in CISCO ASA running-config.
    :param sourceip:
    :param sourcecidr:
    :param destip:
    :param destcidr:
    :param protocol:
    :param portnum:
    :param nodeid:
    :return:
    """
  
    select= 'SELECT  \"NodeID\",\"DownloadTime\", config FROM fnts.auto_configs WHERE solr_query=\'{\"q\":\"CustomerID:0000001\",\"sort\":\"DownloadTime desc\"}\limit 1'
    rows = session.execute(select)
   #solr query to get sh run from cassandra
    for user_row in rows:
        shrun = str(user_row.config)
        print(shrun)
        print(user_row.DownloadTime)

    ciscoasa = Asafilter(shrun)
    asaint = iter(ciscoasa.asaint)
    #print(asaint)
    # for item in asaint:
    #     print(item)

    asaintdict = dict(zip(asaint, asaint))
    #print(asaintdict)

    asagroup = ciscoasa.asagroup

    aclnames = aclname(sourceip, asaintdict)
    groupname = findkey(asagroup, aclnames)

    srcIPconfig = IPInfo(sourceip, sourcecidr)
    dstIPconfig = IPInfo(destip, destcidr)
    # print(asaintdict.values())
    # print(*ciscoasa.asalist,sep="\n")
    # for key, value in asaintdict.items():
    #     print(key, value)

    return (
    "access-list %s extended permit %s %s %s eq %s" % (str(groupname), protocol, srcIPconfig, dstIPconfig, portnum))


def main():
    #nodeid=4166
    #print('SELECT  \"NodeID\",\"DownloadTime\", config FROM fnts.auto_configs WHERE solr_query=\'{\"q\":\"NodeID:4166\", \"sort\":\"DownloadTime desc\"}\' limit 1')
    x = fwruleoutput(sourceip="10.111.13.112",
                     sourcecidr="32",
                     destip="10.101.0.0",
                     destcidr="24",
                     protocol="udp",
                     portnum="53",
                     nodeid="4166")
    print(x)


if __name__ == "__main__":
    main()
