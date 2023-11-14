import RsInstrument as RS


"""

FSW_Example.py
    basic commands

HelloWorld_Example.py
    connection types (TCPIP, GPIB, USB, RSNRP, etc.)




"""



ip = '192.168.0.61'

instr = RS.RsInstrument('TCPIP::{}'.format(ip), id_query=True, reset=True)
idn = instr.query_str('*IDN?')
print('Hello, I am: ' + idn)


# instr.close()

###############################################################################

instr.clear_status()
instr.reset()
instr.write_str('INIT:CONT OFF')  # Switch OFF the continuous sweep
instr.write_str('SYST:DISP:UPD ON')  # Display update ON - switch OFF after debugging



# # -----------------------------------------------------------
# # Basic Settings:
# # -----------------------------------------------------------
instr.write_str('DISP:WIND:TRAC:Y:RLEV 10.0')  # Setting the Reference Level
instr.write_str('FREQ:CENT 3.0 GHz')  # Setting the center frequency
instr.write_str('FREQ:SPAN 200 MHz')  # Setting the span
instr.write_str('BAND 100 kHz')  # Setting the RBW
instr.write_str('BAND:VID 300kHz')  # Setting the VBW
instr.write_str('SWE:POIN 10001')  # Setting the sweep points
instr.query_opc()  # Using *OPC? query waits until all the instrument settings are finished






# -----------------------------------------------------------
# SyncPoint 'SettingsApplied' - all the settings were applied
# -----------------------------------------------------------
instr.VisaTimeout = 2000  # Sweep timeout - set it higher than the instrument acquisition time
instr.write_str_with_opc('INIT')  # Start the sweep and wait for it to finish
# -----------------------------------------------------------
# SyncPoint 'AcquisitionFinished' - the results are ready
# -----------------------------------------------------------
# Fetching the trace
# The functions are universal for binary or ascii data format
# -----------------------------------------------------------
t = time()
trace = instr.query_bin_or_ascii_float_list('FORM ASC;:TRAC? TRACE1')  # Query ascii array of floats
print(f'Instrument returned {len(trace)} points in the ascii trace, query duration {time() - t:.3f} secs')
t = time()
instr.bin_float_numbers_format = BinFloatFormat.Single_4bytes  # This tells the driver in which format to expect the binary float data
trace = instr.query_bin_or_ascii_float_list('FORM REAL,32;:TRAC? TRACE1')  # Query binary array of floats - the query function is the same as for the ASCII format
print(f'Instrument returned {len(trace)} points in the binary trace, query duration {time() - t:.3f} secs')




# -----------------------------------------------------------
# Setting the marker to max and querying the X and Y
# -----------------------------------------------------------
instr.write_str_with_opc('CALC1:MARK1:MAX')  # Set the marker to the maximum point of the entire trace, wait for it to be set
markerX = instr.query_float('CALC1:MARK1:X?')
markerY = instr.query_float('CALC1:MARK1:Y?')
print(f'Marker Frequency {markerX:.2f} Hz, Level {markerY:.3f} dBm')



# -----------------------------------------------------------
# Making an instrument screenshot and transferring the file to the PC
# -----------------------------------------------------------
instr.write_str("HCOP:DEV:LANG PNG")
instr.write_str(r"MMEM:NAME 'c:\temp\Dev_Screenshot.png'")
instr.write_str("HCOP:IMM")  # Make the screenshot now
instr.query_opc()  # Wait for the screenshot to be saved
instr.read_file_from_instrument_to_pc(r"c:\temp\Dev_Screenshot.png", r"c:\Temp\PC_Screenshot.png")  # Transfer the instrument file to the PC
print(r"Instrument screenshot file saved to PC 'c:\Temp\PC_Screenshot.png'")





