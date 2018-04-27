from neuron import h, gui
import matplotlib.pyplot as plt
import numpy as np
from utils import *
import os
from analysis_utils import *

path = os.getcwd()

##########################################
class Cell():
    def __init__(self, name = 'NMDA'):
        self.name = name
        self.create_sections()
        self.define_geometry()
        self.define_biophysics()
        self.insert_NMDA()

    def create_sections(self):
        """Create the sections of the cell."""
        self.soma = h.Section(name='soma')

    def define_geometry(self):
        """Set the 3D geometry of the cell."""
        self.soma.L = self.soma.diam = 12.6157 # microns

    def define_biophysics(self):
        """Assign the membrane properties across the cell."""
        for sec in [self.soma]: #
            sec.Ra = 100    # Axial resistance in Ohm * cm
            sec.cm = 1      # Membrane capacitance in micro Farads / cm^2

    def insert_NMDA(self):
        # Insert the NMDA Channel:
        self.ns = h.NetStim()
        self.ns.interval = 20
        self.ns.number = 1
        self.ns.start = 200
        self.ns.noise = 0

        if self.name == 'major': # It doesn't work!!! Why???
            self.SynNMDA = h.nmda(self.soma(0.5))
            self.SynNMDA.gmax = 0.005
            self.SynNMDA.onset = 200
            # self.SynNMDA = h.NMDAmajor(self.soma(0.5))
        else:
            if self.name == 'NMDA':
                self.SynNMDA = h.NMDA(self.soma(0.5))
                self.SynNMDA.gmax = 0.01
            elif self.name == 'NMDAeee':
                self.SynNMDA = h.NMDAeee(self.soma(0.5))
                self.SynNMDA.gmax = 0.01
                self.SynNMDA.Beta = 0.02
                self.SynNMDA.Cdur = 10
            self.nc_NMDA = h.NetCon(self.ns, self.SynNMDA)
            self.nc_NMDA.delay = 0
            self.nc_NMDA.weight[0] = 0.5


    def add_voltage_stim(self, V0, V1, V2, D1 = 200, D2 = 1000, D3 = 300):
        self.Vclamp = h.SEClamp(self.soma(0.5))
        self.Vclamp.dur1 = D1
        self.Vclamp.rs = 0.01 # series resistance should be much smaller than input resistance of the cell
        self.Vclamp.dur2 = D2
        self.Vclamp.dur3 = D3
        self.Vclamp.amp1 = V0
        self.Vclamp.amp2 = V1
        self.Vclamp.amp3 = V2

    def set_recording(self):
        """Set soma, dendrite, and time recording vectors on the cell. """
        self.soma_v_vec = h.Vector()   # Membrane potential vector at soma
        self.t_vec = h.Vector()        # Time stamp vector
        self.soma_v_vec.record(self.soma(0.5)._ref_v)
        self.t_vec.record(h._ref_t)
        self.NMDA_i = h.Vector()
        # self.NMDA_i.record(self.Vclamp._ref_i)
        if self.name == 'major':
            self.NMDA_i.record(self.SynNMDA._ref_i)
        else:
            self.NMDA_i.record(self.SynNMDA._ref_iNMDA)

    def plot_voltage(self):
        """Plot the recorded traces"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4)) # Default figsize is (8,6)
        ax1.plot(self.t_vec, self.soma_v_vec, color='black', label='soma(0.5)')
        ax1.set_ylim(-80,80)
        ax1.set_xlabel('time (ms)')
        ax1.set_ylabel('mV')
        ax1.set_title("Voltage_clamp")
        ax2.plot(self.t_vec, self.NMDA_i)
        ax2.set_title("NMDA current at different voltage clamp")
        ax2.set_xlabel("Time (ms)")
        ax2.set_ylabel("Current(nA)")


##########################
# Voltage-clamp protocol
##########################
# def generate_voltage_clamp_fig(cell = Cell, Vmin = -80, Vmax = 60, Vstep = 10, N = 10):
#     plt.close()
#     plt.clf()
#     fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
#     plt.subplots_adjust(left=0.15, right=0.9, top=0.8, bottom=0.15, wspace = 0.5, hspace = 0.25)
#     plt.style.use("ggplot")
#     plt.rcParams['axes.edgecolor'] = "black"
#     plt.rcParams['axes.facecolor'] = "white"
#     ax1.spines['right'].set_visible(False)
#     ax1.spines['top'].set_visible(False)
#     ax1.yaxis.set_ticks_position('left')
#     ax1.xaxis.set_ticks_position('bottom')
#     ax2.spines['right'].set_visible(False)
#     ax2.spines['top'].set_visible(False)
#     ax2.yaxis.set_ticks_position('left')
#     ax2.xaxis.set_ticks_position('bottom')
#
#     for i in range(N):
#         V1 = Vmin + Vstep*i
#         cell.add_voltage_stim(-65, V1, -65)
#         cell.set_recording()
#         h.tstop = 1500 # set simulation duration
#         h.celsius = 32
#         h.init()
#         h.run()  # run simulation
#         ax1.plot(cell.t_vec, cell.soma_v_vec, color = tableau(2*i), label='soma(0.5)')
#         ax1.set_ylim(-100,80)
#         ax1.set_xlabel('time (ms)', fontsize = 20)
#         ax1.set_ylabel('mV', fontsize = 20)
#         ax1.set_title("Voltage clamp protocols", y=1.08, fontsize = 20)
#         ax2.plot(cell.t_vec, cell.NMDA_i, color = tableau(2*i))
#         ax2.set_ylim(-0.05, 0.001)
#         ax2.set_title(str(cell.name) + " - current at different voltage", y=1.08, fontsize = 20)
#         ax2.set_xlabel("Time (ms)", fontsize = 20)
#         ax2.set_ylabel("Current(nA)", fontsize = 20)
#         # fig.tight_layout()
#     plt.rc('xtick', labelsize= 15)
#     plt.rc('ytick', labelsize= 15)
#     title = str(cell.name) + "_Voltage_Protocol"
#     save(title, path, ext = 'png', close = True, verbose = True)
#
cell1 = Cell('NMDA')
cell2 = Cell('NMDAeee')
cell3 = Cell('major')
# generate_voltage_clamp_fig(cell1, -80, 0, 10, 9)
# generate_voltage_clamp_fig(cell2, -80, 0, 10, 9)
# generate_voltage_clamp_fig(cell3, -80, 0, 10, 9)

##########################
# I-V curve
##########################

def IV_curve(cell = Cell, Vmin = -80, Vmax = 60, N = 10):

    Vstep = [x for x in range(Vmin, Vmax, N)]
    NMDA_peak = []
    time = []
    for V in Vstep:
        cell.add_voltage_stim(-65, V, -65)
        cell.set_recording()
        h.tstop = 1500 # set simulation duration
        h.celsius = 16# 32
        h.v_init =  -65
        h.init()
        h.run()
        time.append(cell.t_vec.as_numpy)
        if V<= 0:
            NMDA_peak.append(min(cell.NMDA_i.as_numpy()))
        else:
            NMDA_peak.append(max(cell.NMDA_i.as_numpy()))

    plt.close()
    plt.clf()
    plt.figure(figsize=(9, 6))
    plt.subplots_adjust(left=0.15, right=0.9, top=0.8, bottom=0.15)
    ax = plt.gca()
    plt.style.use("ggplot")
    plt.rcParams['axes.edgecolor'] = "black"
    plt.rcParams['axes.facecolor'] = "white"
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.yaxis.set_ticks_position('left')
    ax.xaxis.set_ticks_position('bottom')
    plt.plot(Vstep, NMDA_peak)
    # plt.xlim([-90, 70])
    # plt.ylim([-0.055, 0.25])
    plt.xlabel("Voltage Clamp (mV)")
    plt.ylabel("Current of NMDAR (nA)")
    plt.title(str(cell.name) + " I-V curve")
    title = str(cell.name) + "_IV_curve"
    save(title, path, ext = 'png', close = True, verbose = True)


IV_curve(cell1, -90, 60, 10)
IV_curve(cell2, -90, 60, 10)
IV_curve(cell3, -90, 60, 20)
#save("NMDA I-V curve")


#####################
# Ramp voltage clamp protocols
#####################
# t = h.Vector()
#
# Vclamp = h.SEClamp(cell.soma(0.5))
# Vclamp.dur1 = 1e9
# Vclamp.rs = 0.01 # series resistance should be much smaller than input resistance of the cell
# tempvec = h.Vector()

##########################
# Voltage-clamp protocol2
##########################
# def generate_voltage_clamp2_fig(cell = Cell, Vmin = -80, Vmax = -20, Vstep = 10, N = 10):
#     plt.close()
#     plt.clf()
#     fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
#     plt.subplots_adjust(left=0.15, right=0.9, top=0.8, bottom=0.15, wspace = 0.5, hspace = 0.25)
#     plt.style.use("ggplot")
#     plt.rcParams['axes.edgecolor'] = "black"
#     plt.rcParams['axes.facecolor'] = "white"
#     ax1.spines['right'].set_visible(False)
#     ax1.spines['top'].set_visible(False)
#     ax1.yaxis.set_ticks_position('left')
#     ax1.xaxis.set_ticks_position('bottom')
#     ax2.spines['right'].set_visible(False)
#     ax2.spines['top'].set_visible(False)
#     ax2.yaxis.set_ticks_position('left')
#     ax2.xaxis.set_ticks_position('bottom')
#
#     for i in range(N):
#         V1 = Vmax - Vstep*i
#         cell.add_voltage_stim(-65, -20, V1, 200, 50, 1e9)
#         cell.set_recording()
#         h.tstop = 1500 # set simulation duration
#         h.celsius = 32
#         h.init()
#         h.run()  # run simulation
#         ax1.plot(cell.t_vec, cell.soma_v_vec, color = tableau(2*i), label='soma(0.5)')
#         ax1.set_ylim(-100,80)
#         ax1.set_xlabel('time (ms)', fontsize = 20)
#         ax1.set_ylabel('mV', fontsize = 20)
#         ax1.set_title("Voltage clamp protocols", y=1.08, fontsize = 20)
#         ax2.plot(cell.t_vec, cell.NMDA_i, color = tableau(2*i))
#         ax2.set_ylim(-0.05, 0.001)
#         ax2.set_title(str(cell.name) + " - current at different voltage", y=1.08, fontsize = 20)
#         ax2.set_xlabel("Time (ms)", fontsize = 20)
#         ax2.set_ylabel("Current(nA)", fontsize = 20)
#         # fig.tight_layout()
#     plt.rc('xtick', labelsize= 15)
#     plt.rc('ytick', labelsize= 15)
#     title = str(cell.name) + "_Voltage_Protocol2"
#     save(title, path, ext = 'png', close = True, verbose = True)
#
# generate_voltage_clamp2_fig(cell1, -80, -20, 10, 6)
# generate_voltage_clamp2_fig(cell2, -80, -20, 10, 6)
# generate_voltage_clamp2_fig(cell3, -80, -20, 10, 6)
