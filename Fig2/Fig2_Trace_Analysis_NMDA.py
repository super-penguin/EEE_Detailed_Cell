"""
The analysis functions for EEE stimulation data.

Author: Peng (Penny) Gao
penggao.1987@gmail.com
"""

import json
import matplotlib.pyplot as plt
from pprint import pprint
import os
import numpy as np
import pandas as pd
from analysis_utils import *
from analysis_utils import tableau
from utils import *
import seaborn as sns



# Need to organize all the analysis and plotting here
######################################################
new_data = pd.DataFrame(columns = ['AMPA_num', 'AMPA_locs', 'AMPA_weight',
'NMDA_num', 'NMDA_locs', 'NMDA_weight', 'NMDA_Beta', 'NMDA_Cdur',
'spike_num','platamp', 'ISI', 'platdur'])

# Need to check the name of data folder
# Replace this step with a function
# Add the correct path here:
path_to_json = 'Data_04_25/'
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
        spike_num = spike_count(data['recording']['soma']['voltage'])
        ISI, platamp = meas_platamp(data['recording']['soma']['voltage'])
        platdur = meas_platdur(data['recording']['soma']['voltage'])
        # For TTX
        # platamp = TTX_platamp(data['recording']['soma']['voltage'])
        # ISI = 0
        new_data.loc[index] = [AMPA_num, AMPA_locs, AMPA_weight,
        NMDA_num, NMDA_locs, NMDA_weight, NMDA_Beta, NMDA_Cdur,
        spike_num, platamp, ISI, platdur]


print("--- %s seconds ---" % (time.time() - start_time))
new_data = new_data.sort_values(by = ['NMDA_weight'])
# print new_data
# Add the correct saving path here:
savepath = path_to_json + '/NMDA_total_results.csv'
new_data.to_csv(savepath)

# ##### Plotting

path1 = savepath
# path2 = 'srdjan_data/total_results.csv'
df1 = pd.read_csv(path1, index_col = 0)
# df2 = pd.read_csv(path2, index_col = 0)

######## Load both exp and simulation data
df1 = df1.sort_values(by = ['NMDA_weight'])
# df2 = df2.sort_values(by = ['Glu'])

df11 = df1[df1['spike_num'] == 0]
df12 = df1[df1['spike_num'] != 0]

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
ax.yaxis.set_ticks_position('left')
ax.xaxis.set_ticks_position('bottom')
ax.scatter(df11['NMDA_weight'], df11['platamp'], s = 200, marker = 'o',
c = tableau(0), edgecolors = tableau(14), linewidth = 2, alpha = 0.5)
ax.scatter(df12['NMDA_weight'], df12['platamp'], s = 200, marker = 'o',
c = tableau(4), edgecolors = tableau(14), linewidth = 2,alpha = 0.5)
plt.xlim([0.0, 1.0])
plt.xlabel("Syanptic Input Weights", size = 22, color = "black")
plt.ylabel("Plateau Amplitude (mV)", size = 22, color = "black")
plt.tick_params(labelsize=22, pad = 12, colors = "black")
plt.xticks([])
# plt.title("Plateau Amplitude vs. Glutmate Stimulation", size = 20)
plt.ylim([-1, 25])
# ax.grid(False)
ax.set_axis_bgcolor('white')
title1 = "Platamp"
save(title1, path_to_json, ext="ps", close=False, verbose=True)
save(title1, path_to_json, ext="png", close=True, verbose=True)


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
# ax.spines['bottom'].set_visible(False)
ax.yaxis.set_ticks_position('left')
ax.xaxis.set_ticks_position('bottom')
ax.scatter(df1['NMDA_weight'], df1['platamp'], s = 200, marker = 'o',
c = 'white', edgecolors = tableau(6), linewidth = 2, alpha = 1)
# ax.scatter(df12['NMDA_weight'], df12['platamp'], s = 200, marker = 'o',
# c = tableau(4), edgecolors = tableau(14), linewidth = 2,alpha = 0.5)
plt.xlim([0.0, 1.0])
plt.xlabel("Syanptic Input Weights", size = 22, color = "black")
plt.ylabel("Plateau Amplitude (mV)", size = 22, color = "black")
plt.tick_params(labelsize=22, pad = 12, colors = "black")
# plt.xticks([])
# plt.title("Plateau Amplitude vs. Glutmate Stimulation", size = 20)
plt.ylim([-1, 22])
# ax.grid(False)
ax.set_axis_bgcolor('white')
title2 = "Platamp_v2"
save(title2, path_to_json, ext="ps", close=False, verbose=True)
save(title2, path_to_json, ext="png", close=True, verbose=True)
############### Experimental results
# plt.close()
# plt.clf()
# plt.figure(figsize = (9,6), dpi = 100)
# plt.subplots_adjust(left=0.15, right=0.9, top=0.85, bottom=0.15)
# ax = plt.gca()
# ax.spines['right'].set_visible(False)
# ax.spines['top'].set_visible(False)
# ax.yaxis.set_ticks_position('left')
# ax.xaxis.set_ticks_position('bottom')
# ax.scatter(df2['Glu'], df2['platamp'], s = 200, marker = '<',
# c = 'white', edgecolors = tableau(20), linewidth = 2, alpha = 1)
# plt.xlim([-1, 11])
# plt.xlabel("Glutmate Stimulations", size = 22)
# plt.ylabel("Plateau Amplitude (mV)", size = 22)
# plt.tick_params(labelsize=22, pad = 12)
# plt.xticks([])
# # plt.title("Plateau Amplitude vs. Glutmate Stimulation", size = 20)
# plt.ylim([-1, 30])
# # ax.grid(False)
# ax.set_axis_bgcolor('white')
# plt.savefig("srdjan_data/Exp_Platamp_v2.png")


# Plateau duration
#########################################################################
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
# ax.spines['bottom'].set_visible(False)
ax.yaxis.set_ticks_position('left')
ax.xaxis.set_ticks_position('bottom')
ax.scatter(df1['NMDA_weight'], df1['platdur'], s = 200, marker = 'o',
c = 'white', edgecolors = tableau(6), linewidth = 2, alpha = 1)
# ax.scatter(df12['NMDA_weight'], df12['platamp'], s = 200, marker = 'o',
# c = tableau(4), edgecolors = tableau(14), linewidth = 2,alpha = 0.5)
plt.xlim([0.0, 1.0])
plt.xlabel("Syanptic Input Weights", size = 22, color = "black")
plt.ylabel("Plateau Duration (ms)", size = 22, color = "black")
plt.tick_params(labelsize=22, pad = 12, colors = "black")
# plt.xticks([])
# plt.title("Plateau Amplitude vs. Glutmate Stimulation", size = 20)
plt.ylim([-10, 320])
# ax.grid(False)
ax.set_axis_bgcolor('white')
title3 = "Platdur"
save(title3, path_to_json, ext="ps", close=False, verbose=True)
save(title3, path_to_json, ext="png", close=True, verbose=True)
############### Experimental results
# plt.close()
# plt.clf()
# plt.figure(figsize = (9,6), dpi = 100)
# plt.subplots_adjust(left=0.15, right=0.9, top=0.85, bottom=0.15)
# ax = plt.gca()
# ax.spines['right'].set_visible(False)
# ax.spines['top'].set_visible(False)
# ax.yaxis.set_ticks_position('left')
# ax.xaxis.set_ticks_position('bottom')
# ax.scatter(df2['Glu'], df2['platdur'], s = 200, marker = '<',
# c = 'white', edgecolors = tableau(20), linewidth = 2, alpha = 1)
# plt.xlim([-1, 11])
# plt.xlabel("Glutmate Stimulations", size = 22)
# plt.ylabel("Plateau Duration (ms)", size = 22)
# plt.tick_params(labelsize=22, pad = 12)
# plt.xticks([])
# # plt.title("Plateau Amplitude vs. Glutmate Stimulation", size = 20)
# plt.ylim([-10, 300])
# # ax.grid(False)
# ax.set_axis_bgcolor('white')
# plt.savefig("srdjan_data/Exp_Platdur.png")


# Spike Number
#########################################################################
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
# ax.spines['bottom'].set_visible(False)
ax.yaxis.set_ticks_position('left')
ax.xaxis.set_ticks_position('bottom')
ax.scatter(df1['NMDA_weight'], df1['spike_num'], s = 200, marker = 'o',
c = 'white', edgecolors = tableau(6), linewidth = 2, alpha = 1)
# ax.scatter(df12['NMDA_weight'], df12['platamp'], s = 200, marker = 'o',
# c = tableau(4), edgecolors = tableau(14), linewidth = 2,alpha = 0.5)
plt.xlim([0.0, 1.0])
plt.xlabel("Syanptic Input Weights", size = 22, color = "black")
plt.ylabel("Spike Numbers", size = 22, color = "black")
plt.tick_params(labelsize=22, pad = 12, colors = "black")
# plt.xticks([])
# plt.title("Plateau Amplitude vs. Glutmate Stimulation", size = 20)
plt.ylim([-0.5, 10])
# ax.grid(False)
ax.set_axis_bgcolor('white')
title4 = "Spike_num"
save(title4, path_to_json, ext="ps", close=False, verbose=True)
save(title4, path_to_json, ext="png", close=True, verbose=True)
############### Experimental results
# plt.close()
# plt.clf()
# plt.figure(figsize = (9,6), dpi = 100)
# plt.subplots_adjust(left=0.15, right=0.9, top=0.85, bottom=0.15)
# ax = plt.gca()
# ax.spines['right'].set_visible(False)
# ax.spines['top'].set_visible(False)
# ax.yaxis.set_ticks_position('left')
# ax.xaxis.set_ticks_position('bottom')
# ax.scatter(df2['Glu'], df2['spike_num'], s = 200, marker = '<',
# c = 'white', edgecolors = tableau(20), linewidth = 2, alpha = 1)
# plt.xlim([-1, 11])
# plt.xlabel("Glutmate Stimulations", size = 22)
# plt.ylabel("Spike Numbers", size = 22)
# plt.tick_params(labelsize=22, pad = 12)
# plt.xticks([])
# # plt.title("Plateau Amplitude vs. Glutmate Stimulation", size = 20)
# plt.ylim([-0.5, 10])
# # ax.grid(False)
# ax.set_axis_bgcolor('white')
# plt.savefig("srdjan_data/Exp_Spikes.png")
