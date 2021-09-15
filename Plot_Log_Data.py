import pandas as pd
import matplotlib.pyplot as plt
import datetime

def MatchBeginnings(Battery1Filename, Battery1DF, Battery2Filename, Battery2DF, Hiwind_Panel_Filename):
    datetime = Battery1Filename.split("-Serial")[0]
    datetime.strptime('Jun 1 2005  1:33PM', '%b %d %Y %I:%M%p')
    return

def BatteryDataParsing(filename):
    data = pd.read_csv(filename, header=0, delimiter='\t')

    matchedDF =
    return


def agilentDataConversion(agilentDF, agilentMaxCurrent = 15, agilentMaxVoltage = 5):
    agilentDF['Current'] = agilentDF['Voltage']*agilentMaxCurrent/agilentMaxVoltage
    agilentDF['Voltage'] = None
    return agilentDF


def voltageVTime(ports, DependantVariable):
    fig, axs = plt.subplots(2)
    fig.suptitle(f'{DependantVariable} V Time ports')
    for port in ports:
        axs[0].plot(port["Sim Time"], port[DependantVariable])


data = pd.read_csv('HiWind_Panel_13Sep2021_1958.log', header=0,delimiter='\t')

load = data[data["Port"] == "com7"]
aligent = data[data["Port"] == "com8"]
p1 = data[data["Port"] == "com9"]
p2 = data[data["Port"] == "com10"]
p3 = data[data["Port"] == "com11"]
p4 = data[data["Port"] == "com12"]
p5 = data[data["Port"] == "com13"]

ports = [p1,p2,p3,p4,p5]

voltageVTime(ports, 'Current')

plt.show()
