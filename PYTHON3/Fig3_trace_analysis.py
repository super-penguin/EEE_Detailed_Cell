"""
The analysis functions for EEE stimulation data.
Analyze the somatic voltage traces of both Model 1 and Model 2

Generate final plots to compare the plateau amplitude, plateau duration
and spikes per plateau in Model 1 with Model 2.

Author: Peng (Penny) Gao
penggao.1987@gmail.com
"""

import json
import matplotlib.pyplot as plt
from pprint import pprint
import os
import numpy as np
import pandas as pd
import analysis_utils as ana
#from analysis_utils import *
from analysis_utils import tableau
import utils as ut #from utils import *
import seaborn as sns
import time

######################################################
# Analysis for Model 1
DMS_data = pd.DataFrame(columns = ['AMPA_num', 'AMPA_locs', 'AMPA_weight',
'NMDA_num', 'NMDA_locs', 'NMDA_weight', 'NMDA_Beta', 'NMDA_Cdur',
'spike_num','platamp', 'ISI', 'platdur'])

path_to_json = 'Fig3/DMS/Analysis/'
start_time = time.time()
json_files = [pos_json for pos_json in os.listdir(path_to_json) if pos_json.endswith('.json')]

for index, js in enumerate(json_files):
    with open(os.path.join(path_to_json, js)) as json_file:
        data = json.load(json_file)
        filename = json_files[index]
        AMPA_num = data['SynAMPA']['num']
        AMPA_locs = data['SynAMPA']['locs']
        AMPA_weight = data['SynAMPA']['weight']
        NMDA_num = data['SynNMDA']['num']
        NMDA_locs = data['SynNMDA']['locs']
        NMDA_weight = data['SynNMDA']['weight']
        NMDA_Beta = data['SynNMDA']['Beta']
        NMDA_Cdur = data['SynNMDA']['Cdur']
        spike_num = ana.spike_count(data['recording']['soma']['voltage'])
        ISI, platamp = ana.meas_platamp(data['recording']['soma']['voltage'])
        platdur = ana.meas_platdur(data['recording']['soma']['voltage'])
        # For TTX
        # platamp = TTX_platamp(data['recording']['soma']['voltage'])
        # ISI = 0
        DMS_data.loc[index] = [AMPA_num, AMPA_locs, AMPA_weight,
        NMDA_num, NMDA_locs, NMDA_weight, NMDA_Beta, NMDA_Cdur,
        spike_num, platamp, ISI, platdur]

print("--- %s seconds ---" % (time.time() - start_time))
DMS_data = DMS_data.sort_values(by = ['NMDA_weight'])
# Add the correct saving path here:
savepath = path_to_json + '/total_results.csv'
DMS_data.to_csv(savepath)

######################################################
# Analysis for Model2
Major_data = pd.DataFrame(columns = ['AMPA_num', 'AMPA_locs', 'AMPA_weight',
'NMDA_num', 'NMDA_locs', 'NMDA_weight',
'spike_num','platamp', 'ISI', 'platdur'])

path_to_json = 'Fig3/Major/Analysis/'
start_time = time.time()
json_files = [pos_json for pos_json in os.listdir(path_to_json) if pos_json.endswith('.json')]

for index, js in enumerate(json_files):
    with open(os.path.join(path_to_json, js)) as json_file:
        data = json.load(json_file)
        filename = json_files[index]
        AMPA_num = data['SynAMPA']['num']
        AMPA_locs = data['SynAMPA']['locs']
        AMPA_weight = data['SynAMPA']['weight']
        NMDA_num = data['SynNMDA']['num']
        NMDA_locs = data['SynNMDA']['locs']
        NMDA_weight = data['SynNMDA']['weight']
        # NMDA_Beta = data['SynNMDA']['Beta']
        # NMDA_Cdur = data['SynNMDA']['Cdur']
        spike_num = ana.spike_count(data['recording']['soma']['voltage'])
        ISI, platamp = ana.meas_platamp(data['recording']['soma']['voltage'])
        platdur = ana.meas_platdur(data['recording']['soma']['voltage'])
        # For TTX
        # platamp = TTX_platamp(data['recording']['soma']['voltage'])
        # ISI = 0
        Major_data.loc[index] = [AMPA_num, AMPA_locs, AMPA_weight,
        NMDA_num, NMDA_locs, NMDA_weight,
        spike_num, platamp, ISI, platdur]

print("--- %s seconds ---" % (time.time() - start_time))
Major_data = Major_data.sort_values(by = ['NMDA_weight'])
# Add the correct saving path here:
savepath = path_to_json + '/total_results.csv'
Major_data.to_csv(savepath)


# ##### Plotting
File1 = 'Fig3/DMS/Analysis/total_results.csv'
File2 = 'Fig3/Major/Analysis/total_results.csv'

df1 = pd.read_csv(File1, index_col = 0)
df2 = pd.read_csv(File2, index_col = 0)

savepath = 'Fig3/'
plt.close()
plt.clf()
plt.figure(figsize = (9,6), dpi = 100)
plt.subplots_adjust(left=0.15, right=0.9, top=0.85, bottom=0.15)
ax = plt.gca()
plt.style.use("ggplot")
plt.rcParams['axes.edgecolor'] = "black"
plt.rcParams['axes.facecolor'] = "white"
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)
ax.grid(False)
# ax.spines['bottom'].set_visible(False)
ax.yaxis.set_ticks_position('left')
ax.xaxis.set_ticks_position('bottom')
plt.plot(df1['NMDA_weight'], df1['platamp'],linestyle = '--', marker = 'o',
markersize = 15, c = tableau(20), linewidth = 2, label = 'Model 1')
plt.plot(df2['NMDA_weight'], df2['platamp'],linestyle = '-', marker = '^',
markersize = 15, c = tableau(14), linewidth = 2, label = 'Model 2')
plt.xlabel("NMDA weight", size = 22, color = 'black')
plt.ylabel("Plateau Amp (mV)", size = 22, color = 'black')
ax.tick_params(labelsize=22, pad = 12, colors = "black")
ax.set_facecolor('white')
plt.xlim([0,1])
plt.ylim([0,25])
ax.set_facecolor('white')
plt.legend(loc = 'best', fontsize = 22)
title = "Platamp_Model_B&W"
# save(title, savepath, ext="pdf", close=False, verbose=True)
ut.save(title, savepath, ext="png", close=True, verbose=True)
###################################################
plt.close()
plt.clf()
plt.figure(figsize = (9,6), dpi = 100)
plt.subplots_adjust(left=0.15, right=0.9, top=0.85, bottom=0.15)
ax = plt.gca()
plt.style.use("ggplot")
plt.rcParams['axes.edgecolor'] = "black"
plt.rcParams['axes.facecolor'] = "white"
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)
ax.grid(False)
# ax.spines['bottom'].set_visible(False)
ax.yaxis.set_ticks_position('left')
ax.xaxis.set_ticks_position('bottom')
plt.plot(df1['NMDA_weight'], df1['platdur'],linestyle = '--', marker = 'o',
markersize = 15, c = tableau(20), linewidth = 2, label = 'Model 1')
plt.plot(df2['NMDA_weight'], df2['platdur'],linestyle = '-', marker = '^',
markersize = 15, c = tableau(14), linewidth = 2, label = 'Model 2')
plt.xlabel("NMDA weight", size = 22, color = 'black')
plt.ylabel("Plateau Duration (ms)", size = 22, color = 'black')
ax.tick_params(labelsize=22, pad = 12, colors = "black")
ax.set_facecolor('white')
plt.xlim([0,1])
plt.ylim([-10,330])
ax.set_facecolor('white')
plt.legend(loc = 'best', fontsize = 22)
title = "Platdur_Model_B&W"
# save(title, savepath, ext="pdf", close=False, verbose=True)
ut.save(title, savepath, ext="png", close=True, verbose=True)

###################################################
plt.close()
plt.clf()
plt.figure(figsize = (9,6), dpi = 100)
plt.subplots_adjust(left=0.15, right=0.9, top=0.85, bottom=0.15)
ax = plt.gca()
plt.style.use("ggplot")
plt.rcParams['axes.edgecolor'] = "black"
plt.rcParams['axes.facecolor'] = "white"
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)
ax.grid(False)
# ax.spines['bottom'].set_visible(False)
ax.yaxis.set_ticks_position('left')
ax.xaxis.set_ticks_position('bottom')
plt.plot(df1['NMDA_weight'], df1['spike_num'],linestyle = '--', marker = 'o',
markersize = 15, c = tableau(20), linewidth = 2, label = 'Model 1')
plt.plot(df2['NMDA_weight'], df2['spike_num'],linestyle = '-', marker = '^',
markersize = 15, c = tableau(14), linewidth = 2, label = 'Model 2')
plt.xlabel("NMDA weight", size = 22, color = 'black')
plt.ylabel("Spike Numbers", size = 22, color = 'black')
ax.tick_params(labelsize=22, pad = 12, colors = "black")
ax.set_facecolor('white')
plt.xlim([0,1])
plt.ylim([-0.5,11.5])
plt.legend(loc = 'best', fontsize = 22)
ax.set_facecolor('white')
title = "SpikeNum_Model_B&W"
# save(title, savepath, ext="pdf", close=False, verbose=True)
ut.save(title, savepath, ext="png", close=True, verbose=True)
