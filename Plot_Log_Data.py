import pandas as pd
import matplotlib.pyplot as plt
import datetime


def MatchBeginnings(Battery1Filename, Hiwind_Panel_Filename, Battery1DataFrame, Battery2DataFrame):

    BatteryLogStart = datetime.datetime.strptime(Battery1Filename.split("-Serial")[0], '%Y-%m-%d-%H-%M')
    PanelLogStart = datetime.datetime.strptime(Hiwind_Panel_Filename.split("HiWind_Panel_")[1].split(".log")[0], '%d%b%Y_%H%M')
    difference = BatteryLogStart - PanelLogStart
    seconds_offset = difference.total_seconds()

    return Battery1DataFrame.drop(Battery1DataFrame[Battery1DataFrame['Time [s]'] < abs(seconds_offset)].index), Battery2DataFrame.drop(Battery2DataFrame[Battery2DataFrame['Time [s]'] < abs(seconds_offset)].index)


def formatBatteryDataTime(BatteryData):
    BatteryData['Time [s]'] = BatteryData['Time [s]'] - BatteryData['Time [s]'].iloc[0]
    BatteryData['Time [s]'] = BatteryData['Time [s]']/3600
    return BatteryData

def BatteryDataParsing(filename):
    data = pd.read_csv(filename, header=0, delimiter='\t')
    return data


def agilentDataConversion(agilentDF, agilentMaxCurrent = 15, agilentMaxVoltage = 5):
    agilentDF['Current'] = agilentDF['Voltage']*agilentMaxCurrent/agilentMaxVoltage
    agilentDF['Voltage'] = None
    return agilentDF

def batteryPlots(batterydata, DependantVariable, axs):
    for battery in batterydata:
        axs.plot(battery["Time [s]"], battery[DependantVariable])


def portPlots(ports, DependantVariable, axs):
    for port in ports:
        axs.plot(port["Sim Time"], port[DependantVariable])

def MakePlots(ports, BatteryData, load):
    fig, axs = plt.subplots(3)
    fig.suptitle(f'Voltage v Time')
    axs[0].set_title("Voltage as Reported by Batteries")
    batteryPlots(BatteryData, 'Voltage[V]', axs[0])
    axs[1].set_title("Voltage as reported by Panels")
    portPlots(ports, 'Voltage', axs[1])
    axs[2].set_title("Voltage as reported by Load")
    portPlots(load, 'Voltage', axs[2])


    fig, axs = plt.subplots(3)
    fig.suptitle(f'Current v Time')
    axs[0].set_title("Current as reported by Battery")
    batteryPlots(BatteryData, 'Current [A]', axs[0])
    axs[1].set_title("Current as reported by Panels")
    portPlots(ports, 'Current', axs[1])
    axs[2].set_title("Current as reported by Load")
    portPlots(load, 'Current', axs[2])
    plt.locator_params(axis='x', nbins=24)

    fig, axs = plt.subplots(2)
    axs[0].set_title("Solar Altitude")
    portPlots(ports, 'Solar Alt', axs[0])
    axs[1].set_title("Panel Efficiency")
    portPlots(ports, 'Panel Eff', axs[1])




Battery1Log = "2021-09-13-13-32-Serial-1.log"
Battery2Log = "2021-09-13-13-32-Serial-2.log"
PanelLog = 'HiWind_Panel_13Sep2021_1958.log'
data = pd.read_csv(PanelLog, header=0,delimiter='\t')
B1data = pd.read_csv(Battery1Log, header=0,delimiter='\t')
B2data = pd.read_csv(Battery2Log, header=0,delimiter='\t')


load = data[data["Port"] == "com7"]
aligent = data[data["Port"] == "com8"]
aligent = agilentDataConversion(aligent)
p1 = data[data["Port"] == "com9"]
p2 = data[data["Port"] == "com10"]
p3 = data[data["Port"] == "com11"]
p4 = data[data["Port"] == "com12"]
p5 = data[data["Port"] == "com13"]
load = [load] # so we can feed in the same function
ports = [p1,p2,p3,p4,p5, aligent]

B3data, B4data = MatchBeginnings(Battery1Log, PanelLog, B1data, B2data)
BatteryData = [formatBatteryDataTime(B3data), formatBatteryDataTime(B4data)]
MakePlots(ports, BatteryData, load)
plt.show()
