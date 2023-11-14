"""

Created 2021/05

Author:                     Jahns_P
Version Number:             1
Date of last change:        2021/05/28
Requires:                   R&S ZNB, FW 3.12 or newer and adequate options
                            Installed VISA e.g. R&S Visa 5.12.x or newer

Description:    Example for remote calibration with robot support to feed the calibration elements.


General Information:

Please always check this example script for unsuitable setting that may
destroy your DUT before connecting it to the instrument!
This example does not claim to be complete. All information has been
compiled with care. However errors can not be ruled out. 
"""

# --> Import necessary packets  
from RsInstrument import *
from time import sleep

# Define variables
resource = 'TCPIP::10.205.0.51::hislip0'  # VISA resource string for the device

# Define the device handle
# Instrument = RsInstrument(resource)
Instrument = RsInstrument(resource, True, True, "SelectVisa='rs'")
'''
(resource, True, True, "SelectVisa='rs'") has the following meaning:
(VISA-resource, id_query, reset, options)
- id_query: if True: the instrument's model name is verified against the models 
supported by the driver and eventually throws an exception.   
- reset: Resets the instrument (sends *RST) command and clears its status syb-system
- option SelectVisa:
    - 'SelectVisa = 'socket' - uses no VISA implementation for socket connections - you do not need any VISA-C installation
    - 'SelectVisa = 'rs' - forces usage of Rohde&Schwarz Visa
    - 'SelectVisa = 'ni' - forces usage of National Instruments Visa     
'''
sleep(1)  # Eventually add some waiting time when reset is performed during initialization


def comprep():
    """Preparation of the communication (termination, etc...)"""

    print(f'VISA Manufacturer: {Instrument.visa_manufacturer}')  # Confirm VISA package to be choosen
    Instrument.visa_timeout = 5000  # Timeout for VISA Read Operations
    Instrument.opc_timeout = 5000  # Timeout for opc-synchronised operations
    Instrument.instrument_status_checking = True  # Error check after each command, can be True or False
    Instrument.clear_status()  # Clear status register


def close():
    """Close the VISA session"""

    Instrument.close()


def comcheck():
    """Check communication with the device"""

    # Just knock on the door to see if instrument is present
    idnResponse = Instrument.query_str('*IDN?')
    sleep(1)
    print('Hello, I am ' + idnResponse)


def meassetup():
    """Prepare measurement setup and define calkit"""
    # RF Setup first
    Instrument.write_str_with_opc('SYSTEM:DISPLAY:UPDATE ON')  # Be sure to have the display updated whilst remote control
    Instrument.write_str_with_opc('SENSe1:FREQuency:Start 1e9')  # Set start frequency to 1 GHz
    Instrument.write_str_with_opc('SENSe1:FREQuency:Stop 2e9')  # Set stop frequency to 2 GHz
    Instrument.write_str_with_opc('SENSe1:SWEep:POINts 501')  # Set number of sweep points
    Instrument.write_str_with_opc('CALCulate1:PARameter:MEAsure "Trc1", "S11"')  # Change active trace to S11 measurement
    # Calibration preparation setup follows
    Instrument.write_str_with_opc('SENSe1:CORRection:CKIT:PC292:SELect "ZN-Z229"')  # Select cal kit
    Instrument.write_str_with_opc('SENSe1:CORRection:COLLect:CONN PC292MALE')  # Define gender of the port
    Instrument.write_str_with_opc('SENSe1:CORRection:COLLect:METHod:DEFine "NewCal", FOPort, 1')  # Choose OSM cal type
    Instrument.write_str_with_opc('SENSe:CORRection:COLLect:ACQuire:RSAVe:DEFault OFF')  # Avoid to save the data to your default calibration


def calopen():
    """Perform calibration of open element"""
    print()
    print('Please connect OPEN to port 1 and confirm')
    _ = input()
    Instrument.write_str_with_opc('SENSe1:CORRection:COLLect:ACQuire:SELected OPEN, 1')


def calshort():
    """Perform calibration with short element"""
    print('Please connect SHORT to port 1 and confirm')
    _ = input()
    Instrument.write_str_with_opc('SENSe1:CORRection:COLLect:ACQuire:SELected SHORT, 1')


def calmatch():
    """Perform calibration with matched element"""
    print('Please connect MATCH to port 1 and confirm')
    _ = input()
    Instrument.write_str_with_opc('SENSe1:CORRection:COLLect:ACQuire:SELected MATCH, 1')


def applycal():
    """Apply calibration after it is finished and save the calfile"""
    sleep(2)
    Instrument.write_str_with_opc('SENSe1:CORRection:COLLect:SAVE:SELected')
    #Instrument.write_str_with_opc('MMEMORY:STORE:CORRection 1, "NEWCAL.cal"')
    #Instrument.write_str_with_opc('MMEMORY:LOAD:CORRection 1, "NEWCAL.cal"')


def savecal():
    """Save the calibration file to the pool"""
    print('Now saving the calibration to the pool')
    Instrument.write('MMEMory:STORE:CORRection 1,"P1_OSM_1-2GHz"')


def loadprep():
    """Reset the instrument, add two channels and load calibration file to each channel"""
    print()
    print('Resetting the instrument, assign three channels with adequate settings')
    Instrument.write_str_with_opc('*RST')  # Perform a reset
    #
    # Prepare CH1 and trace 1 (CH, window and trace already existing as it is the 1st one)
    #
    # Using the complete command including "SENSe" will define the channel the changes will be associated to
    Instrument.write_str_with_opc('SENSe1:FREQuency:Start 1e9')  # Set start frequency to 1 GHz
    Instrument.write_str_with_opc('SENSe1:FREQuency:Stop 2e9')  # Set stop frequency to 2 GHz
    Instrument.write_str_with_opc('SENSe1:SWEep:POINts 501')  # Set number of sweep points

    #
    # Prepare CH2 and trace 2
    #
    # Using the complete command including "SENSe" will define the channel the changes will be associated to
    Instrument.write_str_with_opc("CALCULATE2:PARAMETER:SDEFINE 'Trc2', 'S11'")
    Instrument.write_str_with_opc("CALCULATE2:PARAMETER:SELECT 'Trc2'")
    Instrument.write_str_with_opc("DISPLAY:WINDOW2:STATE ON")
    Instrument.write_str_with_opc("DISPLAY:WINDOW2:TRACE1:FEED 'Trc2'")
    Instrument.write_str_with_opc('SENSe2:FREQuency:Start 1e9')  # Set start frequency to 1 GHz
    Instrument.write_str_with_opc('SENSe2:FREQuency:Stop 2e9')  # Set stop frequency to 2 GHz
    Instrument.write_str_with_opc('SENSe2:SWEep:POINts 501')  # Set number of sweep points
    #
    # Prepare CH3 and trace 3
    #
    # Using the complete command including "SENSe" will define the channel the changes will be associated to
    Instrument.write_str_with_opc("CALCULATE3:PARAMETER:SDEFINE 'Trc3', 'S11'")
    Instrument.write_str_with_opc("CALCULATE3:PARAMETER:SELECT 'Trc3'")
    Instrument.write_str_with_opc("DISPLAY:WINDOW3:STATE ON")
    Instrument.write_str_with_opc("DISPLAY:WINDOW3:TRACE1:FEED 'Trc3'")
    Instrument.write_str_with_opc('SENSe3:FREQuency:Start 1e9')  # Set start frequency to 1 GHz
    Instrument.write_str_with_opc('SENSe3:FREQuency:Stop 2e9')  # Set stop frequency to 2 GHz
    Instrument.write_str_with_opc('SENSe3:SWEep:POINts 501')  # Set number of sweep points


def loadcal():
    """Now load the cal file to each channel"""
    print()
    print('Load the calibration to all three channels')
    Instrument.write('MMEMory:LOAD:CORRection 1,"P1_OSM_1-2GHz"')
    Instrument.write('MMEMory:LOAD:CORRection 2,"P1_OSM_1-2GHz"')
    Instrument.write('MMEMory:LOAD:CORRection 3,"P1_OSM_1-2GHz"')
    # Instrument.write_str('SENSe1:CORRection:DELete')    # Command to remove the user calibration from CH1 if desired for RF debugging purposes

#
# ---------------------------
# Main Program begins here
# just calling the functions
# ---------------------------
#

comprep()
comcheck()
meassetup()
calopen()
calshort()
calmatch()
applycal()
savecal()
loadprep()
loadcal()
close()

print()
print("I'm done")
