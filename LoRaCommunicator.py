#!/usr/bin/env python3
"""
This program is used to listen to the LoRa transmissions

It is intended to be used as part of the LoRa Monitor, but it can be run independently.
"""


import logging
import time
import math
import sys
import wiringpi

#TODO: Need to return the values, not just print them.
#TODO: Consider putting this within a class

def SetupUART():
    """
    Setup the UART for communications and return an object referencing it. Does:-
    -Initiates wiringpi software
    -Opens the serial port
    -Checks all is ok and returns the object
    """
    
    response = wiringpi.wiringPiSetup()
    # open the serial port and set the speed accordingly
    sp = wiringpi.serialOpen('/dev/ttyAMA0', 9600)

    # clear the serial buffer of any left over data
    wiringpi.serialFlush(sp)
    
    if response == 0 and sp >0:
        # if wiringpi is setup and the opened channel is greater than zero (zero = fail)
        logging.info ("PI setup complete on channel %d" %sp)
    else:
        logging.critical("Unable to Setup communications")
        sys.exit()
        
    return sp

def ReadData(fd):
    # read the data back from the serial line and return it as a string to the calling function
    qtydata = wiringpi.serialDataAvail(fd)
    logging.info("Amount of data: %d bytes" % qtydata)
    response = []
    while qtydata > 0:
        # while there is data to be read, read it back
        logging.debug("Reading data back byte:%d" % qtydata)
        # This used to have hex to convert the data to a hex string
        response.append(wiringpi.serialGetchar(fd))
        qtydata = qtydata - 1
    logging.info("Data Packet received: %s" % response)
    logging.debug("Size of data packet received %d" % len(response))
    return response

def ReadChar(fd):
    # read a single character back from the serial line
    qtydata = wiringpi.serialDataAvail(fd)
    logging.info("Amount of data: %s bytes" % qtydata)
    response = 0
    if qtydata > 0:
        logging.debug("Reading data back %d" % qtydata)
        response = wiringpi.serialGetchar(fd)
    return response

    
def SetupLoRa(fd):
    # send the right commands to setup the LoRa module
    logging.info("Setting up the LoRA module with the various commands")
    # The commands are not yet known, so this is to be added
    logging.warning("No LoRa commands setup")
    #wiringpi.serialPutchar(fd, 0x46)
    time.sleep(0.1)
    logging.debug("LoRa module commands sent")
    return
    
def Setup():
    """
    Sets up the comms and returns the object that is the connection.
    """
    sp = SetupUART()
    SetupLoRa(sp)
    return sp

def main():
    """
    This is the main entry point for the program when it is being run independently.
    
    """
    sp = SetupUART()
    SetupLoRa(sp)
    while(True):
        print("Data Received:%s" % ReadChar(sp))
    

    
# Only call the independent routine if the module is being called directly, else it is handled by the calling program
if __name__ == "__main__":

    main()
