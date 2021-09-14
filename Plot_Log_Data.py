import pandas as pd
import matplotlib.pyplot as plt

data = pd.read_csv('C:\\Users\\mjeffers\\Desktop\\TestData.log', header=0,delimiter='\t')




p2 = data[data["Port"] == "com7"]
p1 = data[data["Port"] == "com8"]
load = data[data["Port"] == "com9"]
p3 = data[data["Port"] == "com10"]
p4 = data[data["Port"] == "com11"]
p5 = data[data["Port"] == "com12"]
p6 = data[data["Port"] == "com13"]

plt.plot(p2["Sim Time"], p2['Voltage'])
plt.show()


