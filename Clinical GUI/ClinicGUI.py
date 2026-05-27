import serial
import time
import os
import copy
import argparse
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import timeit
import math
from datetime import datetime
from multiprocessing import Process
import keyboard
import FreeSimpleGUI as sg

# Setup state variables:
currentState = "Not Running"
timersRunning = False

# Setup recording variables:
interRecordingInterval = 60*5 - 30     # seconds
recordingInterval = 30           # seconds
preStimDuration = 1800-1         # seconds
randStimDuration = 3600-1        # seconds
fixedStimDuration = 3600-1       # seconds

# Fill this out! INITALS + DATE
PatientName = 'p0_date'
# What port is the arduino on?
ACOM = 'COM7'

now = datetime.now()
current_time = copy.deepcopy(now.strftime("m%m_d%d_y%Y_h%H_m%M"))
print(current_time)

patientDirectory = PatientName+"_"+current_time+"/"
print(current_time)


# define a function to stream arduino serial output to a file:
def ReadArduinoOut(current_time):
    global patientDirectory
    # Connect to the arduino serial. This will also reset it.
    Arduino = serial.Serial(ACOM,9600)

    # Setup a datafile for Arduino events:
    print("Dir:")
    print(patientDirectory)
    text_file = open(patientDirectory+current_time+"_extractedArduinoData.text", "w")

    # Record session start to the file
    data = "SESSION STARTED\n"
    text_file.write(current_time + "-->" + data)

    # Create the exit file killer variable
    file_operation = True
    
    # Setup interval checker
    time_landmark = datetime.now()
    
    # Create the exit file (process killer)
    exit_file = current_time+"_DELETE_TO_END_SESSION.txt"
    exit_file_object = open(exit_file, "w")
    exit_file_object.close() 

    
    # Enter an infinite While loop
    while file_operation:
        # check elapsed time:
        current_landmark = datetime.now()
        
        # Read from the arduino serial
        data = str(Arduino.readline())   #read the data
        
        print(data)
        
        # If the data is valid, record it.
        if len(data) > 10:
            current_time = current_landmark.strftime("m%m_d%d_y%Y_h%H_m%M_s%S_us%f")
            text_file.write(current_time + "---" + data.rstrip('\n'))
        
        # peridoically check if we need to bail out of the process
        elapsed_time = current_landmark - time_landmark
        if elapsed_time.seconds >= 1:
            time_landmark = current_landmark
            if not os.path.isfile(exit_file):
                file_operation = False
                
        # If so, finalize the file
        if not file_operation:
            print('Arduino Process Interrupted, Closing File.')
            current_landmark = datetime.now()
            current_time = current_landmark.strftime("m%m_d%d_y%Y_h%H_m%M_s%S")
            data = "SESSION CLOSED\n"
            text_file.write(current_time + "-->" + data)
            text_file.close()   

# define a function to stream user events to a file:
def ReadUserEvents(current_time):
    global currentState
    global timersRunning
    # Setup a datafile
    text_file = open(patientDirectory+current_time+"_extractedUserData.text", "w")

    # Start file
    data = "SESSION STARTED\n"
    text_file.write(current_time + "-->" + data)
    exit_file = current_time+"_DELETE_TO_END_SESSION.txt"

    # Create the exit file killer variable
    file_operation = True
    
    # Setup interval checker
    time_landmark = datetime.now()
    init_landmark = datetime.now() 
    # Create the exit file (process killer)
    exit_file = current_time+"_DELETE_TO_END_SESSION.txt"
    exit_file_object = open(exit_file, "w")
    exit_file_object.close() 
    
    ct = current_time;

    next_rec_timer = 60*5 - 30
    held_lm_start = datetime.now()
    
    stop_rec_timer = -1
    held_lm_end = datetime.now()
    
    total_rec_timer = 3599
    held_rec_start = datetime.now()
    
    recording = False;
    running_m = 0
    running_s = 0
    running_ms = 0
    # Enter an infinite While loop
    while file_operation:
        current_landmark = datetime.now()
        current_time = current_landmark.strftime("m%m_d%d_y%Y_h%H_m%M_s%S_us%f")
        
        event, values = window.read(timeout=5)
        
        if timersRunning:
            delt = (current_landmark -held_lm_start)
            temp = str(100-int(delt.microseconds/10000))
            if len(temp) < 2:
                temp = "0" + temp
            ustr = str(next_rec_timer-delt.seconds) + ":" + temp[0:2]
            
            if ustr[0] == "-":
                ustr = "----"
            window['text1'].update(ustr)
                
            delt = (current_landmark -held_lm_end)
            temp = str(100-int(delt.microseconds/10000))
            if len(temp) < 2:
                temp = "0" + temp
            ustr = str(stop_rec_timer-delt.seconds) + ":" + temp[0:2]
            
            if ustr[0] == "-":
                ustr = "----"
            window['text2'].update(ustr)
    
            delt = (current_landmark - held_rec_start)
            temp = str(100-int(delt.microseconds/10000))
            if len(temp) < 2:
                temp = "0" + temp
            ustr = str(total_rec_timer-delt.seconds) + ":" + temp[0:2]
            if ustr[0] == "-":
                ustr = "----"
            window['text3'].update(ustr)
        
        if values['session_dropdown'] != currentState:
            if values['sessionlock'] == True:
                values['session_dropdown'] = currentState
                window['session_dropdown'].update(currentState)
                print("Session type is locked. Changes were not implemented.")
            else:
                timersRunning = False
                ustr = "----"
                window['text1'].update(ustr)
                window['text2'].update(ustr)
                window['text3'].update(ustr)
                window['text4'].update(ustr)
                currentState = values['session_dropdown']
                print("Session type was changed to",currentState,"... starting a new session file.")
                
                
        
        
        temp_s = str(running_s)
        if len(temp_s) < 2:
            temp_s = "0" + temp_s
        temp = str(running_ms)
        if len(temp) < 2:
            temp = "0" + temp
        window['text4'].update(str(running_m) + ":" + temp_s + ":" + temp[0:2])
        
        # End program if user closes window or
        # presses the OK button
        if event == "Exit GUI" or event == sg.WIN_CLOSED:
            file_operation = False
            
        if event == "Start Stimulus":
            print("Recording the onset of stimulus.")
            text_file.write(current_time + "---" + 'Stimulus START.\n')  
            if values['session_dropdown'] == "Pre-Stimulus":
                total_rec_timer = preStimDuration
                text_file.write(current_time + "---" + 'Pre-Stimulus experiment START.\n')   
            if values['session_dropdown'] == "Random Stimulus":
                total_rec_timer = randStimDuration            
                text_file.write(current_time + "---" + 'Random Stimulus experiment START.\n')                   
            if values['session_dropdown'] == "Fixed Stimulus":
                total_rec_timer = fixedStimDuration
                text_file.write(current_time + "---" + 'Fixed Stimulus experiment START.\n')   
            held_rec_start = datetime.now()
            timersRunning = True
            
        if event == "End Stimulus":
            print("Recording the end of stimulus.")
            text_file.write(current_time + "---" + 'Stimulus END.\n')   
            held_rec_start = datetime.now()
            total_rec_timer = -1
            timersRunning = False
            if values['session_dropdown'] == "Pre-Stimulus":
                text_file.write(current_time + "---" + 'Pre-Stimulus experiment END.\n')   
            if values['session_dropdown'] == "Random Stimulus":        
                text_file.write(current_time + "---" + 'Random Stimulus experiment END.\n')                   
            if values['session_dropdown'] == "Fixed Stimulus":
                text_file.write(current_time + "---" + 'Fixed Stimulus experiment END.\n')   
            
        if event == "Start Recording":
            print("Recording the start of the DBS recording.")
            text_file.write(current_time + "---" + 'Recording START.\n')  
            stop_rec_timer = 29
            next_rec_timer = -1
            held_lm_end = datetime.now()
            recording = True;
            
        if event == "End Recording":
            print("Recording the end of the DBS recording.")
            text_file.write(current_time + "---" + 'Recording END.\n')
            stop_rec_timer = -1
            next_rec_timer = 60*5 - 30
            held_lm_start = datetime.now()
            recording = False;
            running_ms = running_ms + (current_landmark - held_lm_end).microseconds/1000
            while running_ms > 1000:
                running_ms -= 1000
                running_s += 1
            running_s = running_s + (current_landmark - held_lm_end).seconds
            while running_s > 60:
                running_s -= 60
                running_m += 1
        if event == "Exit GUI":
            os.remove(exit_file)
            file_operation = False
        
                
        #if event != "__TIMEOUT__":
        #    print(event)
        #    print(values)
            
        
        # peridoically check if we need to bail out of the process
        elapsed_time = current_landmark - time_landmark
        if elapsed_time.seconds >= 1:
            time_landmark = current_landmark
            if not os.path.isfile(exit_file):
                file_operation = False

        if not file_operation:
            print('User Process Interrupted, Closing File.')
            current_landmark = datetime.now()
            current_time = current_landmark.strftime("m%m_d%d_y%Y_h%H_m%M_s%S")
            data = "SESSION CLOSED\n"
            text_file.write(current_time + "-->" + data)
            text_file.close()  
            break
 


col1 = [
[sg.Text("Select session type: ")], 
[sg.Combo(["Not Running",'Pre-Stimulus', 'Random Stimulus', 'Fixed Stimulus'],key='session_dropdown', enable_events=True,readonly=True,default_value = currentState), sg.Checkbox('Locked?', True, key='sessionlock')],
[sg.Text("",pad=(0,10))],
[sg.Button('Start Stimulus', size = (12, 2)), sg.Button('End Stimulus', size = (12, 2))], 
[sg.Button('Start Recording', size = (12, 2)), sg.Button('End Recording', size = (12, 2))],
[sg.Button('Other Event', size = (12, 2))],
[sg.Text("",pad=(0,10))],
[sg.Button('Open Notes', size = (12, 2))],
[sg.Text("",pad=(0,10))],
[sg.Button('Exit GUI', size = (12, 2), button_color = 'red')]
]


col2 = [
[sg.Text("Time until next recording:", size=(None, 1), justification = 'center')],
[sg.Text("N/A",  size=(None, None), key='text1', text_color='red', font = 'Consolas 35 bold')],
[sg.Text("Time until next recording ends:", size=(None, 1), justification = 'center')],
[sg.Text("N/A",  size=(None, None), key='text2', text_color='red', font = 'Consolas 35 bold')],
[sg.Text("Time remaining in session:", size=(None, 1), justification = 'center')],
[sg.Text("N/A",  size=(None, None), key='text3', text_color='red', font = 'Consolas 35 bold')],
[sg.Text("Total sample time taken:", size=(None, 1), justification = 'center')],
[sg.Text("N/A",  size=(None, None), key='text4', text_color='purple', font = 'Consolas 35 bold')],
]
layout = [[sg.Column(col1,justification = 'center', pad = (15, 30)), sg.Column([],pad=(50,30)), sg.Column(col2,justification = 'center',pad = (35, 60))]]


window = sg.Window("Parkinson's Clinic Controller", layout, resizable=True, no_titlebar=True, auto_size_buttons=False, keep_on_top=True, grab_anywhere=True, size=(715,500))

# Enter main 
if __name__ == '__main__':
    # Setup a unified time

    os.mkdir(patientDirectory)

    # Start an Arduino subprocess
    #ArduinoProcess = Process(target=ReadArduinoOut, args=[current_time])
    #ArduinoProcess.start()
    #
    # The EEG process needs to resolve, so wait for it to hit the kill step
    #exit_file = current_time+"_DELETE_TO_END_SESSION.txt"
    #while not os.path.isfile(exit_file):
    #    time.sleep(.01)
    
    # Start an Events subprocess
    EventsProcess = Process(target=ReadUserEvents, args=[current_time])
    EventsProcess.start()
    
    # The EEG process needs to resolve, so wait for it to hit the kill step
    exit_file = current_time+"_DELETE_TO_END_SESSION.txt"
    while not os.path.isfile(exit_file):
        time.sleep(.1)
    
    # Start an Arduino subprocess
    ArduinoProcess = Process(target=ReadArduinoOut, args=[current_time])
    ArduinoProcess.start()
    
    # Wait for resolution for the subprocesses
    ArduinoProcess.join()
    EventsProcess.join()
    
    window.close()
