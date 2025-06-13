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
		    XByteField("Junction_Timer", 0x00), # timer for how long the light has been green at a particular entrance
		    XByteField("Consecutive_Timer", 0x00), # timer between new cars entering the same entrance of a green entrance.
                    XByteField("J1_car", 0x00),
                    XByteField("J2_car", 0x00),
                    XByteField("J3_car", 0x00),
                    XByteField("J4_car", 0x00),
                    XByteField("New_green_car", 0x00)]

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
    
def simulate(cars, junction_timer, consecutive_timer):
    print(f"junc = {junction_timer}, cons = {consecutive_timer}")
    time.sleep(2) # let the time taken for a car to clear the junction be 2s.
    junction_timer += 2
    consecutive_timer += 2
    if cars >= 1:
    	return cars - 1, junction_timer, consecutive_timer
    else:
    	return cars, junction_timer, consecutive_timer

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
    	j1_car = int(sys.argv[2])
    	j2_car = int(sys.argv[3])
    	j3_car = int(sys.argv[4])
    	j4_car = int(sys.argv[5])
    	
    print("Added successfully:")
    print(f"{j1_car} cars to Junction 1\n{j2_car} cars to Junction 2\n{j3_car} cars to Junction 3\n{j4_car} cars to Junction 4")
    old_green = 0x01 # green light entrance before it is changed by the P4 script
    new_green = 0x01 # initialise for the case when we change light
    junction_timer = 0 # initialise timers
    consecutive_timer = 0 # initialise timers
    new_green_car = 0 # initialise the variable to give in any new cars entering the green entrance
    while True:
    	try:
    	    pkt = Ether(dst='e4:5f:01:84:8c:5e', type=0x1234) / P4Traffic(J1_car = j1_car,
                                                                          J2_car = j2_car,
                                                                          J3_car = j3_car,
                                                                          J4_car = j4_car,
                                                                          Green_Light = new_green,
                                                                          Junction_Timer = junction_timer,
                                                                          Consecutive_Timer = consecutive_timer,
                                                                          New_green_car = new_green_car)
    	    pkt = pkt/' '
            #pkt.show()
    	    resp = srp1(pkt, iface=iface, timeout=5, verbose=False)
    	    if resp:
    	        p4traffic = resp[P4Traffic]
    	        if p4traffic:
                    # if the green light changed entrances, then reset the timer
                    if p4traffic.Green_Light != old_green:
                        new_green = p4traffic.Green_Light
                        old_green = p4traffic.Green_Light
                    # simulate the 
                    newcar, junction_timer, consecutive_timer = simulate(p4traffic.Green_Car, p4traffic.Junction_Timer, p4traffic.Consecutive_Timer) 
                    
                    addn_j1_car = random.choices([0, 1], weights=[10, 90])[0]
                    addn_j2_car = random.choices([0, 1], weights=[30, 70])[0]
                    addn_j3_car = random.choices([0, 1], weights=[20, 80])[0]
                    addn_j4_car = random.choices([0, 1], weights=[15, 85])[0]
                                       
                    if p4traffic.Green_Light == 0x01:   	            	    
                        j1_car = newcar
                        new_green_car = addn_j1_car
                    elif p4traffic.Green_Light == 0x02:
                        j2_car = newcar
                        new_green_car = addn_j2_car
                    elif p4traffic.Green_Light == 0x03:
                        j3_car = newcar
                        new_green_car = addn_j3_car
                    elif p4traffic.Green_Light == 0x04:
                        j4_car = newcar
                        new_green_car = addn_j4_car
                    print(j1_car, j2_car, j3_car, j4_car)
                    time.sleep(2) # additional sleep to help read the CLI output
                    
                    j1_car += addn_j1_car
                    j2_car += addn_j2_car
                    j3_car += addn_j3_car
                    j4_car += addn_j4_car
                                 
                    print(f"After new cars have entered, if any:")
                    print(j1_car, j2_car, j3_car, j4_car)
                    print(f"green light is at {p4traffic.Green_Light}")
                    print(f"junction timer is {p4traffic.Junction_Timer}")
                    print(f"consecutive timer is {p4traffic.Consecutive_Timer}")
                    print(f"end of loop")
                    print("\n")
                    time.sleep(2) # additional sleep to help read the CLI output
    	        else:
    	            print("cannot find P4Traffic header in the packet")
    	        
    	    else:
    	        print("Didn't receive response")
    	        sys.exit(5)
    	except Exception as error:
    	    print(error)
    	    sys.exit(6)
    	
if __name__ == '__main__':
    main()


