#!/usr/bin/env python3

import re
import time
import random

from scapy.all import *

"""
CONSTANTS
"""
SLEEP_TIME = 0.5 # Amount of seconds to sleep in some of the sleep functions. Useful for reading command-line outputs
SECONDS_PER_ITERATION = 2 # Amount of seconds each iteration of the while loop should model
CARS_PER_ITERATION = 2 # Number of cars that can pass through the junction each iteration

# Percentage chance at each iteration this junction will get a new car incoming
J1_CHANCE = 30
J2_CHANCE = 70
J3_CHANCE = 60
J4_CHANCE = 50



class P4Traffic(Packet):
    """
    Defines the format of the sent packet. In this case, each field is worth 1 byte.
    """
    name = "P4Traffic"
    fields_desc = [ StrFixedLenField("P", "P", length=1),
                    StrFixedLenField("Four", "4", length=1),
                    XByteField("version", 0x01),  
                    XByteField("Green_Light", 0x01),       # Let the initial green light be at Junction 1
                    XByteField("Green_Car", 0x00),         # How many cars there are at the greenlit entrance
		            XByteField("Junction_Timer", 0x00),    # Timer for how long the light has been green at a particular entrance
		            XByteField("Consecutive_Timer", 0x00), # Timer between new cars entering the same entrance of a green entrance
                    XByteField("J1_car", 0x00),            # Number
                    XByteField("J2_car", 0x00),            # of cars
                    XByteField("J3_car", 0x00),            # at each
                    XByteField("J4_car", 0x00),            # entrance
                    XByteField("New_green_car", 0x00)]     # Number of cars entering the green junction at each iteration

bind_layers(Ether, P4Traffic, type=0x1234)
    
def simulate(cars, junction_timer, consecutive_timer):
    """
    Simulates the cars passing through the junction by decrement the number of cars at the green entrance.
    Also implements the timer that keeps track of how long this particular entrance has been green for (junction_time)
    and the amount of time since the last time a new car entered the green entrance (consecutive_timer)
    """
    time.sleep(SLEEP_TIME) # let the time taken for a car to clear the junction be 2s.
    junction_timer += SECONDS_PER_ITERATION
    consecutive_timer += SECONDS_PER_ITERATION
    if cars - CARS_PER_ITERATION > 0:
        return cars - CARS_PER_ITERATION, junction_timer, consecutive_timer
    else:
    	return 0, junction_timer, consecutive_timer

def main():
    """
    Main function
    """
    iface = "enx0c37965f8a0f"
    
    # Take in command line arguments, with error checking that the correct arguments are given
    # The 3rd up to 6th arguments describe the initial number of cars at each junction entrance
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
    
    # Confirmation about the number of cars added at each junction entrance
    print("Added successfully:")
    print(f"{j1_car} cars to Entrance 1\n{j2_car} cars to Entrance 2\n{j3_car} cars to Entrance 3\n{j4_car} cars to Entrance 4")

    # Initial values to be passed onto the packet's fields.
    # While we have defined default values above, since we are feeding output from the previous iteration into the inputs of the next iteration,
    # and we are using the same variables, these variables need to be initialised for the first iteration.
    old_green = 0x01 # initialise which entrance is green
    new_green = 0x01 # initialise for the case when we change light
    junction_timer = 0 # initialise junction_timer
    consecutive_timer = 0 # initialise consecutive_timer
    new_green_car = 0 # initialise the number of new cars entering the green entrance

    # Iterate to model the traffic flow over discretised timestamps
    while True:
    	try:
            # Establish the destination of packet, Ethernet type to use, and any variables to send with non-default values
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
                # Get a response from the interface and place into variable for easy access
                p4traffic = resp[P4Traffic]
                if p4traffic:
                    # if the green light changed entrances, then update what the new green light is, and what the previous green light was
                    if p4traffic.Green_Light != old_green:
                        new_green = p4traffic.Green_Light
                        old_green = p4traffic.Green_Light

                    # simulate the movement of cars
                    newcar, junction_timer, consecutive_timer = simulate(p4traffic.Green_Car, p4traffic.Junction_Timer, p4traffic.Consecutive_Timer) 
                    
                    # randomly decide whether or not to add a car into each of the junction entrances
                    addn_j1_car = random.choices([0, 1], weights=[100-J1_CHANCE, J1_CHANCE])[0]
                    addn_j2_car = random.choices([0, 1], weights=[100-J2_CHANCE, J2_CHANCE])[0]
                    addn_j3_car = random.choices([0, 1], weights=[100-J3_CHANCE, J3_CHANCE])[0]
                    addn_j4_car = random.choices([0, 1], weights=[100-J4_CHANCE, J4_CHANCE])[0]
                    
                    # after simulation, update the number of cars on the green entrance
                    # moreover, update the number of new cars entering the green entrance
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

                    # print out the remaining cars at each entrance to the junction, before new cars have entered
                    print(j1_car, j2_car, j3_car, j4_car)
                    time.sleep(SLEEP_TIME) # additional sleep to help read the CLI output
                    
                    # add the new cars to the current number of cars
                    j1_car += addn_j1_car
                    j2_car += addn_j2_car
                    j3_car += addn_j3_car
                    j4_car += addn_j4_car

                    # print out the remaining cars at each entrance to the junction, after new cars have entered
                    # print also which entrance is green
                    # print also what each of the timer values are                                
                    print(f"After new cars have entered, if any:")
                    print(j1_car, j2_car, j3_car, j4_car)
                    print(f"green light is at {p4traffic.Green_Light}")
                    print(f"junction timer is {p4traffic.Junction_Timer}")
                    print(f"consecutive timer is {p4traffic.Consecutive_Timer}")
                    # print "end of loop" and a newline to make the CLI output easier to read
                    print(f"end of loop")
                    print("\n")
                    time.sleep(SLEEP_TIME) # additional sleep to help read the CLI output
                else:
                    print("cannot find P4Traffic header in the packet")
    	        
            else:
                print("Didn't receive response")
                sys.exit(3)
        except Exception as error:
            print(error)
            sys.exit(4)
    	
if __name__ == '__main__':
    main()
