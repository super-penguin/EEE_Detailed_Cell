from neuron import h, gui
import matplotlib.pyplot as plt
import numpy as np
from utils import *

h.load_file("stdrun.hoc")

soma = h.Section(name='soma')
# Surface area of cylinder is 2*pi*r*h (sealed ends are implicit).
soma.L = soma.diam = 12.6157 # Makes a soma of 500 microns squared.

for sec in h.allsec():
    sec.Ra = 100    # Axial resistance in Ohm * cm
    sec.cm = 1      # Membrane capacitance in micro Farads / cm^2

soma.insert('na')

def explore_VI(vin):
    Vclamp = h.SEClamp(soma(0.5))
    Vclamp.dur1 = 10
    Vclamp.dur2 = 50
    Vclamp.rs = 0.01 # series resistance should be much smaller than input resistance of the cell
    Vclamp.amp1 = -65
    Vclamp.amp2 = vin

    t_vec = h.Vector()
    t_vec.record(h._ref_t)
    na_i = h.Vector()
    na_i.record(Vclamp._ref_i)

    h.init()
    h.tstop = 80 # ms
    h.run()

    current = []
    for index,val in enumerate(t_vec):
        if val < 10.05:
            current.append(0)
        else:
            current.append(na_i[index])

    if vin> 48:
        return max(current), t_vec.as_numpy, current
    else:
        return min(current), t_vec.as_numpy, current

Vstep = [x for x in range(-70, 90, 20)]
Na_vec = []
time = []
for V in Vstep:
    temp1, temp2, temp3 = explore_VI(V)
    time.append(temp2)
    Na_vec.append(temp3)


Na_peak = []
Vc = [x for x in range(-90, 70, 2)]
for V in Vc:
    temp1, temp2, temp3 = explore_VI(V)
    Na_peak.append(temp1)


plt.clf()
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15,20))
for i in range(len(time)):
    ax1.plot(time[i],Na_vec[i], label = str(Vstep[i])+'mV')
    ax1.set_title("Na current at different voltage clamp")
    ax1.legend(loc = "best")
    ax1.set_xlabel("Time (ms)")
    ax1.set_ylabel("Current(nA)")
    ax1.set_xlim([0, 50])

ax2.plot(Vc, Na_peak)
ax2.set_xlim([-90, 70])
#ax2.set_xlim([-90, 40])
#ax2.set_ylim([-0.015, 0.04])
ax2.set_xlabel("Voltage Clamp (mV)")
ax2.set_ylabel("Current of Na (nA)")
ax2.set_title("Na I-V curve")

save("Sodium I-V curve")


#plt.show()
