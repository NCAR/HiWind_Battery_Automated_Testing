#!/usr/bin/env python
plot_data = True

import numpy as np
import serial, math, time
import logging
from datetime import datetime

#Sloppy But it works
def BatteryParse(battery):
    try:
        ValidResponse = False
        iter = 0
        while (not ValidResponse) and (iter < 10):
            response = battery.readline().decode('ascii')
            try:
                BatteryID, BatteryVoltage, BatteryTemperature, HeatSinkTemperature, SystemStatus, SOC, Current = response.replace('*', '').strip('\n').strip('\r').split(',')
                ValidResponse = True
            except:
                iter = iter +1
                ValidResponse = False

        return BatteryID, BatteryVoltage, BatteryTemperature, HeatSinkTemperature, SystemStatus, SOC, Current
    except:
        return 'ERR'
#*AAAA,BB.BBB,CCC,DDD,EEEE,FFF, ±GGG.GGG" \
#where:
#AAAA = unique battery ID in Hex" \
#BB.BBB = battery voltage in volts
#CCC = battery temperature in °C. Note: temperature sensor is secured against the
#middle of the lowest voltage cell block
#DDD = Central Controller Heat Sink temperature in °C
#EEEE is system status in Hex containing the following bit mapped information:"

def logging_setup_battery():
    logger = logging_setup("Battery")
    logger.info("Time\tSim Time\tID\tVoltage\tBat Temp[C]\tHeatSink Temp[C]\tStatus\tSOC\tCurrent")
    return logger


def logging_setup_panel():
    logger = logging_setup("Panel")
    logger.info("Time\tSim Time\tSolar Alt\tPanel Eff\tPort\tVoltage\tCurrent")
    return logger


def logging_setup(name, level=logging.DEBUG):

    CurrentDateTime = datetime.now().strftime("%d%b%Y_%H%M")
    filename=f"HiWind_{name}_{CurrentDateTime}.log"
    formatter = logging.Formatter('%(message)s')

    handler = logging.FileHandler(filename)
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)
    return logger

# brief Measure the voltage on the ports
# @return the lowest reported voltage arcross the given list of ports or the voltage on the port itself
def MeasureVoltage(ports):
    if type(ports) == list:
        voltage = 40
        # Find the lowest voltage on all the ports and report that
        for p in ports:
            v = MeasureVoltage(p)
            print(v)
            if v < voltage:
                voltage = v
    else:
        voltage = QueryFloat(ports, "MEAS:VOLT:DC?")
    return voltage


def MeasureCurrent(port):
    return QueryFloat(port, "MEAS:CURR:DC?")


def SetVoltage(ports, val):
    if type(ports) == list:
        for p in ports:
            SendCommand(p, "VOLT " + str(val))
    else:
        SendCommand(ports, "VOLT " + str(val))


def SetCurrent(ports, val):
    if type(ports) == list:
        for p in ports:
            SendCommand(p, "CURR " + str(val))
    else:
        SendCommand(ports, "CURR " + str(val))


def SetAgilentCurrent(port, val):
    volt = AgilentLookUp(val)
    volt = min(5, volt)  # it's good to be paranoid
    SetVoltage(port, volt)


# This will look up the correct value to set the Voltage on the Array power Supply that will drive the current output of the Agilent
def AgilentLookUp(Current):
    AgilentCommandVoltageMax = 5
    AgilentCurrentMax = 15
    # Transfer Function from Current to Voltage
    Voltage = AgilentCommandVoltageMax * Current / AgilentCurrentMax
    # Make sure that the voltage we set wont have bad consequences by making sure that it is under the MaxAmpPerSupply Current
    Voltage = min(Voltage, AgilentCommandVoltageMax)  # never exceed 5 v
    Voltage = min(Voltage,
                  MaxAmpPerSupply / AgilentCurrentMax * AgilentCommandVoltageMax)  # never exceed the equiv of 6.1A out
    return Voltage


# Brief: set the current limit to match the voltage according to the IVCurve.
# Determine the panel current for the currently measured voltage. If the current measured is more than 10% different from what we calculate the panel
# can produce at this voltage, change the current and measure again.
def MatchIVCurve(panel_ports, agilent_port, voltage, efficiency, iter=0):
    # IV Curve
    V = np.array([0, 0.197580, 0.414510, 0.610210, 0.832040, 1.027920, 1.223620, 1.441310, 1.634370, 1.850560, 2.051890,
                  2.248720, 2.466780, 2.657780, 2.876030, 3.070980, 3.271940, 3.487560, 3.685320, 3.900760, 4.096450,
                  4.288950, 4.515480, 4.707980, 4.926230, 5.122300, 5.318560, 5.542460, 5.736650, 5.954720, 6.146280,
                  6.338400, 6.561540, 6.763820, 6.953310, 7.174010, 7.360680, 7.582700, 7.776140, 7.974650, 8.190840,
                  8.387470, 8.604980, 8.799360, 8.997680, 9.224020, 9.416140, 9.632900, 9.826900, 10.018650, 10.237280,
                  10.435790, 10.659690, 10.848800, 11.041680, 11.262000, 11.458830, 11.683280, 11.873340, 12.071860,
                  12.283530, 12.479230, 12.695410, 12.899380, 13.092820, 13.309950, 13.503200, 13.723710, 13.919220,
                  14.119990, 14.340870, 14.530930, 14.753320, 14.943380, 15.141520, 15.363720, 15.558850, 15.774280,
                  15.971110, 16.167370, 16.391640, 16.585640, 16.804840, 16.992820, 17.185510, 17.409410, 17.607550,
                  17.824300, 18.020740, 18.210420, 18.429050, 18.621930, 18.846770, 19.041520, 19.237030, 19.450580,
                  19.640640, 19.839530, 20])
    I = np.array(
        [6.083830, 6.083830, 6.083830, 6.083620, 6.083140, 6.081830, 6.081780, 6.081830, 6.081460, 6.079890, 6.079360,
         6.077370, 6.075110, 6.073850, 6.072170, 6.071330, 6.070330, 6.069180, 6.067600, 6.067130, 6.067340, 6.065350,
         6.064820, 6.064240, 6.064240, 6.063610, 6.062670, 6.062930, 6.061990, 6.060040, 6.060250, 6.059520, 6.057890,
         6.058630, 6.056790, 6.056470, 6.055580, 6.054640, 6.052690, 6.052540, 6.051540, 6.049810, 6.049700, 6.049230,
         6.048700, 6.048490, 6.046600, 6.045130, 6.044450, 6.042400, 6.041140, 6.040770, 6.038570, 6.038250, 6.036420,
         6.034370, 6.033060, 6.031110, 6.028170, 6.026020, 6.023450, 6.020670, 6.016200, 6.013630, 6.009170, 6.005860,
         6.001920, 5.995520, 5.990060, 5.982500, 5.974090, 5.962960, 5.948790, 5.933620, 5.914400, 5.890820, 5.864310,
         5.829660, 5.793330, 5.750380, 5.692520, 5.630720, 5.543880, 5.456100, 5.351510, 5.206550, 5.056390, 4.854200,
         4.643870, 4.395210, 4.068380, 3.732880, 3.297580, 2.857340, 2.358660, 1.732930, 1.122470, 0.443290, 0])
    if (plot_data):
        if not plt.fignum_exists(1):
            plt.figure(1)
            plt.plot(V, I)
            plt.suptitle("IV Curve")
    amps = np.interp(voltage, V, I) * efficiency
    amps = min(amps, MaxAmpPerSupply)
    print(
        "Voltage is {:.1f} V, efficiency {:.2f}, setting current to {:.1f}, iteration {:d}.".format(voltage, efficiency,
                                                                                                    amps, iter))
    SetCurrent(panel_ports, amps)
    if agilent_port is not False:
        SetAgilentCurrent(agilent_port, amps)

    # give time to update and leave transient state
    time.sleep(0.5)
    # re measure voltage and divide by 2 to get voltage on single panel
    panel_voltage = MeasureVoltage(panel_ports) / 2
    panel_current = np.interp(panel_voltage, V, I) * efficiency
    # If the difference between the set current and the panel's expected current is greater than 10%
    if (((abs(amps - panel_current)) > (amps * .1)) and (iter < 5)):
        # re set the current to better match
        iter += 1
        MatchIVCurve(panel_ports, agilent_port, panel_voltage, efficiency, iter)
    print("Performed {:d} IV lookup iterations.".format(iter))
    return amps


def SolarAltitude(hour):
    E = np.array([0, 0, 10.78, 20.97, 30.28, 38.01, 43.25, 45.05, 42.98, 37.52, 29.65, 20.27, 10.04, 0, 0])
    H = np.array([0, 7.5, 8.5, 9.5, 10.5, 11.5, 12.5, 13.5, 14.5, 15.5, 16.5, 17.5, 18.5, 19.5, 24])
    if (plot_data):
        if not plt.fignum_exists(2):
            plt.figure(2)
            plt.plot(H, E)
            plt.suptitle("Solar Altitude")
    return np.interp(hour, H, E)


def PanelEfficiency(hour, PanelAngle):
    # panel angle is normal to panel measured in degrees from horizon
    Altitude = SolarAltitude(hour)
    # cheap hack to ignore sunrise
    if Altitude < 0.5:
        return 0
    SolarAngle = abs(Altitude - PanelAngle)
    return math.cos(math.radians(SolarAngle)) * math.cos(math.radians(15))


def SetLoad(port, hour):
    H = np.array([0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24])
    L = np.array([8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8])
    if (plot_data):
        if not plt.fignum_exists(3):
            plt.figure(3)
            plt.plot(H, L)
            plt.suptitle("Payload Current Draw")
    load = np.interp(hour, H, L)
    SetCurrent(port, load)
    return load


def write_to_log(ports, batteries, elapsedTime, Solar_Alt, Panel_Eff):

    Time = str(datetime.now().strftime("%d%b%y %H:%M:%S"))

    Sim_Time = "{:5.2f}hr".format(elapsedTime)
    Solar_Alt = "{:5.2f}".format(Solar_Alt)
    Panel_Eff = "{:5.2f}".format(Panel_Eff)
    for port in ports:
        Port = port.name
        Voltage = "{:5.2f}".format(MeasureVoltage(port))
        Current = "{:5.2f}".format(MeasureCurrent(port))
        panel_logger.info(f"{Time}\t{Sim_Time}\t{Solar_Alt}\t{Panel_Eff}\t{Port}\t{Voltage}\t{Current}")
    for battery in batteries:
        try:
         BatteryID, BatteryVoltage, BatteryTemperature, HeatSinkTemperature, SystemStatus, SOC, BatteryCurrent = BatteryParse(battery)
         battery_logger.info(f"{Time}\t{Sim_Time}\t{BatteryID}\t{BatteryVoltage}\t{BatteryTemperature}\t{HeatSinkTemperature}\t{SystemStatus}\t{SOC}\t{BatteryCurrent}")
        except:
            battery_logger.info(f"{Time}\t{Sim_Time}\tNULL\tNULL\tNULL\tNULL\tNULL\tNULL\tNULL")


    # Voltage
    # Current
    # Time
    # Simulated Time
    # Port
    return



def RunSimulation(panel_ports, load_port, agilent_port, battery_ports, panel_angle, sleep_duration, time_scaling, starting_hour, test_duration, useLoad = True):
    # sleep duration is in hours
    start = time.time()
    # Setup all the DC Power supplies
    all_ports = panel_ports
    if agilent_port is not False:
        all_ports.append(agilent_port)
    if useLoad:
        all_ports.append(load_port)
    for p in panel_ports:
        SetVoltage(p, 40)
        SetCurrent(p, 0)
        SetOutput(p, True)
    if agilent_port is not False:
        SetCurrent(agilent_port, 1 / 30)  # make sure our control signal cannot push current
        SetVoltage(agilent_port, 0)  # this turns off the current from the agilent to the MEER
        SetOutput(agilent_port, True)
    # Setup the DC load
    if useLoad:
        SetCurrent(load_port, 0)
        SetInput(load_port, True)

    while (True):
        # Find how many Hours its been running
        elapsed_hr = (time.time() - start) / 3600 * time_scaling
        time_of_day = (elapsed_hr + starting_hour) % 24.0

        panelPair_v = MeasureVoltage(panel_ports)
        # battery_v = MeasureVoltage(load_port)
        # Get and Efficiency Percentage of the panel
        eff = PanelEfficiency(time_of_day, panel_angle)

        i = MatchIVCurve(panel_ports, agilent_port, panelPair_v / 2, eff)
        # i=SetILimits(panel_ports, battery_v/2, eff)  # batt/2 because each supply is two panels
        if useLoad:
            load = SetLoad(load_port, time_of_day)

        print("Elapsed: {:5.2f} hr   Solar Alt: {:2.0f} d  Panel Eff: {:2.0f}%  Current in {:5.2f} out NULL".format(
            elapsed_hr, SolarAltitude(time_of_day), eff * 100, i))


        write_to_log(all_ports,battery_ports, elapsed_hr, SolarAltitude(time_of_day), eff*100)

        if (elapsed_hr + sleep_duration * time_scaling) >= test_duration:
            for p in panel_ports:
                SetOutput(p, False)
            SetOutput(agilent_port, False)
            if useLoad:
                SetInput(load_port, False)
            return
        # wait one sleep duration
        time.sleep(sleep_duration * 3600)


# Array communication routines
def SendCommand(port, arg):
    if port != 'A':
        port.write((arg + "\n").encode())


def GetResponse(port, arg):
    try:
        res = port.readline()
        return res.decode('ascii')
    except:
        return 'ERR'


def QueryFloat(port, arg):
    res = Query(port, arg)
    try:
        return float(res)
    except:
        return 'ERR'


def SetInput(port, state):
    if (state):
        SendCommand(port, "INPUT ON")
    else:
        SendCommand(port, "INPUT OFF")


# Brief ask a port for info
# Return the response
def Query(port, arg):
    SendCommand(port, arg)
    res = GetResponse(port, arg)
    return res


# Brief: Turn the output on or off
def SetOutput(port, state):
    if (state):
        SendCommand(port, "OUTPUT ON")
    else:
        SendCommand(port, "OUTPUT OFF")


if (plot_data):
    import matplotlib.pyplot as plt
#  get_ipython().run_line_magic('matplotlib', '')


# TODO Do we need to becarful bc the Com Ports and swap around
# between systems Make sure if your using the Aligent you figure this out in the future
p1 = serial.Serial("com23", 9600, timeout=0.5)
p2 = serial.Serial("com24", 9600, timeout=0.5)
p3 = serial.Serial("com25", 9600, timeout=0.5)
p4 = serial.Serial("com26", 9600, timeout=0.5)
p5 = serial.Serial("com27", 9600, timeout=0.5)
p6 = serial.Serial("com28", 9600, timeout=0.5)
load = serial.Serial("com10", 9600, timeout=0.5)
#load = False
#agilent = serial.Serial("com28", 9600, timeout=0.5)
agilent = False
panels = [p1, p2, p3, p4, p5, p6]


b1 = serial.Serial("com21", 57600, timeout=0.5)
b2 = serial.Serial("com22", 57600, timeout=0.5)
batteries = [b1, b2]

global battery_logger
global panel_logger
battery_logger = logging_setup_battery()
panel_logger = logging_setup_panel()


MaxAmpPerSupply = 6.1

RunSimulation(panels, load, agilent, batteries, 22, 1/3600, 1, 18, 50, useLoad = True)
