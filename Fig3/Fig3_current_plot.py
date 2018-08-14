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


###### Load DATA
## Add the correct analysis path here:
path_to_json = 'Data_05_08/'
json_files = [pos_json for pos_json in os.listdir(path_to_json) if pos_json.endswith('.json')]
nfile = len(json_files)

df = pd.DataFrame(columns = ['soma_trace','dend1_trace','dend2_trace','dend3_trace','labels'])

for index, js in enumerate(json_files):
    with open(os.path.join(path_to_json, js)) as json_file:
        data = json.load(json_file)
        filename = json_files[index]
        time = data['recording']['time'][4000:]
        new_time = [x-100.0 for x in time]
        soma_trace = data['recording']['soma']['voltage'][4000:]
        dend1_trace = data['recording']['basal']['voltage_0.8'][4000:]
        dend2_trace = data['recording']['basal']['voltage_0.5'][4000:]
        dend3_trace = data['recording']['basal']['voltage_0.3'][4000:]
        labels = data['Loc']
        df.loc[index] = [soma_trace, dend1_trace, dend2_trace, dend3_trace, labels]

df = df.sort_values(by = ['labels'])

###############################################################
##### Overlay trace plot - soma
###############################################################
plt.close()
plt.clf()
plt.figure(figsize = (9, 6), dpi = 100)
for i in range(nfile-1):
    plt.plot(new_time, df['soma_trace'].iloc[i+1], color = tableau(i+1), label = 'Input w = ' + str('%.2f' % df['labels'].iloc[i+1]), linewidth = 2)
plt.xlim([0, 600])
plt.ylabel("mV", fontsize = 25)
plt.xlabel("Time(ms)", fontsize = 25)
plt.xticks(fontsize = 20)
plt.yticks(fontsize = 20)
plt.gca().grid(False)
plt.gca().set_axis_bgcolor('white')
save("Simulated_Trace", path_to_json, ext="ps", close=False, verbose=True)
save("Simulated_Trace", path_to_json, ext="png", close=True, verbose=True)
###############################################################
##### Overlay trace plot - dend0.3
###############################################################
plt.close()
plt.clf()
plt.figure(figsize = (9, 6), dpi = 100)
for i in range(nfile-1):
    plt.plot(new_time, df['dend3_trace'].iloc[i+1], color = tableau(i+1), label = 'Input w = ' + str('%.2f' % df['labels'].iloc[i+1]), linewidth = 2)
plt.xlim([0, 600])
plt.ylabel("mV", fontsize = 25)
plt.xlabel("Time(ms)", fontsize = 25)
plt.xticks(fontsize = 20)
plt.yticks(fontsize = 20)
plt.gca().grid(False)
plt.gca().set_axis_bgcolor('white')
save("Dend_0.3", path_to_json, ext="ps", close=False, verbose=True)
save("Dend_0.3", path_to_json, ext="png", close=True, verbose=True)
###############################################################
##### Overlay trace plot - dend0.5
###############################################################
plt.close()
plt.clf()
plt.figure(figsize = (9, 6), dpi = 100)
for i in range(nfile-1):
    plt.plot(new_time, df['dend2_trace'].iloc[i+1], color = tableau(i+1), label = 'Input w = ' + str('%.2f' % df['labels'].iloc[i+1]), linewidth = 2)
plt.xlim([0, 600])
plt.ylabel("mV", fontsize = 25)
plt.xlabel("Time(ms)", fontsize = 25)
plt.xticks(fontsize = 20)
plt.yticks(fontsize = 20)
plt.gca().grid(False)
plt.gca().set_axis_bgcolor('white')
save("Dend_0.5", path_to_json, ext="ps", close=False, verbose=True)
save("Dend_0.5", path_to_json, ext="png", close=True, verbose=True)
###############################################################
##### Overlay trace plot - dend0.8
###############################################################
plt.close()
plt.clf()
plt.figure(figsize = (9, 6), dpi = 100)
for i in range(nfile-1):
    plt.plot(new_time, df['dend1_trace'].iloc[i+1], color = tableau(i+1), label = 'Input w = ' + str('%.2f' % df['labels'].iloc[i+1]), linewidth = 2)
plt.xlim([0, 600])
plt.ylabel("mV", fontsize = 25)
plt.xlabel("Time(ms)", fontsize = 25)
plt.xticks(fontsize = 20)
plt.yticks(fontsize = 20)
plt.gca().grid(False)
plt.gca().set_axis_bgcolor('white')
save("Dend_0.8", path_to_json, ext="ps", close=False, verbose=True)
save("Dend_0.8", path_to_json, ext="png", close=True, verbose=True)
###############################################################
##### Shiftted plot
###############################################################
plt.close()
plt.clf()
plt.figure(figsize = (9,6), dpi = 300)
plt.subplots_adjust(left=0.15, right=0.9, top=0.85, bottom=0.15)
ax = plt.gca()
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)
ax.yaxis.set_ticks_position('left')
ax.xaxis.set_ticks_position('bottom')



new_soma_trace = []
for i in range(nfile-1):
    time1 = [x+330*i for x in new_time]
    new_soma_trace.append([x+20*i for x in df['soma_trace'].iloc[i+1]])
    plt.plot(time1, new_soma_trace[i], color = tableau(i+1), label = 'Input w = ' + str('%.2f' % df['labels'].iloc[i+1]), linewidth = 2)
    # plt.legend(loc = 'best', fontsize = 15)
    plt.title("Voltage Traces at Soma \n", fontsize = 25)
    plt.ylim([-80, 200])
    # plt.ylabel('mV', fontsize = 23)
    plt.yticks(fontsize=23)
    plt.xlim([50, 3500])
    #plt.xlabel('Time (ms)', fontsize = 15)
    # plt.xticks([])
    # plt.yticks([])
    plt.gca().yaxis.grid(False)
    plt.gca().set_axis_bgcolor('white')
    #plt.gca().axes.get_xaxis().set_visible(False)
    #plt.gca().axes.get_yaxis().set_visible(False)
    plt.xlabel('Time (ms)', fontsize = 23)

title1 = "Soma_shift"
save(title1, path_to_json, ext="png", close=False, verbose=True)
save(title1, path_to_json, ext="ps", close=True, verbose=True)

############## Dend0.8
plt.close()
plt.clf()
plt.figure(figsize = (9,6), dpi = 300)
plt.subplots_adjust(left=0.15, right=0.9, top=0.85, bottom=0.15)
ax = plt.gca()
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)
ax.yaxis.set_ticks_position('left')
ax.xaxis.set_ticks_position('bottom')

new_dend1_trace = []
for i in range(nfile-1):
    time1 = [x+330*i for x in new_time]
    new_dend1_trace.append([x+20*i for x in df['dend1_trace'].iloc[i+1]])
    plt.plot(time1, new_dend1_trace[i], color = tableau(i+1), label = 'Input w = ' + str('%.2f' % df['labels'].iloc[i+1]), linewidth = 2)
    # plt.legend(loc = 'best', fontsize = 15)
    plt.title("Voltage Traces at Basal Dendrite (loc:0.8) \n", fontsize = 25)
    plt.ylim([-80, 200])
    # plt.ylabel('mV', fontsize = 23)
    plt.yticks(fontsize=23)
    plt.xlim([50, 3500])
    #plt.xlabel('Time (ms)', fontsize = 15)
    # plt.xticks([])
    # plt.yticks([])
    plt.gca().yaxis.grid(False)
    plt.gca().set_axis_bgcolor('white')
    #plt.gca().axes.get_xaxis().set_visible(False)
    #plt.gca().axes.get_yaxis().set_visible(False)
    plt.xlabel('Time (ms)', fontsize = 23)

title2 = "Dend0.8_shift"
save(title2, path_to_json, ext="png", close=False, verbose=True)
save(title2, path_to_json, ext="ps", close=True, verbose=True)

############## Dend0.5
plt.close()
plt.clf()
plt.figure(figsize = (9,6), dpi = 300)
plt.subplots_adjust(left=0.15, right=0.9, top=0.85, bottom=0.15)
ax = plt.gca()
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)
ax.yaxis.set_ticks_position('left')
ax.xaxis.set_ticks_position('bottom')

new_dend2_trace = []
for i in range(nfile-1):
    time1 = [x+330*i for x in new_time]
    new_dend2_trace.append([x+20*i for x in df['dend2_trace'].iloc[i+1]])
    plt.plot(time1, new_dend2_trace[i], color = tableau(i+1), label = 'Input w = ' + str('%.2f' % df['labels'].iloc[i+1]), linewidth = 2)
    # plt.legend(loc = 'best', fontsize = 15)
    plt.title("Voltage Traces at Basal Dendrite (loc:0.5) \n", fontsize = 25)
    plt.ylim([-80, 200])
    # plt.ylabel('mV', fontsize = 23)
    plt.yticks(fontsize=23)
    plt.xlim([50, 3500])
    #plt.xlabel('Time (ms)', fontsize = 15)
    # plt.xticks([])
    # plt.yticks([])
    plt.gca().yaxis.grid(False)
    plt.gca().set_axis_bgcolor('white')
    #plt.gca().axes.get_xaxis().set_visible(False)
    #plt.gca().axes.get_yaxis().set_visible(False)
    plt.xlabel('Time (ms)', fontsize = 23)

title3 = "Dend0.5_shift"
save(title3, path_to_json, ext="png", close=False, verbose=True)
save(title3, path_to_json, ext="ps", close=True, verbose=True)

############## Dend0.3
plt.close()
plt.clf()
plt.figure(figsize = (9,6), dpi = 300)
plt.subplots_adjust(left=0.15, right=0.9, top=0.85, bottom=0.15)
ax = plt.gca()
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)
ax.yaxis.set_ticks_position('left')
ax.xaxis.set_ticks_position('bottom')

new_dend3_trace = []
for i in range(nfile-1):
    time1 = [x+330*i for x in new_time]
    new_dend3_trace.append([x+20*i for x in df['dend3_trace'].iloc[i+1]])
    plt.plot(time1, new_dend3_trace[i], color = tableau(i+1), label = 'Input w = ' + str('%.2f' % df['labels'].iloc[i+1]), linewidth = 2)
    # plt.legend(loc = 'best', fontsize = 15)
    plt.title("Voltage Traces at Basal Dendrite (loc:0.5) \n", fontsize = 25)
    plt.ylim([-80, 200])
    # plt.ylabel('mV', fontsize = 23)
    plt.yticks(fontsize=23)
    plt.xlim([50, 3500])
    #plt.xlabel('Time (ms)', fontsize = 15)
    # plt.xticks([])
    # plt.yticks([])
    plt.gca().yaxis.grid(False)
    plt.gca().set_axis_bgcolor('white')
    #plt.gca().axes.get_xaxis().set_visible(False)
    #plt.gca().axes.get_yaxis().set_visible(False)
    plt.xlabel('Time (ms)', fontsize = 23)

title4 = "Dend0.3_shift"
save(title4, path_to_json, ext="png", close=False, verbose=True)
save(title4, path_to_json, ext="ps", close=True, verbose=True)
