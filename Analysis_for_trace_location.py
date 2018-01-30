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
from utils import *

## Add the correct analysis path here:
path_to_json = 'Data_01_25/Sim1'
json_files = [pos_json for pos_json in os.listdir(path_to_json) if pos_json.endswith('.json')]
nfile = len(json_files)

soma_trace = []
dend1_trace = []
dend2_trace = []
dend3_trace = []

for index, js in enumerate(json_files):
    with open(os.path.join(path_to_json, js)) as json_file:
        data = json.load(json_file)
        filename = json_files[index]
        time = data['recording']['time']
        soma_trace.append(data['recording']['soma']['voltage'])
        dend1_trace.append(data['recording']['basal_34']['voltage_0.8'])
        dend2_trace.append(data['recording']['basal_34']['voltage_0.5'])
        dend3_trace.append(data['recording']['basal_34']['voltage_0.3'])

plt.clf()
plt.figure(figsize = (8, 6), dpi = 300)
plt.subplots_adjust(left=0.15, right=0.9, top=0.85, bottom=0.15)

for i in range(nfile):
    #new_time = [x+20*i for x in time]
    #new_soma_trace[i] = soma_trace[i] + 20*i
    plt.plot(time, soma_trace[i], color = tableau(i), linewidth = 2) #label = labels[i],
    plt.legend(loc = 'best', fontsize = 15)
    plt.title("Voltage Traces at Soma \n", fontsize = 25)
    plt.ylim([-80, 40])
    plt.ylabel('mV', fontsize = 23)
    plt.yticks(fontsize=23)
    plt.xlim([0, 400])
    plt.xlabel('Time (ms)', fontsize = 23)
    plt.xticks(fontsize=23)
    plt.gca().yaxis.grid(False)
    plt.gca().set_axis_bgcolor('white')
    #plt.xlabel('Time (ms)', fontsize = 15)
title1 = "soma_trace"
save(title1, ext="png", close=True, verbose=True)

plt.clf()
plt.figure(figsize = (8, 6), dpi = 300)
plt.subplots_adjust(left=0.15, right=0.9, top=0.85, bottom=0.15)
for i in range(nfile):
    #new_time = [x+20*i for x in time]
    plt.plot(time, dend1_trace[i],color = palette[i], label = labels[i], linewidth = 2.5)
    plt.legend(loc = 'best', fontsize = 15)
    plt.title("Voltage Traces at Basal Dendrite (loc:0.8) \n", fontsize = 25)
    plt.ylim([-80, 40])
    plt.ylabel('mV', fontsize = 23)
    plt.yticks(fontsize=23)
    plt.xlim([0, 400])
    plt.xlabel('Time (ms)', fontsize = 23)
    plt.xticks(fontsize=23)
    plt.gca().yaxis.grid(False)
    plt.gca().set_axis_bgcolor('white')
    #plt.xlabel('Time (ms)', fontsize = 15)

title2 = "Basal[34]_0.8"
save(title2, ext="png", close=True, verbose=True)

plt.clf()
plt.figure(figsize = (8, 6), dpi = 300)
plt.subplots_adjust(left=0.15, right=0.9, top=0.85, bottom=0.15)
for i in range(nfile):
    #new_time = [x+20*i for x in time]

    plt.plot(time, dend2_trace[i],color = palette[i], label = labels[i], linewidth = 2.5)
    plt.legend(loc = 'best', fontsize = 15)
    plt.title("Voltage Traces at Basal Dendrite (loc:0.5) \n", fontsize = 25)
    plt.ylim([-80, 40])
    plt.ylabel('mV', fontsize = 23)
    plt.yticks(fontsize = 23)
    plt.xlim([0, 400])
    plt.gca().yaxis.grid(False)
    plt.xlabel('Time (ms)', fontsize = 23)
    plt.xticks(fontsize=23)
    plt.gca().set_axis_bgcolor('white')


title3 = "Basal[34]_0.5"
save(title3, ext="png", close=True, verbose=True)

plt.clf()
plt.figure(figsize = (8, 6), dpi = 300)
plt.subplots_adjust(left=0.15, right=0.9, top=0.85, bottom=0.15)
for i in range(nfile):
    #new_time = [x+20*i for x in time]
    plt.plot(time, dend3_trace[i],color = palette[i], label = labels[i], linewidth = 2.5)
    plt.legend(loc = 'best', fontsize = 15)
    plt.title("Voltage Traces at Basal Dendrite (loc:0.3) \n", fontsize = 25)
    plt.ylim([-80, 40])
    plt.ylabel('mV', fontsize = 23)
    plt.yticks(fontsize=23)
    plt.xlim([0, 400])
    plt.gca().yaxis.grid(False)
    plt.xlabel('Time (ms)', fontsize = 23)
    plt.xticks(fontsize=23)
    plt.gca().set_axis_bgcolor('white')

title4 = "Basal[34]_0.3"

save(title4, ext="png", close=True, verbose=True)


###############################################################
##### Shiftted plot
###############################################################


plt.clf()
plt.figure(figsize = (8, 6), dpi = 300)
plt.subplots_adjust(left=0.15, right=0.9, top=0.85, bottom=0.1)

new_soma_trace = []
for i in range(nfile):
    new_time = [x+200*i for x in time]
    new_soma_trace.append([x+15*i for x in soma_trace[i]])
    plt.plot(new_time, new_soma_trace[i], color = palette[i], label = labels[i], linewidth = 2)
    plt.legend(loc = 'best', fontsize = 15)
    plt.title("Voltage Traces at Soma \n", fontsize = 25)
    plt.ylim([-80, 140])
    plt.ylabel('mV', fontsize = 23)
#    plt.yticks(fontsize=23)
    plt.xlim([0, 1800])
    #plt.xlabel('Time (ms)', fontsize = 15)
    plt.xticks([])
    plt.yticks([])
    plt.gca().yaxis.grid(False)
    plt.gca().set_axis_bgcolor('white')
    #plt.gca().axes.get_xaxis().set_visible(False)
    #plt.gca().axes.get_yaxis().set_visible(False)
    plt.xlabel('Time (ms)', fontsize = 23)

title5 = "Soma_shift"
save(title5, ext="png", close=True, verbose=True)

plt.clf()
plt.figure(figsize = (8, 6), dpi = 300)
plt.subplots_adjust(left=0.15, right=0.9, top=0.85, bottom=0.1)
new_dend1_trace = []

for i in range(nfile):
    new_time = [x+200*i for x in time]
    new_dend1_trace.append([x+15*i for x in dend1_trace[i]])
    plt.plot(new_time, new_dend1_trace[i],color = palette[i], label = labels[i], linewidth = 2)
    #plt.legend(loc = 'best', fontsize = 15)
    plt.title("Voltage Traces at Basal Dendrite (loc:0.8) \n", fontsize = 25)
    plt.ylim([-80, 140])
    plt.ylabel('mV', fontsize = 23)
#    plt.yticks(fontsize=23)
    plt.xlim([0, 1800])
    plt.xlabel('Time (ms)', fontsize = 23)
    plt.xticks([])
    plt.yticks([])
    plt.gca().yaxis.grid(False)
    plt.gca().set_axis_bgcolor('white')
    #plt.xlabel('Time (ms)', fontsize = 15)

title6 = "Basal[34]_0.8_shift"
save(title6, ext="png", close=True, verbose=True)


plt.clf()
plt.figure(figsize = (8, 6), dpi = 300)
plt.subplots_adjust(left=0.15, right=0.9, top=0.85, bottom=0.1)
new_dend2_trace = []

for i in range(nfile):
    new_time = [x+200*i for x in time]
    new_dend2_trace.append([x + 15*i for x in dend2_trace[i]])
    plt.plot(new_time, new_dend2_trace[i],color = palette[i], label = labels[i], linewidth = 2)
    #plt.legend(loc = 'best', fontsize = 14)
    plt.title("Voltage Traces at Basal Dendrite (loc:0.5) \n", fontsize = 25)
    plt.ylim([-80, 140])
    plt.ylabel('mV', fontsize = 23)
    #plt.yticks(fontsize = 23)
    plt.xlim([0, 1800])
    plt.gca().yaxis.grid(False)
    plt.xlabel('Time (ms)', fontsize = 23)
    plt.xticks([])
    plt.yticks([])
    plt.gca().set_axis_bgcolor('white')


title7 = "Basal[34]_0.5_shift"
save(title7, ext="png", close=True, verbose=True)

plt.clf()
plt.figure(figsize = (8, 6), dpi = 300)
plt.subplots_adjust(left=0.15, right=0.9, top=0.85, bottom=0.1)
new_dend3_trace = []
for i in range(nfile):
    new_time = [x+200*i for x in time]
    new_dend3_trace.append([x + 15*i for x in dend3_trace[i]])
    plt.plot(new_time, new_dend3_trace[i],color = palette[i], label = labels[i], linewidth = 2)
    #plt.legend(loc = 'best', fontsize = 15)
    plt.title("Voltage Traces at Basal Dendrite (loc:0.3) \n", fontsize = 25)
    plt.ylim([-80, 140])
    plt.ylabel('mV', fontsize = 23)
    #plt.yticks(fontsize=23)
    plt.xlim([0, 1800])
    plt.gca().yaxis.grid(False)
    plt.xlabel('Time (ms)', fontsize = 23)
    plt.xticks([])
    plt.yticks([])
    plt.gca().set_axis_bgcolor('white')

title8 = "Basal[34]_0.3_shift"

save(title8, ext="png", close=True, verbose=True)
