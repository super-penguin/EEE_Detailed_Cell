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
path_to_json = 'Data_10_10'
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


tableau21 = [(31, 119, 180), (174, 199, 232), (255, 127, 14), (255, 187, 120),
             (44, 160, 44), (152, 223, 138), (214, 39, 40), (255, 152, 150),
             (148, 103, 189), (197, 176, 213), (140, 86, 75), (196, 156, 148),
             (227, 119, 194), (247, 182, 210), (127, 127, 127), (199, 199, 199),
             (188, 189, 34), (219, 219, 141), (23, 190, 207), (158, 218, 229),
             (0, 0, 0)]

# Scale the RGB values to the [0, 1] range, which is the format matplotlib accepts.
for i in range(len(tableau21)):
    r, g, b = tableau21[i]
    tableau21[i] = (r / 255., g / 255., b / 255.)

# Change the color and label numbers based on the number plots you need:
palette = [tableau21[0], tableau21[1], tableau21[2], tableau21[4], tableau21[6],
tableau21[7], tableau21[8], tableau21[14]]
labels = ['Glu_Stim 0.01', 'Glu_Stim 0.02', 'Glu_Stim 0.03',
'Glu_Stim 0.06', 'Glu_Stim 0.15', 'Glu_Stim 0.20', 'Glu_Stim 0.30', 'Glu_Stim 0.40']

plt.clf()
plt.figure(figsize = (8, 6), dpi = 300)
plt.subplots_adjust(left=0.15, right=0.9, top=0.85, bottom=0.15)

for i in range(nfile):
    #new_time = [x+20*i for x in time]
    #new_soma_trace[i] = soma_trace[i] + 20*i
    plt.plot(time, soma_trace[i], color = palette[i], label = labels[i], linewidth = 2)
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

title1 = "Soma"
save(title1, ext="png", close=True, verbose=True)

plt.clf()
plt.figure(figsize = (8, 6), dpi = 300)
plt.subplots_adjust(left=0.15, right=0.9, top=0.85, bottom=0.15)
for i in range(nfile):
    #new_time = [x+20*i for x in time]
    plt.plot(time, dend1_trace[i],color = palette[i], label = labels[i], linewidth = 2)
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

    plt.plot(time, dend2_trace[i],color = palette[i], label = labels[i], linewidth = 2)
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

    plt.plot(time, dend3_trace[i],color = palette[i], label = labels[i], linewidth = 2)
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
    new_time = [x+300*i for x in time]
    new_soma_trace.append([x+20*i for x in soma_trace[i]])
    plt.plot(new_time, new_soma_trace[i], color = palette[i], label = labels[i], linewidth = 2)
    #plt.legend(loc = 'best', fontsize = 15)
    plt.title("Voltage Traces at Soma \n", fontsize = 25)
    #plt.ylim([-80, 40])
    #plt.ylabel('mV', fontsize = 23)
    #plt.yticks(fontsize=23)
#    plt.xlim([0, 1000])
    #plt.xlabel('Time (ms)', fontsize = 15)
    #plt.xticks([])
    plt.gca().yaxis.grid(False)
    plt.gca().set_axis_bgcolor('white')
    #plt.xlabel('Time (ms)', fontsize = 15)

title5 = "Soma_shift"
save(title5, ext="png", close=True, verbose=True)

plt.clf()
plt.figure(figsize = (8, 6), dpi = 300)
plt.subplots_adjust(left=0.15, right=0.9, top=0.85, bottom=0.1)
new_dend1_trace = []

for i in range(nfile):
    new_time = [x+300*i for x in time]
    new_dend1_trace.append([x+20*i for x in dend1_trace[i]])
    plt.plot(new_time, new_dend1_trace[i],color = palette[i], label = labels[i], linewidth = 2)
    plt.legend(loc = 'best', fontsize = 15)
    plt.title("Voltage Traces at Basal Dendrite (loc:0.8) \n", fontsize = 25)
#    plt.ylim([-80, 40])
#    plt.ylabel('mV', fontsize = 23)
#    plt.yticks(fontsize=23)
#    plt.xlim([0, 1000])
    plt.xlabel('Time (ms)', fontsize = 15)
    #plt.xticks([])
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
    new_time = [x+300*i for x in time]
    new_dend2_trace.append([x + 20*i for x in dend2_trace[i]])
    plt.plot(new_time, new_dend2_trace[i],color = palette[i], label = labels[i], linewidth = 2)
    #plt.legend(loc = 'best', fontsize = 14)
    plt.title("Voltage Traces at Basal Dendrite (loc:0.5) \n", fontsize = 25)
    #plt.ylim([-80, 40])
    #plt.ylabel('mV', fontsize = 23)
    #plt.yticks(fontsize = 23)
    #plt.xlim([0, 1000])
    plt.gca().yaxis.grid(False)
    #plt.xlabel('Time (ms)', fontsize = 15)
    #plt.xticks([])
    plt.gca().set_axis_bgcolor('white')


title7 = "Basal[34]_0.5_shift"
save(title7, ext="png", close=True, verbose=True)

plt.clf()
plt.figure(figsize = (8, 6), dpi = 300)
plt.subplots_adjust(left=0.15, right=0.9, top=0.85, bottom=0.1)
new_dend3_trace = []
for i in range(nfile):
    new_time = [x+300*i for x in time]
    new_dend3_trace.append([x + 20*i for x in dend3_trace[i]])
    plt.plot(new_time, new_dend3_trace[i],color = palette[i], label = labels[i], linewidth = 2)
    #plt.legend(loc = 'best', fontsize = 15)
    plt.title("Voltage Traces at Basal Dendrite (loc:0.3) \n", fontsize = 25)
    #plt.ylim([-80, 40])
    #plt.ylabel('mV', fontsize = 23)
    #plt.yticks(fontsize=23)
    #plt.xlim([0, 1000])
    plt.gca().yaxis.grid(False)
    #plt.xlabel('Time (ms)', fontsize = 15)
    #plt.xticks([])
    plt.gca().set_axis_bgcolor('white')

title8 = "Basal[34]_0.3_shift"

save(title8, ext="png", close=True, verbose=True)
