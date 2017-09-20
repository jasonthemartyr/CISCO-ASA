# Network-Class

A collection of functions and a class used to filter a "sh run" for a CISCO ASA firewall and match routes/access-group based on source IP.


Example:

sourceip = "10.101.0.85"

sourcecidr = "32"

destip = "10.101.1.10"

destcidr = "32"

protocol = "tcp"

portnum = "69"






produces:

access-list inside_access_out extended permit tcp host 10.101.0.85 host 10.101.1.10 eq 69

access-list mon_access_in extended permit tcp host 10.101.0.85 host 10.101.1.10 eq 69

Process finished with exit code 0


