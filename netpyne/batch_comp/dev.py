# See plateau measurement calculations for experimental data

import os
import batch_utils
import batch_analysis as ba
import numpy as np
import matplotlib.pyplot as plt

plt.ion()


curpath = os.getcwd()
while os.path.split(curpath)[1] != "eee":
    oldpath = curpath
    curpath = os.path.split(curpath)[0]
    if oldpath == curpath:
        raise Exception("Couldn't find data directory. Try running from within eee/sim file tree.")
datapath = os.path.join(curpath, "data")
expdata = batch_utils.import_excel(os.path.join(datapath, "srdjan_20171017/B_73_004.xlsx"))

expparam1 = {}
expparam1['label'] = 'glutAmp'
#expparam1['values'] = np.linspace(min(sim_glutAmps), max(sim_glutAmps), 10).round(2)
expparam1['values'] = np.linspace(1, 10, 10).round(2)
expdata_params = [expparam1]

time = np.array(expdata.index.tolist())

platamps = []
platdurs = []
numspikes = []
spikefreqs = []
timetospikes = []
interspikes = []

for column in np.arange(0, len(expdata.columns)):
    
    cur_data = np.array(expdata.iloc[:,column].tolist())
    
    clip_trace, clip_time = ba.clip_trace_spikes(cur_data, time=time, showwork=True)

    platamp, platvolt = ba.meas_trace_plat_amp(cur_data, time=time, recstep=0.2, stable=0.0)
    platamps.append(platamp)

    platdur, plattimes = ba.meas_trace_plat_dur(cur_data, time=time, recstep=0.2, stable=0.0, showwork=True)
    platdurs.append(platdur)

    numspike = ba.meas_trace_num_spikes(cur_data, time=time, recstep=0.2, showwork=False)
    numspikes.append(numspike)

    spikefreq = ba.meas_trace_spike_freq(cur_data, time=time, recstep=0.2)
    spikefreqs.append(spikefreq)

    time_to_spike = ba.meas_trace_time_to_spike(cur_data, time=time, recstep=0.2, syntime=100.0, showwork=False)
    timetospikes.append(time_to_spike)

    interspike = ba.meas_trace_first_interspike(cur_data, time=time, recstep=0.2, showwork=False)
    interspikes.append(interspike)

expdata_platamps = {}
expdata_platamps['label'] = 'Plateau Amplitude (mV)'
expdata_platamps['values'] = platamps
fig1 = ba.plot_measure(expdata_platamps, expdata_params, title=None, measlabel=None, param_labels=None, legend_label="Exp Data")

expdata_platdurs = {}
expdata_platdurs['label'] = 'Plateau Duration (ms)'
expdata_platdurs['values'] = platdurs 
fig2 = ba.plot_measure(expdata_platdurs, expdata_params, title=None, measlabel=None, param_labels=None, legend_label="Exp Data")

expdata_numspikes = {}
expdata_numspikes['label'] = 'Number of Spikes'
expdata_numspikes['values'] = numspikes 
fig3 = ba.plot_measure(expdata_numspikes, expdata_params, title=None, measlabel=None, param_labels=None, legend_label="Exp Data")

expdata_spikefreq = {}
expdata_spikefreq['label'] = 'Spike Frequency (Hz)'
expdata_spikefreq['values'] = spikefreqs 
fig4 = ba.plot_measure(expdata_spikefreq, expdata_params, title=None, measlabel=None, param_labels=None, legend_label="Exp Data")

expdata_timetospike = {}
expdata_timetospike['label'] = 'Time to first spike (ms)'
expdata_timetospike['values'] = timetospikes 
fig5 = ba.plot_measure(expdata_timetospike, expdata_params, title=None, measlabel=None, param_labels=None, legend_label="Exp Data")

expdata_interspike = {}
expdata_interspike['label'] = 'First interspike interval (ms)'
expdata_interspike['values'] = interspikes 
fig6 = ba.plot_measure(expdata_interspike, expdata_params, title=None, measlabel=None, param_labels=None, legend_label="Exp Data")

