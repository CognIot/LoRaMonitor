#!/usr/bin/env python3
"""
A test program to generate UART packages that reflect the LoRa transmissions.
These are sent out over the transmit line, with a wire loop so they can be received.

It is intended to be run for testing and development

"""

#TODO: to be checked to see if required
#TODO: Need to add logging throughout for debugging

import logging
import time
import math
import sys
import wiringpi
import random

#TODO: Have more levels of logging so I don't generate too much data

# fixed addresses
# The METER is the water capturing devices, this is a list to simulate multiple meters 
METER = [[0x00, 0x11, 0x11,0x11,0x11], [0x00,0x22,0x22,0x22,0x22]]
CONCENTRATOR = [0x00,0xFE,0xFE,0xFE,0xFE]
NEWASSMETER = [0x00,0x00,0x00,0x00,0xEE]


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

def GetPayload():
    """
    Returns a defined payload
    """
    payload_length = 27
    load = []
    load = [0x80]
    for f in range(1, payload_length):
        load.insert(f, random.randint(0x00, 0xff))
    logging.debug("Random Payload Generated of %x bytes:%s" % (payload_length,load))
    return load

def GenerateAssociationRequest():
    """
    Function generates an Association Request packet of data and puts it into a list for use.
    """
    packet_to_send = []
    # Receiver address
    packet_to_send = packet_to_send + NEWASSMETER
    # Sender address
    packet_to_send = packet_to_send + CONCENTRATOR
    # Command
    packet_to_send.append(0x30)
    logging.info("Association Request message:%s" % packet_to_send)
    return packet_to_send

def GenerateAssociationConfirmation(meter):
    """
    Function generates an Association Confirmation response packet of data and puts it into a list for use.
    """
    packet_to_send = []
    # Receiver address
    packet_to_send = packet_to_send + CONCENTRATOR
    # Sender address
    packet_to_send = packet_to_send + meter
    # Command
    packet_to_send.append(0x31)
    # Response Code
    packet_to_send.append(0x00)
    logging.info("Association Confirmation message:%s" % packet_to_send)
    return packet_to_send

def GenerateD2SRequestReadyToSend(meter):
    """
    Function generates an Data To Send Request Ready To Send packet of data and puts it into a list for use.
    """
    packet_to_send = []
    # Receiver address
    packet_to_send = packet_to_send + meter
    # Sender address
    packet_to_send = packet_to_send + (CONCENTRATOR)
    # Command
    packet_to_send.append(0x34)
    logging.info("Data To Send Ready To Send message:%s" % packet_to_send)
    return packet_to_send

def GenerateD2SClearToSendData(meter):
    """
    Function generates an Clear to Send Data response packet of data and puts it into a list for use.
    """
    packet_to_send = []
    # Receiver address
    packet_to_send = packet_to_send + (CONCENTRATOR)
    # Sender address
    packet_to_send = packet_to_send + meter
    # Command
    packet_to_send.append(0x35)
    # Response Code
    packet_to_send.append(0x00)
    logging.info("Data To Send Clear To Send Data message:%s" % packet_to_send)
    return packet_to_send

def GenerateSendData(meter):
    """
    Function generates an Data To Send Request Ready To Send packet of data and puts it into a list for use.
    """
    packet_to_send = []
    payload = []
    # Receiver address
    packet_to_send = packet_to_send + meter
    # Sender address
    packet_to_send = packet_to_send + (CONCENTRATOR)
    # Command
    packet_to_send.append(0x36)
    # Payload
    payload = GetPayload()
    for items in payload:
        packet_to_send.append(items)
    # Length of payload
    packet_to_send.append(len(payload))
    logging.info("Send Data message:%s" % packet_to_send)
    return packet_to_send

def GenerateSendDataResponse(meter):
    """
    Function generates an Send Data response packet of data and puts it into a list for use.
    """
    packet_to_send = []
    # Receiver address
    packet_to_send = packet_to_send + (CONCENTRATOR)
    # Sender address
    packet_to_send = packet_to_send + meter
    # Command
    packet_to_send.append(0x35)
    # Response Code
    packet_to_send.append(0x00)
    logging.info("Send Data response message:%s" % packet_to_send)
    return packet_to_send

def TransmitData(channel,payload):
    """
    Given the payload, transmit it over the UART line
    """
    logging.info('Data to be sent to the serial port %s' % payload)
    for items in payload:
        logging.debug('Data packet to be sent >%x< on channel:%x' %(items, channel))
        wiringpi.serialPutchar(channel, items)
    
    return



def main():
    """
    This is the main entry point for the program when it is being run independently.
    
    The program sends a valid data packet, similar to what is expected from the LoRa moudles
    
    """
    logging.basicConfig(filename="LoRaReplicator.txt", filemode="w", level=logging.WARNING, format='%(asctime)s:%(levelname)s:%(message)s')

    port = SetupUART()

    while(True):
        data = []
        # Choose meter
        meter_no = random.randint(0, len(METER)-1)
        meter = METER[meter_no]
        logging.info("This meter is being used:%s" % meter)
        
        # Association
        data = GenerateAssociationRequest()
        TransmitData(port,data)

        data = GenerateAssociationConfirmation(meter)
        TransmitData(port,data)
        
        #generate packet
        data = GenerateD2SRequestReadyToSend(meter)
        TransmitData(port, data)
        data = GenerateD2SClearToSendData(meter)
        TransmitData(port, data)
        data = GenerateSendData(meter)
        TransmitData(port, data)
        data = GenerateSendDataResponse(meter)
        TransmitData(port, data)
        print(".", end="")
    
    
# Only call the independent routine if the module is being called directly, else it is handled by the calling program
if __name__ == "__main__":

    main()
