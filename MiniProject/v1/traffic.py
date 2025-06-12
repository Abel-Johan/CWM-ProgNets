#!/usr/bin/env python3

import re
import time
import random

from scapy.all import *

class P4Traffic(Packet):
    name = "P4Traffic"
    fields_desc = [ StrFixedLenField("P", "P", length=1),
                    StrFixedLenField("Four", "4", length=1),
                    XByteField("version", 0x01),  
                    XByteField("Green_Light", 0x01), # let the initial green light be at Junction 1
                    XByteField("Green_Car", 0x00),
                    XByteField("J1_car", 0x00),
                    XByteField("J2_car", 0x00),
                    XByteField("J3_car", 0x00),
                    XByteField("J4_car", 0x00),
                    XByteField("J1_result", 0xca),
                    XByteField("J2_result", 0xfe),
                    XByteField("J3_result", 0xca),
                    XByteField("J4_result", 0xfe),
                    XByteField("J1_newcar", 0x00),
                    XByteField("J2_newcar", 0x00),
                    XByteField("J3_newcar", 0x00),
                    XByteField("J4_newcar", 0x00)]

bind_layers(Ether, P4Traffic, type=0x1234)

def get_if():
    ifs=get_if_list()
    iface= "enx0c37965f8a0f" # "h1-eth0"
    #for i in get_if_list():
    #    if "eth0" in i:
    #        iface=i
    #        break;
    #if not iface:
    #    print("Cannot find eth0 interface")
    #    exit(1)
    #print(iface)
    return iface
    
def simulate(cars):
    return cars - 1;    
    
def main():

    iface = "enx0c37965f8a0f"
    
    if len(sys.argv) < 6:
        print("Usage: python traffic.py [add|quit] <junction1_car> <junction2_car> <junction3_car> <junction4_car>")
        sys.exit(2)
    elif sys.argv[1] == "quit":
    	sys.exit(1)
    elif sys.argv[1] != "add":
        print("First command line argument is 'add' for normal usage")
    else:
    	j1_car = sys.argv[2]
    	j2_car = sys.argv[3]
    	j3_car = sys.argv[4]
    	j4_car = sys.argv[5]
    	
    print("Added successfully:")
    print(f"{j1_car} cars to Junction 1\n{j2_car} cars to Junction 2\n{j3_car} cars to Junction 3\n{j4_car} cars to Junction 4")
    old_green = 0x01 # green light entrance before it is changed by the P4 script
    timer = 0; # timer for use in v2
    while True:
    	time.sleep(2) # let the time taken for a car to clear the junction be 2s.
    	
    	try:
    	    pkt = Ether(dst='e4:5f:01:84:8c:5e', type=0x1234) / P4Traffic(J1_car = int(j1_car),
                                                                          J2_car = int(j2_car),
                                                                          J3_car = int(j3_car),
                                                                          J4_car = int(j4_car))
    	    pkt = pkt/' '
            #pkt.show()
    	    resp = srp1(pkt, iface=iface, timeout=5, verbose=False)
    	    if resp:
    	        p4traffic = resp[P4Traffic]
    	        if p4traffic:
    	            newcar = simulate(p4traffic.Green_Car)
    	            if p4traffic.Green_Light == 0x01:
    	            	# if p4traffic.Green_Light != old_green:    	            	    
    	                j1_car = newcar
    	            elif p4traffic.Green_Light == 0x02:
    	                j2_car = newcar
    	            elif p4traffic.Green_Light == 0x03:
    	                j3_car = newcar
    	            elif p4traffic.Green_Light == 0x04:
    	                j4_car = newcar
    	            print(j1_car, j2_car, j3_car, j4_car)
    	            additional_j2_car = random.choices([0, 1], weights=[75, 25])[0]
    	            j2_car += additional_j2_car
    	            if additional_j2_car:
    	                print(f"A new car has appeared on Junction 2({j1_car} {j2_car} {j3_car} {j4_car})")
    	        else:
    	            print("cannot find P4Traffic header in the packet")
    	        
    	    else:
    	        print("Didn't receive response")
    	except Exception as error:
    	    print(error)
    	
if __name__ == '__main__':
    main()


