import configparser, ipaddress, os, getpass
from ipaddress import IPv4Network

username = getpass.getuser()
config = configparser.ConfigParser()

savepath = '/home/' + username + '/context/'
filename = 'contextconfig.ini'
fullpath = os.path.join(savepath, filename)

print(fullpath)

config.read(fullpath)


def contextbuilder():
    """

    :return: 
    """

    custinfo = context(config, 'custinfo')
    custname = custinfo.custname
    custmonip = custinfo.custmonip
    custcap = custinfo.custcap

    for each_section in config.sections():

        customer = context(config, each_section)

        if 'custinfo' not in each_section:
            # print(customer.ips)
            if 'outsideint' in each_section:
                outsideint = makeadminint(customer.vlans, custname, customer.nameif, ' 4')
                allocateoutsideint = allocateint(customer.vlans, customer.nameif, '4')
                outsidevlans = makevlan(customer.vlans, custname, customer.nameif)
                outsideip = dirtyliststipper(customer.ips)
                outsidenameif = customer.nameif
                outsidevlan = dirtyliststipper(customer.vlans)
                outsideinteface = makeoutsideinterface(customer.vlans, outsidenameif, '4', customer.ips)

            if 'lbvpnint' in each_section:
                lbvpnnameif = customer.nameif
                lbvpnint = makeadminint(customer.vlans, custname, lbvpnnameif, ' 3')
                allocatelbvpnint = allocateint(customer.vlans, lbvpnnameif, '3')
                lbvpnvlans = makevlan(customer.vlans, custname, lbvpnnameif)
                lbvpnip = dirtyliststipper(customer.ips)
                lbvpnmonroutes = makeroutes(customer.ips, custmonip, lbvpnnameif)
                lbvpnlocal = makesubnet(customer.ips, lbvpnnameif)
                lbvpninterface = makeinterface(customer.vlans, custname, lbvpnnameif, '3', customer.ips)

            if 'asaint' in each_section:
                insidenameif = customer.nameif
                insideint = makeadminint(customer.vlans, custname, insidenameif, ' 2')
                allocateinsideint = allocateint(customer.vlans, insidenameif, '2')
                insidevlans = makevlan(customer.vlans, custname, insidenameif)
                insideip = uglyliststipper(customer.ips)
                insidemonroutes = makeroutes(customer.ips, custmonip, insidenameif)
                insidelocal = makesubnet(customer.ips, insidenameif)
                insidepat = makepat(customer.ips, custname, insidenameif)
                insideinterface = makeinterface(customer.vlans, custname, insidenameif, '2', customer.ips)

            if 'vrf' in each_section:
                vrfnameif = customer.nameif
                vrfint = makeadminint([customer.vlans[0]], custname, [vrfnameif[0]], ' 3')
                allocatevrfint = allocateint([customer.vlans[0]], [vrfnameif[0]], '3')
                vrfvlans = makevlan(customer.vlans, custname, vrfnameif)
                vrfip = uglyliststipper(customer.ips)
                vrfmonroutes = makeroutes(customer.ips[1:], custmonip, vrfnameif[1:])
                vrflocal = makesubnet(customer.ips[1:], vrfnameif[1:])
                vrfinterface01 = makevrfinterface01(customer.vlans, custname, vrfnameif, '3', customer.ips)
                vrfinterface02 = makevrfinterface02(customer.vlans, custname, vrfnameif, '3', customer.ips)
                vrftransitasa = makeinterface([customer.vlans[0]], custname, [vrfnameif[0]], '3', [customer.ips[0]])
                vrfasaroutes = makeasavrfroutes(customer.ips[1:], customer.ips[0], vrfnameif[1:])
                vrf = """vrf context {}""".format(custname.upper())

            if 'vrf' and 'asaint' in each_section:
                vrfnameif = customer.nameif
                routeip = str(iphost(customer.ips[0])[1])
                vrfroutes = makeroutes(customer.ips, routeip, vrfnameif)



                # print(vrfroutes)


        else:
            lbvpnnameif = ''
            lbvpnint = ''
            allocatelbvpnint = ''
            lbvpnvlans = ''
            lbvpnip = ''
            lbvpnmonroutes = ''
            lbvpnlocal = ''
            lbvpninterface = ''
            vrfnameif = ''
            vrfint = ''
            allocatevrfint = ''
            vrfvlans = ''
            vrfip = ''
            vrfmonroutes = ''
            vrflocal = ''
            vrfinterface01 = ''
            vrfinterface02 = ''
            vrftransitasa = ''
            vrfasaroutes = ''
            vrf = ''
            vrfnameif = ''
            routeip = ''
            vrfroutes = ''

        if 'custinfo' in each_section:
            moninterface = makemoninterface('3004', 'mon', '4', custmonip, custname)

    newcustomer = (newcustconfig(
        outsidevlans,
        custname,
        custcap,
        outsideip,
        outsideint,
        lbvpnint,
        insideint,
        allocateoutsideint,
        allocatelbvpnint,
        allocateinsideint,
        lbvpnvlans,
        insidevlans,
        outsidevlan,
        lbvpnmonroutes,
        insidemonroutes,
        lbvpnlocal,
        insidelocal,
        insidepat,
        insideinterface,
        lbvpninterface,
        outsideinteface,
        moninterface,
        vrfinterface01,
        vrfinterface02,
        vrf,
        vrfroutes,
        vrfvlans,
        allocatevrfint,
        vrflocal,
        vrfmonroutes,
        vrftransitasa,
        vrfint,
        vrfasaroutes

    ))
    # fout = open(custname + "_template.txt", "w")
    # fout.write(newcustomer)
    # fout.close()
    return newcustomer


class context(object):
    def __init__(self, config, interface):
        """

        :param config: 
        :param interface: 
        """

        self.sections = self.getSections(config)
        self.vals = context.getvals(config, interface)
        self.keys = context.getkeys(config, interface)

        self.nameif = context.getnameif(self.vals)
        self.vlans = context.getvlans(self.vals)
        self.ips = context.getips(self.vals)

        self.custname = context.getcustname(self.vals)
        self.custmonip = context.getcustmonip(self.vals)
        self.custcap = context.getcustcap(self.vals)

    def getSections(self, config):
        """

        :param config: 
        :return: 
        """
        list = []
        for each_section in config.sections():
            list.append(each_section)
        return list

    def getvals(config, item):
        """

        :param item: 
        :return: 
        """
        list = []
        for (each_key, each_val) in config.items(item):
            list.append(each_val)
        return list

    def getkeys(config, item):
        """

        :param item: 
        :return: 
        """
        list = []
        for (each_key, each_val) in config.items(item):
            list.append(each_key)
        return list

    def getnameif(list):
        """

        :return: 
        """
        return list[::3]

    def getvlans(list):
        """

        :return: 
        """
        return list[1::3]

    def getips(list):
        """

        :return: 
        """
        return list[2::3]

    def getcustname(list):
        """

        :return: 
        """
        return list[0]

    def getcustmonip(list):
        """

        :return: 
        """
        return list[1]

    def getcustcap(list):
        """

        :return: 
        """
        return list[2]


def iphost(ipwithsubnet):
    """

    :param ipwithsubnet: 
    :return: 
    """
    iprange = ipaddress.ip_network(ipwithsubnet)
    return iprange


def ipsubnet(ipwithsubnet):
    """

    :param ipwithsubnet: 
    :return: 
    """
    iprange = ipaddress.ip_network(ipwithsubnet)
    ipsubnet = iprange.netmask
    return ipsubnet


def dirtyliststipper(johndoe):
    """

    :param johndoe: 
    :return: 
    """
    naked = ''
    for pp in johndoe:
        naked += ((str(pp).replace('[', '')).replace(']', '')).replace('\'', '')
    return naked


def uglyliststipper(johndoe):
    """

    :param johndoe: 
    :return: 
    """
    naked = ''
    for pp in johndoe:
        naked += ((str(pp).replace('[', '')).replace(']', '')).replace('\'', '') + '\n'
    return naked


def makevlan(vlans, customerid, nameif):
    """

    :param vlans: 
    :param customerid: 
    :param nameif: 
    :return: 
    """

    if len(vlans) == len(nameif):
        vlanstring = ""
        y = 0
        for x in nameif:
            vlanstring += """
vlan {0}
  name {1}_{2}
                """.format(vlans[y], customerid.upper(), nameif[y])
            y += 1
            # print(vlanstring)
    else:
        print("lists are not the same length")
    return vlanstring


def makeadminint(vlans, customerid, nameif, intnumber):
    """

    :param vlans: 
    :param customerid: 
    :param nameif: 
    :param intnumber: 
    :return: 
    """

    if len(vlans) == len(nameif):
        vlanstring = ""
        y = 0
        for x in nameif:
            vlanstring += """
!
interface Port-channel{3}.{0}
 description {1}_{2}
 vlan {0}
! """.format(vlans[y], customerid.upper(), nameif[y], intnumber)
            y += 1
            # print(vlanstring)
    else:
        print("lists are not the same length")
    return vlanstring


def makeroutes(customerips, nextip, nameif):
    """

    :param customerips: 
    :param nextip: 
    :param nameif: 
    :return: 
    """

    if len(customerips) == len(nameif):
        nextip = nextip.partition('/')[0]
        routes = ""
        y = 0
        for x in nameif:
            routes += """
		ip route {0} {1}
                """.format(str(customerips[y]), nextip)
            y += 1
    else:
        print("lists are not the same length")
    return routes


def makeasavrfroutes(customerips, nextip, nameif):
    if len(customerips) == len(nameif):
        nextip = iphost(nextip)[1]

        customerips = [iphost(ips) for ips in customerips]
        customersubnet = [ipsubnet(subnets) for subnets in customerips]
        # customerips = str(customerips).replace('/', ' ')
        
        routes = ""
        y = 0
        for x in nameif:
            routes += """
route {0} {1} {2} {3} 1 
                """.format(nameif[0], str(customerips[y]).split('/', 1)[0], customersubnet[y], nextip)
            y += 1

            # str(customerips[y]).split('/',1)[0]
    else:
        print("lists are not the same length")
    return routes


def makesubnet(customerips, nameif):
    """

    :param customerips: 
    :param nameif: 
    :return: 
    """

    if len(customerips) == len(nameif):

        customerips = [iphost(ips) for ips in customerips]

        customersubnet = [ipsubnet(subnets) for subnets in customerips]

        vlanstring = ""
        y = 0
        for x in nameif:
            vlanstring += """
network-object {0} {1}
                """.format(str(customerips[y]).split('/', 1)[0], customersubnet[y])
            # .format(str(customerips[y]).replace('/24', ''), customersubnet[y])
            y += 1
    else:
        print("lists are not the same length")
    return vlanstring


def makepat(customerips, custname, nameif):
    """

    :param customerips: 
    :param custname: 
    :param nameif: 
    :return: 
    """
    customerips = iphost(customerips[0])
    customersubnet = ipsubnet(customerips[0])

    vlanstring = ""

    vlanstring += """
!
object network {2}_INSIDE_NETWORK_PAT
subnet {0} {1}
!
object network {2}_INSIDE_NETWORK_PAT
nat ({3},outside) dynamic interface
!
                    """.format(str(customerips[0]).partition('/')[0], customersubnet, str(custname).upper(), nameif[0])

    return vlanstring


def makeinterface(vlans=None, customerid=None, nameif=None, intnumber=None, customerips=None):
    """

    :param vlans: 
    :param customerid: 
    :param nameif: 
    :param intnumber: 
    :param customerips: 
    :return: 
    """
    interface = ""
    if len(vlans) == len(nameif):

        customerips = [iphost(ips) for ips in customerips]
        customersubnet = [ipsubnet(subnets) for subnets in customerips]

        y = 0
        level = 100
        for x in nameif:
            interface += """
interface Port-channel{3}.{0}
 nameif {2}
 security-level {4}
 ip address {5} {6} standby {7}
!
access-list {2}_access_in remark ************* START EXAMPLE ACL ********************
access-list {2}_access_in extended permit icmp object-group LOCAL_NETWORKS any object-group ICMP_ALLOWED
access-list {2}_access_in extended permit udp object-group LOCAL_NETWORKS any eq domain
access-list {2}_access_in extended permit tcp object-group LOCAL_NETWORKS any eq domain
access-list {2}_access_in extended permit tcp object-group LOCAL_NETWORKS object-group AVAMAR_NODES object-group AVAMAR_REPLICATION
access-list {2}_access_in extended permit tcp object-group LOCAL_NETWORKS object-group TACACS_SERVERS eq tacacs
access-list {2}_access_in remark ************* END EXAMPLE ACL ********************
access-list {2}_access_in remark --


access-group {2}_access_in in interface {2}
""".format(vlans[y], customerid.upper(), nameif[y], intnumber, level, str(customerips[y][1]).partition('/')[0],
           customersubnet[y], str(customerips[y][2]).partition('/')[0])
            y += 1
            level -= 5

        return interface


def makeoutsideinterface(vlans=None, nameif=None, intnumber=None, customerips=None):
    """

    :param vlans: 
    :param nameif: 
    :param intnumber: 
    :param customerips: 
    :return: 
    """
    interface = ""
    customerips = iphost(customerips[0])
    customersubnet = ipsubnet(customerips[0])

    interface += """
!
interface Port-channel{5}.{0}
 nameif {1}
 security-level 0
 ip address {6} {3} standby {4}

access-list {1}access_in remark ********* REMOVE RULE ONCE S2S IS ESTABLISHED ***********
access-list {1}_access_in extended permit tcp host 1.1.1.1 host 1.1.1.1 eq 443
access-list {1}_access_in remark ********* REMOVE RULE ONCE S2S IS ESTABLISHED  ***********

!
access-group {1}_access_in in interface {1}
!
route outside 0.0.0.0 0.0.0.0 {2} 1
!                    
    """.format(vlans[0], nameif[0], str(customerips[1]), customersubnet,
               str(customerips[5]), intnumber, str(customerips[4]))

    return interface


def makevrfinterface01(vlans=None, customerid=None, nameif=None, intnumber=None, customerips=None):
    """

    :param vlans: 
    :param customerid: 
    :param nameif: 
    :param intnumber: 
    :param customerips: 
    :return: 
    """
    interface = ""
    if len(vlans) == len(nameif):

        customerips = [iphost(ips) for ips in customerips]
        customersubnet = [ipsubnet(subnets) for subnets in customerips]
        y = 0
        priority = 100
        for x in nameif:
            interface += """
!
interface Vlan{0}
  description {1} {2}
  no shutdown
  vrf member {1}
  no ip redirects
  ip address  {5}
  hsrp version 2
  hsrp {0}
    preempt 
    priority {6} forwarding-threshold lower 1 upper {6}
    ip {4}
!
""".format(vlans[y], customerid.upper(), nameif[y], intnumber, str(customerips[y][1]).partition('/')[0],
           str(customerips[y][2]).partition('/')[0], priority)
            y += 1

        return interface


def makevrfinterface02(vlans=None, customerid=None, nameif=None, intnumber=None, customerips=None):
    """

    :param vlans: 
    :param customerid: 
    :param nameif: 
    :param intnumber: 
    :param customerips: 
    :return: 
    """
    interface = ""
    if len(vlans) == len(nameif):

        customerips = [iphost(ips) for ips in customerips]
        customersubnet = [ipsubnet(subnets) for subnets in customerips]
        y = 0
        priority = 110
        for x in nameif:
            interface += """
!
interface Vlan{0}
  description {1} {2}
  no shutdown
  vrf member {1}
  no ip redirects
  ip address  {5}
  hsrp version 2
  hsrp {0}
    preempt 
    priority {6} forwarding-threshold lower 1 upper {6}
    ip {4}
!
""".format(vlans[y], customerid.upper(), nameif[y], intnumber, str(customerips[y][1]).partition('/')[0],
           customerips[y][3], priority)
            y += 1

        return interface


def makemoninterface(vlans=None, nameif=None, intnumber=None, customerips=None, custname=None):
    moninterface = ""
    monip = customerips.rpartition('/')[0]
    monip = ipaddress.IPv4Address(monip)

    moninterface += """
!
interface Port-channel{5}.{0}
 nameif {1}
 security-level 10
 ip address {2} {3} standby {6}
!
route {1} 10.101.0.0 255.255.255.0 1.1.1.1 1
route {1} 10.10.0.0 255.255.0.0 1.1.1.1 1
!
aaa-server TACACS+ protocol tacacs+
aaa-server TACACS+ ({1}) host 10.10.10.10
 key P@ssw0rd
aaa-server TACACS+ ({1}) host 10.10.10.10
 key P@ssw0rd
aaa authentication ssh console TACACS+ LOCAL
aaa authentication enable console TACACS+ LOCAL
!
snmp-server group vpn-group v3 priv
snmp-server user {7} vpn-group v3 auth sha {7} priv aes 128 {7}
snmp-server host {7} 10.101.20.20 version 3 {7}
snmp-server location DATACENTER
snmp-server contact Network Team 1-800-696-6969
snmp-server enable traps snmp authentication linkup linkdown coldstart
!
ssh 10.101.20.21 255.255.255.255 {1}
!
access-list {1}_access_in line 1 remark ************* START EXAMPLE ACL ************************
access-list {1}_access_in line 2 extended permit tcp object-group DUMMY_OBJECT_GROUP object-group LOCAL_NETWORKS object-group DUMMY_PORTS
access-list {1}_access_in line 6 remark ************* END EXAMPLE ACL ************************

!
access-group {1}_access_in in interface {1}
!
logging host mon 10.10.10.11
!
                        """.format(vlans, nameif, str(customerips).partition('/')[0], "255.255.255.0",
                                   monip, intnumber, monip + 1, custname)

    return moninterface


def allocateint(vlans, nameif, intnumber):
    if len(vlans) == len(nameif):
        interface = ""
        y = 0
        for x in nameif:
            interface += """
allocate-interface Port-channel{1}.{0}
            """.format(vlans[y], intnumber)
            y += 1
            # print(vlanstring)
    else:
        print("lists are not the same length")
    return interface


def newcustconfig(outsidevlans,
                  custname,
                  cap,
                  outsideip,
                  outsideint,
                  lbvpnint,
                  insideint,
                  allocateoutsideint,
                  allocatelbvpnint,
                  allocateinsideint,
                  lbvpnvlans,
                  insidevlans,
                  outsidevlan,
                  lbvpnmonroutes,
                  insidemonroutes,
                  lbvpnlocal,
                  insidelocal,
                  insidepat,
                  insideinterface,
                  lbvpninterface,
                  outsideinteface,
                  moninterface,
                  vrfinterface01,
                  vrfinterface02,
                  vrf,
                  vrfroutes,
                  vrfvlans,
                  allocatevrfint,
                  vrflocal,
                  vrfmonroutes,
                  vrftransitasa,
                  vrfint,
                  vrfasaroutes

                  ):
    outsideip = iphost(outsideip)
    outsidesubnet = ipsubnet(outsideip)

    fwtemplate = """

PLEASE REVIEW CONFIG BEFORE ADDING IT AND UPDATE IPAM!!!!!


--------------------------------------------------------------------------
DISTSW01 CONFIG:
--------------------------------------------------------------------------


!
    {0}
    {13}
    {14}
    {29}
!
interface vlan {15}
     no shutdown
      description {1} network outside vlan
      vrf member outside
      ip address {4}/{6}
      ip router ospf 1 area 0.0.0.0
      hsrp version 2
      hsrp {15}
          preempt
          priority 110
          ip {3}
!    
    {25}
!
vlan configuration {15}
      service-policy type qos input {2}MbCAP
      service-policy type qos output {2}MbCAP
!
    {27}
    {28}
!

--------------------------------------------------------------------------
DISTSW02 CONFIG:
--------------------------------------------------------------------------

!
    {0}
    {13}
    {14}
    {29}
!
interface vlan {15}
     no shutdown
      description {1} network outside vlan
      vrf member outside
      ip address {5}/{6}
      ip router ospf 1 area 0.0.0.0
      hsrp version 2
      hsrp {15}
          preempt
          priority 120
          ip {3}
!
    {26}
!
vlan configuration {15}
      service-policy type qos input {2}MbCAP
      service-policy type qos output {2}MbCAP
!
    {27}
    {28}
!

--------------------------------------------------------------------------
ACCESS SW CONFIG:
--------------------------------------------------------------------------

!
    {13}
    {14}
    {29}
!
--------------------------------------------------------------------------
MONITORING ROUTES:
--------------------------------------------------------------------------

!
 vrf context mon
  {16}
  {17}
  {32}
! 
--------------------------------------------------------------------------
FIREWALL CONFIG:
--------------------------------------------------------------------------
!
Changeto context system
!
{7}
{8}
{9}
{34}
!
context {1}
allocate-interface Port-channel1.3004
{10}
{11}
{12}
{30}
config-url disk0:/{1}.cfg
!
!
Changeto context {1}
!
!
hostname {1}
enable password P@ssw0rd
passwd P@ssw0rd
no names
!
pager lines 24
logging enable
logging timestamp
logging buffer-size 100000
logging buffered debugging
logging trap debugging
logging asdm informational
logging device-id hostname
!
no http server enable
!
ssh timeout 5
ssh version 2
!
banner motd
banner motd PUT YOUR BANNER HERE
banner motd
!
crypto key generate rsa modulus 1024
!
username localuser password P@ssw0rd
!
{20}
object-group network LOCAL_NETWORKS
{18}
{19}
{31}

object-group network DUMMY_OBJECT_GROUP 
description dummy object group
network-object host 10.10.10.20
!
object-group service DUMMY_PORTS tcp
description dummy ports
port-object eq 3389
port-object eq ssh

{24}
{23}
{21}
{22}
{33}
{35}
    """.format(outsidevlans,
               str(custname).upper(),
               cap,
               outsideip[1],
               outsideip[2],
               outsideip[3],
               outsideip.prefixlen,
               outsideint,
               lbvpnint,
               insideint,
               allocateoutsideint,
               allocatelbvpnint,
               allocateinsideint,
               lbvpnvlans,
               insidevlans,
               outsidevlan,
               lbvpnmonroutes,
               insidemonroutes,
               lbvpnlocal,
               insidelocal,
               insidepat,
               insideinterface,
               lbvpninterface,
               outsideinteface,
               moninterface,
               vrfinterface01,
               vrfinterface02,
               vrf,
               vrfroutes,
               vrfvlans,
               allocatevrfint,
               vrflocal,
               vrfmonroutes,
               vrftransitasa,
               vrfint,
               vrfasaroutes
               )

    return fwtemplate


if __name__ == "__main__":
    main()
