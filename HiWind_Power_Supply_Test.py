#!/usr/bin/env python
# coding: utf-8

# In[1]:


import numpy as np
import serial, math, time
import matplotlib.pyplot as plt
get_ipython().run_line_magic('matplotlib', '')
p1=serial.Serial("com13",9600, timeout=0.5)
p2=serial.Serial("com14",9600, timeout=0.5)
p3=serial.Serial("com15",9600, timeout=0.5)
p4=serial.Serial("com16",9600, timeout=0.5)
p5=serial.Serial("com17",9600, timeout=0.5)
p6=serial.Serial("com18",9600, timeout=0.5)
load=serial.Serial("com11",9600, timeout=0.5)
panels = [p1, p2, p3, p4, p5, p6]
plot_data = True

# In[82]:



# Array communication routines
def SendCommand(port, arg):
    if port != 'A':
        port.write((arg + "\n").encode())
        
        
def GetResponse(port, arg):
    try:
        res=port.readline()
        return res.decode('ascii')
    except:
        return 'ERR'   

    
def QueryFloat(port, arg):
    res=Query(port,arg)
    try:
        return float(res)
    except:
        return 'ERR'

#Brief ask a port for info
#Return the response
def Query(port, arg):
    SendCommand(port, arg)
    res=GetResponse(port,arg)
    return res

#Brief: Turn the output on or off
def SetOutput(port, state):
    if (state):
        SendCommand(port, "OUTPUT ON")
    else:
        SendCommand(port, "OUTPUT OFF")

# brief Measure the voltage on the ports
# @return the highest reported voltage arcross the given list of ports or the voltage on the port itself
#TODO this may have unwanted implication when the MEER Charge Controller stops accepting power from a supply. 
#ie return will always be 40V?? Maybe check to see if current is still being delivered from that supply 
def MeasureVoltage(ports):
    voltage = 0
    
    if type(port) == list:
    #Find the Highest voltage on all the ports and report that
        for p in port:
            v=MeasureVoltage(p)
            if v > voltage:
                voltage = v
    else:
        voltage = MeasureVoltage(ports)
    return voltage
    
    return QueryFloat(port, "MEAS:VOLT:DC?")


def MeasureCurrent(port):
    return QueryFloat(port, "MEAS:CURR:DC?")


def MeasureWattage(port):
    return QueryFloat(port, "MEAS:VOLT:DC?") * QueryFloat(port, "MEAS:CURR:DC?")


def SetVoltage(port, val):
    if type(port) == list:
        for p in port:
            SendCommand(p, "VOLT "+str(val))
    else:
        SendCommand(port, "VOLT "+str(val))

        
        
def SetCurrent(port, val):
    if type(port) == list:
        for p in port:
            SendCommand(p, "CURR "+str(val))
    else:
        SendCommand(port, "CURR "+str(val))


        
        
def SetInput(port, state):
    if (state):
        SendCommand(port, "INPUT ON")
    else:
        SendCommand(port, "INPUT OFF")
            

#Brief: set the current limit to match the voltage according to the IVCurve. 
#If the new voltage of the DC power supply is greater than 10% different than the expected voltage then change the current limit again to better match
def MatchIVCurve(ports, voltage, efficiency):
    #IV Curve
    V=np.array([0, 0.197580, 0.414510, 0.610210, 0.832040, 1.027920, 1.223620, 1.441310, 1.634370, 1.850560, 2.051890, 2.248720, 2.466780, 2.657780, 2.876030, 3.070980, 3.271940, 3.487560, 3.685320, 3.900760, 4.096450, 4.288950, 4.515480, 4.707980, 4.926230, 5.122300, 5.318560, 5.542460, 5.736650, 5.954720, 6.146280, 6.338400, 6.561540, 6.763820, 6.953310, 7.174010, 7.360680, 7.582700, 7.776140, 7.974650, 8.190840, 8.387470, 8.604980, 8.799360, 8.997680, 9.224020, 9.416140, 9.632900, 9.826900, 10.018650, 10.237280, 10.435790, 10.659690, 10.848800, 11.041680, 11.262000, 11.458830, 11.683280, 11.873340, 12.071860, 12.283530, 12.479230, 12.695410, 12.899380, 13.092820, 13.309950, 13.503200, 13.723710, 13.919220, 14.119990, 14.340870, 14.530930, 14.753320, 14.943380, 15.141520, 15.363720, 15.558850, 15.774280, 15.971110, 16.167370, 16.391640, 16.585640, 16.804840, 16.992820, 17.185510, 17.409410, 17.607550, 17.824300, 18.020740, 18.210420, 18.429050, 18.621930, 18.846770, 19.041520, 19.237030, 19.450580, 19.640640, 19.839530, 20])
    I=np.array([6.083830, 6.083830, 6.083830, 6.083620, 6.083140, 6.081830, 6.081780, 6.081830, 6.081460, 6.079890, 6.079360, 6.077370, 6.075110, 6.073850, 6.072170, 6.071330, 6.070330, 6.069180, 6.067600, 6.067130, 6.067340, 6.065350, 6.064820, 6.064240, 6.064240, 6.063610, 6.062670, 6.062930, 6.061990, 6.060040, 6.060250, 6.059520, 6.057890, 6.058630, 6.056790, 6.056470, 6.055580, 6.054640, 6.052690, 6.052540, 6.051540, 6.049810, 6.049700, 6.049230, 6.048700, 6.048490, 6.046600, 6.045130, 6.044450, 6.042400, 6.041140, 6.040770, 6.038570, 6.038250, 6.036420, 6.034370, 6.033060, 6.031110, 6.028170, 6.026020, 6.023450, 6.020670, 6.016200, 6.013630, 6.009170, 6.005860, 6.001920, 5.995520, 5.990060, 5.982500, 5.974090, 5.962960, 5.948790, 5.933620, 5.914400, 5.890820, 5.864310, 5.829660, 5.793330, 5.750380, 5.692520, 5.630720, 5.543880, 5.456100, 5.351510, 5.206550, 5.056390, 4.854200, 4.643870, 4.395210, 4.068380, 3.732880, 3.297580, 2.857340, 2.358660, 1.732930, 1.122470, 0.443290, 0])
    amps=np.interp(voltage, V,I)*efficiency
    
    SetCurrent(ports, amps)
    #give time to update and leave transient state
    time.sleep(2)
    #re measure voltage and divide by 2 to get voltage on single panel
    updated_voltage/2 = MeasureVoltage(ports)
    #If the difference between the measured voltage and the expected voltage is greater than 10%
    if (abs(updated_voltage - V) > V*.1):
        #re set the current to better match
        MatchIVCurve(ports, updated_voltage, efficiency)
    return amps


def SetILimits(ports, battery_voltage, efficiency):
    # flux is a ratio of incident power vs. IV data test conditions
    V=np.array([0, 0.197580, 0.414510, 0.610210, 0.832040, 1.027920, 1.223620, 1.441310, 1.634370, 1.850560, 2.051890, 2.248720, 2.466780, 2.657780, 2.876030, 3.070980, 3.271940, 3.487560, 3.685320, 3.900760, 4.096450, 4.288950, 4.515480, 4.707980, 4.926230, 5.122300, 5.318560, 5.542460, 5.736650, 5.954720, 6.146280, 6.338400, 6.561540, 6.763820, 6.953310, 7.174010, 7.360680, 7.582700, 7.776140, 7.974650, 8.190840, 8.387470, 8.604980, 8.799360, 8.997680, 9.224020, 9.416140, 9.632900, 9.826900, 10.018650, 10.237280, 10.435790, 10.659690, 10.848800, 11.041680, 11.262000, 11.458830, 11.683280, 11.873340, 12.071860, 12.283530, 12.479230, 12.695410, 12.899380, 13.092820, 13.309950, 13.503200, 13.723710, 13.919220, 14.119990, 14.340870, 14.530930, 14.753320, 14.943380, 15.141520, 15.363720, 15.558850, 15.774280, 15.971110, 16.167370, 16.391640, 16.585640, 16.804840, 16.992820, 17.185510, 17.409410, 17.607550, 17.824300, 18.020740, 18.210420, 18.429050, 18.621930, 18.846770, 19.041520, 19.237030, 19.450580, 19.640640, 19.839530, 20])
    I=np.array([6.083830, 6.083830, 6.083830, 6.083620, 6.083140, 6.081830, 6.081780, 6.081830, 6.081460, 6.079890, 6.079360, 6.077370, 6.075110, 6.073850, 6.072170, 6.071330, 6.070330, 6.069180, 6.067600, 6.067130, 6.067340, 6.065350, 6.064820, 6.064240, 6.064240, 6.063610, 6.062670, 6.062930, 6.061990, 6.060040, 6.060250, 6.059520, 6.057890, 6.058630, 6.056790, 6.056470, 6.055580, 6.054640, 6.052690, 6.052540, 6.051540, 6.049810, 6.049700, 6.049230, 6.048700, 6.048490, 6.046600, 6.045130, 6.044450, 6.042400, 6.041140, 6.040770, 6.038570, 6.038250, 6.036420, 6.034370, 6.033060, 6.031110, 6.028170, 6.026020, 6.023450, 6.020670, 6.016200, 6.013630, 6.009170, 6.005860, 6.001920, 5.995520, 5.990060, 5.982500, 5.974090, 5.962960, 5.948790, 5.933620, 5.914400, 5.890820, 5.864310, 5.829660, 5.793330, 5.750380, 5.692520, 5.630720, 5.543880, 5.456100, 5.351510, 5.206550, 5.056390, 4.854200, 4.643870, 4.395210, 4.068380, 3.732880, 3.297580, 2.857340, 2.358660, 1.732930, 1.122470, 0.443290, 0])
    if 'plt' in dir():
        if not plt.fignum_exists(1):
            plt.figure(1)
            plt.plot(V,I)
            plt.suptitle("IV Curve")
    amps=np.interp(battery_voltage,V,I) * efficiency
    SetCurrent(ports, amps)
    return amps


def SolarAltitude(hour):
    E=np.array([0, 0,   10.78, 20.97, 30.28, 38.01, 43.25, 45.05, 42.98, 37.52, 29.65, 20.27, 10.04, 0,    0])
    H=np.array([0, 7.5, 8.5,   9.5,   10.5,  11.5,  12.5,  13.5,  14.5,  15.5,  16.5,  17.5,  18.5, 19.5, 24])
    if 'plt' in dir():
        if not plt.fignum_exists(2):
            plt.figure(2)
            plt.plot(H,E)
            plt.suptitle("Solar Altitude")
    return np.interp(hour, H, E)


def PanelEfficiency(hour, PanelAngle):
    # panel angle is normal to panel measured in degrees from horizon
    Altitude = SolarAltitude(hour)
    # cheap hack to ignore sunrise
    if Altitude < 0.5:
        return 0
    SolarAngle = abs(Altitude-PanelAngle)
    return math.cos(math.radians(SolarAngle)) * math.cos(math.radians(15))


def SetLoad(port, hour):
    H=np.array([0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24])
    L=np.array([7, 7, 7, 7, 7, 7,  7,  7,  7,  7,  7,  7,  7])
    if 'plt' in dir():
        if not plt.fignum_exists(3):
            plt.figure(3)
            plt.plot(H,L)
            plt.suptitle("Payload Current Draw")
    load = np.interp(hour, H, L)
    SetCurrent(port, load)
    return load



def RunSimulation(panel_ports, load_port, panel_angle, sleep_duration, time_scaling):
    # sleep duration is in hours
    start=time.time()
    #Setup all the DC Power supplies
    for p in panel_ports:
        SetVoltage(p, 40)
        SetCurrent(p, 0)
        SetOutput(p, True)
    #Setup the DC load
    SetCurrent(load_port, 0)
    SetInput(load_port, True)
    
    
    while (True):
        #Find how many Hours its been running
        elapsed_hr=(time.time()-start) / 3600 * time_scaling
        panelPair_v = MeasureVoltage(panel_ports)
        #battery_v = MeasureVoltage(load_port)
        #Get and Efficiency Percentage of the panel
        eff=PanelEfficiency(elapsed_hr, panel_angle)
        
        i=MatchIVCurve(panel_ports, panelPair_v/2, eff)
        #i=SetILimits(panel_ports, battery_v/2, eff)  # batt/2 because each supply is two panels
        load=SetLoad(load_port, elapsed_hr)
        print("Elapsed: {:5.2f} hr   Solar Alt: {:2.0f} d  Panel Eff: {:2.0f}%  Current in {:5.2f} out {:5.2f}".format(
               elapsed_hr, SolarAltitude(elapsed_hr), eff*100, i, load))
        if (elapsed_hr + sleep_duration* time_scaling) >= 24:
            for p in panel_ports:
                SetOutput(p, False)
            SetInput(load_port, False)
            return
        #wait one second
        time.sleep(sleep_duration*3600)
        

        
        
    


# In[90]:


RunSimulation('A', 'A', 22, 1/3600, 5000)

