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

# Loading data from NMDA, NMDAeee and major
df1 = pd.read_csv("Data_04_25/NMDA_total_results.csv", index_col = 0)
df2 = pd.read_csv("Data_04_25/eee_total_results.csv", index_col = 0)
df3 = pd.read_csv("Data_04_25/Major_total_results.csv", index_col = 0)
df1 = df1.sort_values(by = ['AMPA_weight'])
df2 = df2.sort_values(by = ['AMPA_weight'])
df3 = df3.sort_values(by = ['AMPA_weight'])

path_to_json = "Data_04_25/"
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
# ax.scatter(df1['AMPA_weight'], df1['platamp'], s = 200, marker = '<',
# c = 'white', edgecolors = tableau(20), linewidth = 2, alpha = 1, label ='NMDA.mod')
# ax.scatter(df2['AMPA_weight'], df2['platamp'], s = 200, marker = 'o',
# c = 'white', edgecolors = tableau(0), linewidth = 2, alpha = 1, label = "NMDAeee.mod")
# ax.scatter(df3['AMPA_weight'], df3['platamp'], s = 200, marker = '>',
# c = 'white', edgecolors = tableau(6), linewidth = 2, alpha = 1, label = "NMDAmajor.mod")linestyle
plt.plot(df1['AMPA_weight'], df1['platamp'], '--o', color = tableau(20), linewidth = 2, markersize = 10, label ='NMDA.mod')
plt.plot(df2['AMPA_weight'], df2['platamp'], '--^', color = tableau(0), linewidth = 2, markersize = 10, label ='NMDAeee.mod')
plt.plot(df3['AMPA_weight'], df3['platamp'], '--D', color = tableau(6), linewidth = 2, markersize = 10, label ='NMDAmajor.mod')
plt.xlim([0.0, 1.0])
plt.xlabel("Syanptic Input Weights", size = 22, color = "black")
plt.ylabel("Plateau Amplitude (mV)", size = 22, color = "black")
plt.tick_params(labelsize=22, pad = 12, colors = "black")
# plt.xticks([])
# plt.title("Plateau Amplitude vs. Glutmate Stimulation", size = 20)
plt.ylim([-1, 22])
# ax.grid(False)
plt.legend(loc = 'best', fontsize = 22)
ax.set_axis_bgcolor('white')
title2 = "Platamp_compare_all"
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
plt.plot(df1['AMPA_weight'], df1['platdur'], '--o', color = tableau(20), linewidth = 2, markersize = 10, label ='NMDA.mod')
plt.plot(df2['AMPA_weight'], df2['platdur'], '--^', color = tableau(0), linewidth = 2, markersize = 10, label ='NMDAeee.mod')
plt.plot(df3['AMPA_weight'], df3['platdur'], '--D', color = tableau(6), linewidth = 2, markersize = 10, label ='NMDAmajor.mod')
plt.xlim([0.0, 1.0])
plt.legend(loc = 'best', fontsize = 22)
plt.xlabel("Syanptic Input Weights", size = 22, color = "black")
plt.ylabel("Plateau Duration (ms)", size = 22, color = "black")
plt.tick_params(labelsize=22, pad = 12, colors = "black")
# plt.xticks([])
# plt.title("Plateau Amplitude vs. Glutmate Stimulation", size = 20)
plt.ylim([-10, 350])
# ax.grid(False)
ax.set_axis_bgcolor('white')
title3 = "Platdur_compare_all"
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
plt.plot(df1['AMPA_weight'], df1['spike_num'], '--o', color = tableau(20), linewidth = 2, markersize = 10, label ='NMDA.mod')
plt.plot(df2['AMPA_weight'], df2['spike_num'], '--^', color = tableau(0), linewidth = 2, markersize = 10, label ='NMDAeee.mod')
plt.plot(df3['AMPA_weight'], df3['spike_num'], '--D', color = tableau(6), linewidth = 2, markersize = 10, label ='NMDAmajor.mod')
plt.xlim([0.0, 1.0])
plt.xlabel("Syanptic Input Weights", size = 22, color = "black")
plt.ylabel("Spike Numbers", size = 22, color = "black")
plt.tick_params(labelsize=22, pad = 12, colors = "black")
plt.legend(loc = 'best', fontsize = 22)
# plt.xticks([])
# plt.title("Plateau Amplitude vs. Glutmate Stimulation", size = 20)
plt.ylim([-0.5, 11])
# ax.grid(False)
ax.set_axis_bgcolor('white')
title4 = "Spike_num_compare_all"
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

# ISI
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
plt.plot(df1['AMPA_weight'], df1['ISI'], '--o', color = tableau(20), linewidth = 2, markersize = 10, label ='NMDA.mod')
plt.plot(df2['AMPA_weight'], df2['ISI'], '--^', color = tableau(0), linewidth = 2, markersize = 10, label ='NMDAeee.mod')
plt.plot(df3['AMPA_weight'], df3['ISI'], '--D', color = tableau(6), linewidth = 2, markersize = 10, label ='NMDAmajor.mod')
plt.xlim([0.0, 1.0])
plt.xlabel("Syanptic Input Weights", size = 22, color = "black")
plt.ylabel("Interspike Interval (ms)", size = 22, color = "black")
plt.tick_params(labelsize=22, pad = 12, colors = "black")
plt.legend(loc = 'best', fontsize = 22)
# plt.xticks([])
# plt.title("Plateau Amplitude vs. Glutmate Stimulation", size = 20)
plt.ylim([-0.5, 45])
# ax.grid(False)
ax.set_axis_bgcolor('white')
title5 = "ISI_compare_all"
save(title5, path_to_json, ext="ps", close=False, verbose=True)
save(title5, path_to_json, ext="png", close=True, verbose=True)
