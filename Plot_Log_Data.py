import matplotlib.pyplot
import pandas as pd
import matplotlib.pyplot as plt
import datetime
import numpy as np

def FormatPanelData(data):
    data1 = data
    data1['Sim Time'] = data['Sim Time'].map(lambda x: x.rstrip('hr')).astype(float)
    return data1

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

def batteryPlots(batterydata, DependantVariable, axs, xticks):
    axs.grid(color='gray', linestyle='-', linewidth=1)
    axs.xaxis.set_ticks(xticks)
    for battery in batterydata:
        axs.plot(battery["Sim Time"], battery[DependantVariable])


def portPlots(ports, DependantVariable, axs, xticks, yticks = None):
    axs.grid(color='gray', linestyle='-', linewidth=1)
    axs.xaxis.set_ticks(xticks)
    if yticks is not None:
        axs.yaxis.set_ticks(yticks)
    for port in ports:
        print(port["Port"])
        axs.plot(port["Sim Time"], port[DependantVariable], label = port["Port"].iloc[0])

    axs.legend()
    axs.set_ylabel(f"{DependantVariable}")
    axs.set_xlabel(f"Time [Hours]")

def MakePlots(ports, BatteryData, load):
    xticks = np.arange(0,51,1)
    voltageYticks = np.arange(26,29,.1)
    print(xticks)
    fig, axs = plt.subplots(3, sharex=True)
    fig.suptitle(f'Voltage v Time')
    axs[0].set_title("Voltage as Reported by Batteries")
    batteryPlots(BatteryData, 'Voltage[V]', axs[0], xticks)
    axs[1].set_title("Voltage as reported by Panels")
    axs[1].legend()
    portPlots(ports, 'Voltage', axs[1], xticks)
    axs[2].set_title("Voltage as reported by Load")
    portPlots(load, 'Voltage', axs[2], xticks, voltageYticks)


    fig, axs = plt.subplots(3)
    fig.suptitle(f'Current v Time')
    axs[0].set_title("Current as reported by Battery")
    batteryPlots(BatteryData, 'Current [A]', axs[0], xticks)
    axs[1].set_title("Current as reported by Panels")
    portPlots(ports, 'Current', axs[1], xticks)
    axs[2].set_title("Current as reported by Load")
    portPlots(load, 'Current', axs[2], xticks)

    fig, axs = plt.subplots(2)
    axs[0].set_title("Solar Altitude")
    portPlots(ports, 'Solar Alt', axs[0], xticks)
    axs[1].set_title("Panel Efficiency")
    portPlots(ports, 'Panel Eff', axs[1], xticks)
    axs[1].grid(color='gray', linestyle='-', linewidth=.5)
    axs[1].xaxis.set_ticks(xticks)


Battery1Log = "2021-09-17-18-26-Serial-1.log"
Battery2Log = "2021-09-17-18-26-Serial-2.log"
PanelLog = 'HiWind_Panel_17Sep2021_2150.log'
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
loads = [load] # so we can feed in the same function
ports = [p1,p2,p3,p4,p5, aligent]
for port in ports:
    port = FormatPanelData(port)
for load in loads:
    load = FormatPanelData(load)


def CleanLogFile(infile):
    newFile = infile.replace('.log','_Cleaned.log')
    bad_words = ['ADC', '00009', '00008', 'NULL']
    with open(infile) as inf, open(newFile, 'w') as newf:
        for line in inf:
            if not any(bad_word in line for bad_word in bad_words):
                newf.write(line)
    return newFile


def BatteryPlot(infile):
    Data = pd.read_csv(infile, header=0, delimiter='\t')
    df1 = Data[Data['ID'].str.contains('^0008', na=False)]
    df2 = Data[Data['ID'].str.contains('^0009', na=False)]

    df1['Sim Time'] = pd.to_numeric(df1['Sim Time'].map(lambda x: x.rstrip('hr')), errors='coerce')
    df1["Voltage"] = pd.to_numeric(df1["Voltage"], errors='coerce')
    df2['Sim Time'] = pd.to_numeric(df2['Sim Time'].map(lambda x: x.rstrip('hr')), errors='coerce')
    df2["Voltage"] = pd.to_numeric(df2["Voltage"], errors='coerce')




    print(df1['Sim Time'])
    xticks = np.arange(0, 51, 1)
    voltageYticks = np.arange(26, 29, .1)
    print(xticks)
    fig, axs = plt.subplots(1, sharex=True)
    fig.suptitle(f'Voltage v Time')
    axs.set_title("Voltage as Reported by Batteries")
    axs.grid(color='gray', linestyle='-', linewidth=1)
    axs.xaxis.set_ticks(xticks)
    axs.plot(df1["Sim Time"], df1["Voltage"])
    axs.plot(df2["Sim Time"], df2["Voltage"])


infile= "HiWind_Battery_09Nov2021_1755.log"
BatteryPlot(infile)
plt.show()
#B3data, B4data = MatchBeginnings(Battery1Log, PanelLog, B1data, B2data)
#BatteryData = BatteryData()
#BatteryData = [formatBatteryDataTime(B3data), formatBatteryDataTime(B4data)]
#MakePlots(ports, BatteryData, loads)
#plt.show()


