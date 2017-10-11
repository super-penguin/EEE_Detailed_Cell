from neuron import h, gui
import matplotlib.pyplot as plt
import numpy as np
from utils import *

soma = h.Section(name='soma')
dend = h.Section(name='dend')

dend.connect(soma(1))

# Surface area of cylinder is 2*pi*r*h (sealed ends are implicit).
soma.L = soma.diam = 12.6157 # Makes a soma of 500 microns squared.
dend.L = 200 # microns
dend.diam = 1 # microns

for sec in h.allsec():
    sec.Ra = 100    # Axial resistance in Ohm * cm
    sec.cm = 1      # Membrane capacitance in micro Farads / cm^2

# Insert active Hodgkin-Huxley current in the soma
#soma.insert('hh')
#soma.gnabar_hh = 0 # Sodium conductance in S/cm2
#soma.gkbar_hh = 0  # Potassium conductance in S/cm2
#soma.gl_hh = 0.0003    # Leak conductance in S/cm2
#soma.el_hh = - 65     # Reversal potential in mV

# Insert passive current in the dendrite
#dend.insert('pas')
#dend.g_pas = 0.001  # Passive conductance in S/cm2
#dend.e_pas = -65    # Leak reversal potential mV
#dend.nseg = 10


def explore_VI(vin):
    # add NetStim
    #h.init()
    ns = h.NetStim()
    ns.interval = 20
    ns.number = 1
    ns.start = 50
    ns.noise = 0

    SynNMDA = h.NMDA(soma(0.5))
    SynNMDA.gmax = 0.1
    nc_NMDA = h.NetCon(ns, SynNMDA)
    nc_NMDA.delay = 0
    nc_NMDA.weight[0] = 0.05

    Vclamp = h.SEClamp(soma(0.5))
    Vclamp.dur1 = 60
    Vclamp.rs = 0.01 # series resistance should be much smaller than input resistance of the cell
    Vclamp.dur2 = 1e9
    Vclamp.amp1 = -65
    Vclamp.amp2 = vin

    t_vec = h.Vector()
    t_vec.record(h._ref_t)
    NMDA_i = h.Vector()
    NMDA_i.record(SynNMDA._ref_iNMDA)

    h.init()
    h.tstop = 500 # ms
    h.run()

    if vin<= 0:
        return min(NMDA_i.as_numpy()), t_vec.as_numpy, NMDA_i.as_numpy
    else:
        return max(NMDA_i.as_numpy()), t_vec.as_numpy, NMDA_i.as_numpy




Vstep = [x for x in range(-90, 50, 20)]

NMDA_vec = []
time = []

for V in Vstep:
    temp1, temp2, temp3 = explore_VI(V)
    time.append(temp2)
    NMDA_vec.append(temp3)


NMDA_peak = []
Vc = [x for x in range(-90, 70, 2)]
for V in Vc:
    temp1, temp2, temp3 = explore_VI(V)
    NMDA_peak.append(temp1)


plt.clf()
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15,20))
for i in range(len(time)):
    ax1.plot(time[i],NMDA_vec[i], label = str(Vstep[i])+'mV')
    ax1.set_title("NMDA current at different voltage clamp")
    ax1.legend(loc = "best")
    ax1.set_xlabel("Time (ms)")
    ax1.set_ylabel("Current(nA)")


ax2.plot(Vc, NMDA_peak)
ax2.set_xlim([-90, 70])
ax2.set_ylim([-0.015, 0.04])
ax2.set_xlabel("Voltage Clamp (mV)")
ax2.set_ylabel("Current of NMDAR (nA)")
ax2.set_title("NMDAR I-V curve")

#save("NMDA I-V curve")
plt.show()

#t, i = explore_VI(0)
#print min(i.as_numpy())#

### plot voltage vs time
#plt.figure(figsize=(8,4)) # Default figsize is (8,6)
#plt.plot(t, i, 'r')
##plt.ylim([-0.02, 0.002])
###pyplot.plot(t_vec, v_vec_axon, 'g')
##plt.xlabel('time (ms)')
##plt.ylabel('mV')
#plt.show()
