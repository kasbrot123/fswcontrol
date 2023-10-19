# -*- coding: utf-8 -*-
"""
Script: "3d_visualization.py"

Author(s): Michael Toefferl
Created: 2023-10-19 12:35


Class to control the Rohde & Schwarz FSW spectrum analyzer via python commands.




"""


import os
import datetime
from RsInstrument import RsInstrument, BinFloatFormat


class FSW:

    def __init__(self):

        self.ip = '192.168.0.61'
        self.path = '.'
        self.f_center = None
        self.f_span = None
        self.N_points = None


    def init(self):

        RsInstrument.assert_minimum_version('1.53.0')
        try:
            # Adjust the VISA Resource string to fit your instrument
            instr = RsInstrument('TCPIP::' + self.ip + '', id_query=True, reset=False)
            instr.visa_timeout = 10000  # Timeout for VISA Read Operations
            instr.opc_timeout = 10000  # Timeout for opc-synchronised operations
            instr.instrument_status_checking = True  # Error check after each command
        except Exception as ex:
            print('Error initializing the instrument session:\n' + ex.args[0])
            return

        self.instr = instr

        idn = self.instr.query_str('*IDN?')
        print('Hello, I am: ' + idn)

        self.debug(True)
        self.continuous_sweep(False)
        self.get_parameter()

    def get_parameter(self):

        # functionality not tested
        f_center = self.instr.write_str('FREQ:CENT?')
        f_span = self.instr.write_str('FREQ:SPAN?')
        N_points = self.instr.write_str('SWE:POIN?')
        
        print(f_center, type(f_center))
        print(f_span, type(f_center))
        print(N_points, type(f_center))

        # self.f_center = f_center
        # self.f_span = f_center
        # self.N_points = f_center



    def debug(self, debug_mode=True):
        if debug_mode:
            self.instr.write_str('SYST:DISP:UPD ON')  # Display update ON - switch OFF after debugging
            print('debug mode on')
        else:
            self.instr.write_str('SYST:DISP:UPD OFF')  # Display update ON - switch OFF after debugging
            print('debug mode off')


    def continuous_sweep(self, cont_mode=True):
        if cont_mode:
            self.instr.write_str('INIT:CONT ON')  # Switch OFF the continuous sweep
            print('continuous sweep on')
        else:
            self.instr.write_str('INIT:CONT OFF')  # Switch OFF the continuous sweep
            print('continuous sweep off')

    def basic_config(self):
        self.instr.write_str('DISP:WIND:TRAC:Y:RLEV 10.0')  # Setting the Reference Level
        self.instr.write_str('FREQ:CENT 3.0 GHz')  # Setting the center frequency
        self.instr.write_str('FREQ:SPAN 200 MHz')  # Setting the span
        self.instr.write_str('BAND 100 kHz')  # Setting the RBW
        self.instr.write_str('BAND:VID 300kHz')  # Setting the VBW
        self.instr.write_str('SWE:POIN 10001')  # Setting the sweep points
        answer = self.instr.query_opc()  # Using *OPC? query waits until all the instrument settings are finished

        # maybe better try-catch
        if answer:
            print('settings applied')
        else:
            print('settings were not applied correctly')

        self.get_parameter()


    def set_path(self, path='.'):
        path = path.replace('\\', '/').replace('/', os.sep)
        if os.path.isdir(path):
            self.path = path
            print("Set path to '{}'".format(self.path))
            return True
        else:
            print("Path '{}' does not exist.".format(path))
            return False


    def measure(self, name=''):

        if name == '':
            name = datetime.datetime.now().strftime('FSW_%Y_%m_%d_%H-%M-%S.txt')
            # if measurement is really fast, append milliseconds
            # name = datetime.datetime.now().strftime('FSW_%Y_%m_%d_%H-%M-%S_%f.txt')

        # consistant file ending
        if not name.endswith('.txt'):
            name += '.txt'

        self.instr.write_str_with_opc('INIT')  # Start the sweep and wait for it to finish

        trace = self.instr.query_bin_or_ascii_float_list('FORM ASC;:TRAC? TRACE1')  # Query ascii array of floats
        marker_x, marker_y = self.marker_xy()


        date_time = datetime.datetime.now().strftime('%d.%m.%Y, %H:%M:%S')

        # for generating test files 
        # # x = np.linspace(-4, 4, 100)
        # # trace = 10*np.exp(-x**2)
        # split = name.replace('.txt','').split('_')
        # az = float(split[-2])
        # el = float(split[-1])
        # trace = np.ones(100)*np.cos(az*np.pi/180)*np.cos(el*np.pi/180)
        # # x = np.linspace(-4, 4, 100)
        # # trace = 10*np.exp(-x**2)
        # marker_x, marker_y = 10, 10


        f_path = self.path + os.sep + name
        file = open(f_path, 'w')
        file.write('# FSW Measurement\n')
        file.write('# File name: {}\n'.format(name))
        file.write('# Date: {}\n'.format(date_time))
        file.write('# Frequency Center: {}\n'.format(self.f_center))
        file.write('# Frequency Span: {}\n'.format(self.f_span))
        file.write('# Number Points: {}\n'.format(self.N_points))
        file.write('# Max Marker X: {}\n'.format(marker_x))
        file.write('# Max Marker Y: {}\n'.format(marker_y))
        file.write('# Values of trace\n'.format(marker_y))
        
        for value in trace:
            file.write('{}\n'.format(value))


        return


        # binary format, maybe this is useful too

        # instr.bin_float_numbers_format = BinFloatFormat.Single_4bytes  # This tells the driver in which format to expect the binary float data
        # trace = instr.query_bin_or_ascii_float_list('FORM REAL,32;:TRAC? TRACE1')  # Query binary array of floats - the query function is the same as for the ASCII format
        # # print(f'Instrument returned {len(trace)} points in the binary trace, query duration {time() - t:.3f} secs')


        
    def marker_xy(self):

        # Set the marker to the maximum point of the entire trace, wait for it to be set
        self.instr.write_str_with_opc('CALC1:MARK1:MAX')  
        markerX = self.instr.query_float('CALC1:MARK1:X?')
        markerY = self.instr.query_float('CALC1:MARK1:Y?')

        return markerX, markerY


    def screenshot(self):
        print("method 'screenshot' not implemented")

        # # -----------------------------------------------------------
        # # Making an instrument screenshot and transferring the file to the PC
        # # -----------------------------------------------------------
        # instr.write_str("HCOP:DEV:LANG PNG")
        # instr.write_str(r"MMEM:NAME 'c:\temp\Dev_Screenshot.png'")
        # instr.write_str("HCOP:IMM")  # Make the screenshot now
        # instr.query_opc()  # Wait for the screenshot to be saved
        # instr.read_file_from_instrument_to_pc(r"c:\temp\Dev_Screenshot.png", r"c:\Temp\PC_Screenshot.png")  # Transfer the instrument file to the PC
        # print(r"Instrument screenshot file saved to PC 'c:\Temp\PC_Screenshot.png'")


    def close(self):
        # reset maybe not so good if you want to reconnect or see the settings
        # but I keep it as an option
        # self.instr.reset() 

        self.instr.close()
        print('connection closed')
        print('reconnect with self.init()')


import numpy as np

# for testing
if __name__ == '__main__':

    fsw = FSW()
    fsw.set_path('./data')
    fsw.ip = '192.168.0.61'
    fsw.init()
    fsw.basic_config()
    fsw.measure()
    mx, my = fsw.marker_xy()
    print('Max Marker at {mx} GHz with {my} dB')

    # for az in np.arange(-100, 100, 10):
    #     for el in np.arange(-100, 100, 10):
    #         fsw.measure('testing_{}_{}.txt'.format(az, el))






# ip = '192.168.0.61'
#
# instr = RS.RsInstrument('TCPIP::{}'.format(ip), id_query=True, reset=True)
# idn = instr.query_str('*IDN?')
# print('Hello, I am: ' + idn)
#
#
# # instr.close()
#
# ###############################################################################
#
# instr.clear_status()
# instr.reset()
# instr.write_str('INIT:CONT OFF')  # Switch OFF the continuous sweep
# instr.write_str('SYST:DISP:UPD ON')  # Display update ON - switch OFF after debugging
#
#
#
# # # -----------------------------------------------------------
# # # Basic Settings:
# # # -----------------------------------------------------------
# instr.write_str('DISP:WIND:TRAC:Y:RLEV 10.0')  # Setting the Reference Level
# instr.write_str('FREQ:CENT 3.0 GHz')  # Setting the center frequency
# instr.write_str('FREQ:SPAN 200 MHz')  # Setting the span
# instr.write_str('BAND 100 kHz')  # Setting the RBW
# instr.write_str('BAND:VID 300kHz')  # Setting the VBW
# instr.write_str('SWE:POIN 10001')  # Setting the sweep points
# instr.query_opc()  # Using *OPC? query waits until all the instrument settings are finished
#
#
#
#
#
#
# # -----------------------------------------------------------
# # SyncPoint 'SettingsApplied' - all the settings were applied
# # -----------------------------------------------------------
# instr.VisaTimeout = 2000  # Sweep timeout - set it higher than the instrument acquisition time
# instr.write_str_with_opc('INIT')  # Start the sweep and wait for it to finish
# # -----------------------------------------------------------
# # SyncPoint 'AcquisitionFinished' - the results are ready
# # -----------------------------------------------------------
# # Fetching the trace
# # The functions are universal for binary or ascii data format
# # -----------------------------------------------------------
# t = time()
# trace = instr.query_bin_or_ascii_float_list('FORM ASC;:TRAC? TRACE1')  # Query ascii array of floats
# print(f'Instrument returned {len(trace)} points in the ascii trace, query duration {time() - t:.3f} secs')
# t = time()
# instr.bin_float_numbers_format = BinFloatFormat.Single_4bytes  # This tells the driver in which format to expect the binary float data
# trace = instr.query_bin_or_ascii_float_list('FORM REAL,32;:TRAC? TRACE1')  # Query binary array of floats - the query function is the same as for the ASCII format
# print(f'Instrument returned {len(trace)} points in the binary trace, query duration {time() - t:.3f} secs')
#
#
#
#
# # -----------------------------------------------------------
# # Setting the marker to max and querying the X and Y
# # -----------------------------------------------------------
# instr.write_str_with_opc('CALC1:MARK1:MAX')  # Set the marker to the maximum point of the entire trace, wait for it to be set
# markerX = instr.query_float('CALC1:MARK1:X?')
# markerY = instr.query_float('CALC1:MARK1:Y?')
# print(f'Marker Frequency {markerX:.2f} Hz, Level {markerY:.3f} dBm')
#
#
#
#




