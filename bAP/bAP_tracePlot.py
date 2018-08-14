"""
The analysis for AP Backpropagation
Plot the control, TTX, 4-AP traces side by side in soma and dendrite

Author: Peng (Penny) Gao
penggao.1987@gmail.com
"""
import sys
sys.path.append("..")
import json
import matplotlib.pyplot as plt
import os
import numpy as np
import pandas as pd
from analysis_utils import *
from utils import *
import seaborn as sns
import itertools

######################################################
path_to_json = 'bAP_traces/'
# start_time = time.time()
json_files = [pos_json for pos_json in os.listdir(path_to_json) if pos_json.endswith('.json')]
for index, js in enumerate(json_files):
    with open(os.path.join(path_to_json, js)) as json_file:
        data = json.load(json_file)
        if 'TTX' in js:
            condition = 'TTX'
            soma_TTX = data['recording']['soma']['voltage']
            dend_TTX = data['recording']['dend']['voltage']

        elif '4AP' in js:
            condition = '4AP'
            soma_4AP = data['recording']['soma']['voltage']
            dend_4AP = data['recording']['dend']['voltage']

        else:
            condition = 'Control'
            soma_con = data['recording']['soma']['voltage']
            dend_con = data['recording']['dend']['voltage']
        time = data['recording']['time']
        dist = data['dist']

print dist
time_TTX = [x + 10 for x in time]
time_4AP = [x + 20 for x in time]
##### Plotting
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
ax.plot(time, soma_con, color = tableau(20), linewidth = 2, label = 'Best Fit')
ax.plot(time_TTX, soma_TTX, color = tableau(6), linewidth = 2, label = 'Na Blocked')
ax.plot(time_4AP, soma_4AP, color = tableau(4), linewidth = 2, label = 'KA Blocked')
plt.xlabel("Time (ms)", size = 22, color = "black")
plt.ylabel("Voltage (mV)", size = 22, color = "black")
plt.tick_params(labelsize=22, pad = 12, colors = "black")
# plt.xticks([])
plt.xlim([140, 200])
plt.ylim([-80, 40])
# ax.grid(False)
ax.set_axis_bgcolor('white')
title1 = "AP_soma"
save(title1, path_to_json, ext="pdf", close=False, verbose=True)
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
ax.yaxis.set_ticks_position('left')
ax.xaxis.set_ticks_position('bottom')
ax.plot(time, dend_con, color = tableau(20), linewidth = 2, label = 'Best Fit')
ax.plot(time_TTX, dend_TTX, color = tableau(6), linewidth = 2, label = 'Na Blocked')
ax.plot(time_4AP, dend_4AP, color = tableau(4), linewidth = 2, label = 'KA Blocked')
plt.xlabel("Time (ms)", size = 22, color = "black")
plt.ylabel("Voltage (mV)", size = 22, color = "black")
plt.tick_params(labelsize=22, pad = 12, colors = "black")
# plt.xticks([])
plt.xlim([140, 200])
plt.ylim([-80, 40])
# ax.grid(False)
ax.set_axis_bgcolor('white')
title2 = "AP_dend"
save(title2, path_to_json, ext="pdf", close=False, verbose=True)
save(title2, path_to_json, ext="png", close=True, verbose=True)
