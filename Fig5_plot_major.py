"""
Calcuate the somatic depolarization ampltiude vs. stimuation distance from soma.
For Fig 5. C1 - Model 2
Calcuate the plateau duration vs. stimuation distance from soma.
For Fig 5. E2 - Model 2

Intrusction:
1. Run Fig5_exp_major.py to generate recording after stimulation.
2. Run Fig5_ana_major.py to analyze the somatic recording simulated from 2.
    - A normal results csv and a TTX results csv files will be saved in the subdirectory
    of each basal branch.
3. Run this file to plot the ampliude or duration vs. distance
    - It needs to read the TTX csv file from each basal branch.
    - It also needs to read the dist info from dist.json file.
    - Combine the data together and plot.

Author: Peng Penny Gao
<penggao.1987@gmail.com>
"""
import json
import matplotlib.pyplot as plt
import os
import numpy as np
import pandas as pd
# import sys
# sys.path.append('../')
from analysis_utils import tableau
import seaborn as sns
from utils import *

##############
# Load dist info
##############
with open('dist.json', 'r') as fp:
    df_dist = json.load(fp)

path = 'Fig5/Major/'
basal_num = [15, 34, 14, 22, 25, 31]

#### I perfer to combine all the data mannally without loop
df1 = pd.read_csv(path + 'B' + str(15) + "/TTX_total_results.csv")
df1_T = df1[df1['NMDA_weight'] == 0.9][['Bnum', 'Loc', 'NMDA_weight', 'soma_platamp', 'dend_platamp', 'dend_platdur']].sort_values(by = ['Loc'])
df1_T['dist'] = df_dist['15']

df2 = pd.read_csv(path + 'B' + str(34) + "/TTX_total_results.csv")
df2_T = df2[df2['NMDA_weight'] == 0.9][['Bnum', 'Loc', 'NMDA_weight', 'soma_platamp', 'dend_platamp', 'dend_platdur']].sort_values(by = ['Loc'])
df2_T['dist'] = df_dist['34']

df3 = pd.read_csv(path + 'B' + str(14) + "/TTX_total_results.csv")
df3_T = df3[df3['NMDA_weight'] == 0.9][['Bnum', 'Loc', 'NMDA_weight', 'soma_platamp', 'dend_platamp', 'dend_platdur']].sort_values(by = ['Loc'])
df3_T['dist'] = df_dist['14']

df4 = pd.read_csv(path + 'B' + str(22) + "/TTX_total_results.csv")
df4_T = df4[df4['NMDA_weight'] == 0.9][['Bnum', 'Loc', 'NMDA_weight', 'soma_platamp', 'dend_platamp', 'dend_platdur']].sort_values(by = ['Loc'])
df4_T['dist'] = df_dist['22']

df5 = pd.read_csv(path + 'B' + str(25) + "/TTX_total_results.csv")
df5_T = df5[df5['NMDA_weight'] == 0.9][['Bnum', 'Loc', 'NMDA_weight', 'soma_platamp', 'dend_platamp', 'dend_platdur']].sort_values(by = ['Loc'])
df5_T['dist'] = df_dist['25']

df6 = pd.read_csv(path + 'B' + str(31) + "/TTX_total_results.csv")
df6_T = df6[df6['NMDA_weight'] == 0.9][['Bnum', 'Loc', 'NMDA_weight', 'soma_platamp', 'dend_platamp', 'dend_platdur']].sort_values(by = ['Loc'])
df6_T['dist'] = df_dist['31']

##############
# Preprocess data
##############
df1 = df1_T[(df1_T['Bnum'] == "B15") & (df1_T['dist']> 50 )][['dist', 'soma_platamp', 'dend_platamp', 'dend_platdur']]
df2 = df2_T[(df2_T['Bnum'] == "B34") & (df2_T['dist']> 50 )][['dist', 'soma_platamp', 'dend_platamp', 'dend_platdur']]
df3 = df3_T[(df3_T['Bnum'] == "B14") & (df3_T['dist']> 75 )][['dist', 'soma_platamp', 'dend_platamp', 'dend_platdur']]
df4 = df4_T[(df4_T['Bnum'] == "B22") & (df4_T['dist']> 75 )][['dist', 'soma_platamp', 'dend_platamp', 'dend_platdur']]
df5 = df5_T[(df5_T['Bnum'] == "B25") & (df5_T['dist']> 75 )][['dist', 'soma_platamp', 'dend_platamp', 'dend_platdur']]
df6 = df6_T[(df6_T['Bnum'] == "B31") & (df6_T['dist']> 50 )][['dist', 'soma_platamp', 'dend_platamp', 'dend_platdur']]

##############
# Generating figs - plot plateau amplitude against input distance from soma
##############
plt.close()
plt.clf()
figure = plt.figure(figsize = (9,6), dpi = 300)
left = 0.1
bottom = 0.15
width = 0.8
height = 0.75
plt.axes([left,bottom,width,height])
ax = plt.gca()
plt.style.use("ggplot")
plt.rcParams['axes.edgecolor'] = "black"
plt.rcParams['axes.facecolor'] = '#FFFFFF'
ax.set_axis_bgcolor('white')
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.yaxis.set_ticks_position('left')
ax.xaxis.set_ticks_position('bottom')
ax.axhline(linewidth=3, color = 'black')
ax.axvline(linewidth=3, color = 'black')
ax.plot(df1['dist'], df1['soma_platamp'], linestyle = '-', marker = 'o', markersize=10,
color = tableau(14), linewidth = 1.5, markerfacecolor="None", markeredgecolor = tableau(20), markeredgewidth=1.5, label = "Basal #15")
ax.plot(df2['dist'], df2['soma_platamp'], linestyle = '--', marker = 'v', markersize=10,
color = tableau(14), linewidth = 1.5, markerfacecolor="None", markeredgecolor = tableau(20), markeredgewidth=1.5, label = "Basal #34")
ax.plot(df3['dist'], df3['soma_platamp'], linestyle = '-', marker = '^', markersize=10,
color = tableau(14), linewidth = 1.5, markerfacecolor="None", markeredgecolor = tableau(20), markeredgewidth=1.5, label = "Basal #14")
ax.plot(df4['dist'], df4['soma_platamp'], linestyle = '--', marker = '*', markersize=10,
color = tableau(14), linewidth = 1.5, markerfacecolor="None", markeredgecolor = tableau(20), markeredgewidth=1.5, label = "Basal #22")
ax.plot(df5['dist'], df5['soma_platamp'], linestyle = '-', marker = 's', markersize=10,
color = tableau(14), linewidth = 1.5, markerfacecolor="None", markeredgecolor = tableau(20), markeredgewidth=1.5, label = "Basal #25")
ax.plot(df6['dist'], df6['soma_platamp'], linestyle = '--', marker = '8', markersize=10,
color = tableau(14), linewidth = 1.5, markerfacecolor="None", markeredgecolor = tableau(20), markeredgewidth=1.5, label = "Basal #31")
ax.set_xlim([0, 250])
ax.set_xlabel("Input distance from soma (um)", size = 22, color = 'black')
ax.set_ylabel("Amplitude in soma (mV)", size = 22, color = 'black')
plt.tick_params(labelsize=22, pad = 12, direction='in', length=6, width=2, colors = 'black')
plt.yticks(np.arange(0, 31, step=5))
plt.xticks(np.arange(0, 251, step=50))
plt.legend(loc = 'best', fontsize = 20)
ax.set_title("Plateau Amplitude vs. Input Location", size = 22, color = 'black')
ttl = ax.title
ttl.set_position([0.5, 1.05])
ax.set_ylim([0, 30])
#plt.show()
name = "Soma_Dist_Platamp_BW"
# save(name, path, ext = 'ps', close = False, verbose = True)
# save(name, path, ext = 'pdf', close = False, verbose = True)
save(name, path, ext = 'png', close = True, verbose = True)

##############
# Generating figs - plot plateau duration against input distance from soma
##############
plt.close()
plt.clf()
figure = plt.figure(figsize = (9,6), dpi = 300)
left = 0.15
bottom = 0.15
width = 0.8
height = 0.75
plt.axes([left,bottom,width,height])
ax = plt.gca()
plt.style.use("ggplot")
plt.rcParams['axes.edgecolor'] = "black"
plt.rcParams['axes.facecolor'] = '#FFFFFF'
ax.set_axis_bgcolor('white')
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

# Only show ticks on the left and bottom spines
ax.yaxis.set_ticks_position('left')
ax.xaxis.set_ticks_position('bottom')
ax.axhline(linewidth=3, color = 'black')
ax.axvline(linewidth=3, color = 'black')
ax.plot(df1['dist'], df1['dend_platdur'], linestyle = '-', marker = 'o', markersize=10,
color = tableau(14), linewidth = 1.5, markerfacecolor="None", markeredgecolor = tableau(20), markeredgewidth=1.5, label = "Basal #15")
ax.plot(df2['dist'], df2['dend_platdur'], linestyle = '--', marker = 'v', markersize=10,
color = tableau(14), linewidth = 1.5, markerfacecolor="None", markeredgecolor = tableau(20), markeredgewidth=1.5, label = "Basal #34")
ax.plot(df3['dist'], df3['dend_platdur'], linestyle = '-', marker = '^', markersize=10,
color = tableau(14), linewidth = 1.5, markerfacecolor="None", markeredgecolor = tableau(20), markeredgewidth=1.5, label = "Basal #14")
ax.plot(df4['dist'], df4['dend_platdur'], linestyle = '--', marker = '*', markersize=10,
color = tableau(14), linewidth = 1.5, markerfacecolor="None", markeredgecolor = tableau(20), markeredgewidth=1.5, label = "Basal #22")
ax.plot(df5['dist'], df5['dend_platdur'], linestyle = '-', marker = 's', markersize=10,
color = tableau(14), linewidth = 1.5, markerfacecolor="None", markeredgecolor = tableau(20), markeredgewidth=1.5, label = "Basal #25")
ax.plot(df6['dist'], df6['dend_platdur'], linestyle = '--', marker = '8', markersize=10,
color = tableau(14), linewidth = 1.5, markerfacecolor="None", markeredgecolor = tableau(20), markeredgewidth=1.5, label = "Basal #31")
ax.set_xlim([0, 250])
ax.set_xlabel("Input distance from soma (um)", size = 22, color = 'black')
ax.set_ylabel("Platau Duration (ms)", size = 22, color = 'black')
plt.tick_params(labelsize=22, pad = 12, direction='in', length=6, width=2, colors = 'black')
# plt.yticks(np.arange(0, 31, step=5))
plt.xticks(np.arange(0, 251, step=50))
plt.legend(loc = 'best', fontsize = 20)
ax.set_title("Plateau Duration vs. Input Location", size = 22, color = 'black')
ttl = ax.title
ttl.set_position([0.5, 1.05])
ax.set_ylim([0, 400])
# plt.show()
name = "Dist_Platdur_BW"
# save(name, path, ext = 'ps', close = False, verbose = True)
# save(name, path, ext = 'pdf', close = False, verbose = True)
save(name, path, ext = 'png', close = True, verbose = True)


##############
# Generating figs - plot plateau amplitude on dendrite at the input location
# against input distance from soma
##############
plt.close()
plt.clf()
figure = plt.figure(figsize = (9,6), dpi = 300)
left = 0.1
bottom = 0.15
width = 0.8
height = 0.75
plt.axes([left,bottom,width,height])
ax = plt.gca()
plt.style.use("ggplot")
plt.rcParams['axes.edgecolor'] = "black"
plt.rcParams['axes.facecolor'] = '#FFFFFF'
ax.set_axis_bgcolor('white')
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

# Only show ticks on the left and bottom spines
ax.yaxis.set_ticks_position('left')
ax.xaxis.set_ticks_position('bottom')
ax.axhline(linewidth=3, color = 'black')
ax.axvline(linewidth=3, color = 'black')
ax.plot(df1['dist'], df1['dend_platamp'], linestyle = '-', marker = 'o', markersize=10,
color = tableau(14), linewidth = 1.5, markerfacecolor="None", markeredgecolor = tableau(20), markeredgewidth=1.5, label = "Basal #15")
ax.plot(df2['dist'], df2['dend_platamp'], linestyle = '--', marker = 'v', markersize=10,
color = tableau(14), linewidth = 1.5, markerfacecolor="None", markeredgecolor = tableau(20), markeredgewidth=1.5, label = "Basal #34")
ax.plot(df3['dist'], df3['dend_platamp'], linestyle = '-', marker = '^', markersize=10,
color = tableau(14), linewidth = 1.5, markerfacecolor="None", markeredgecolor = tableau(20), markeredgewidth=1.5, label = "Basal #14")
ax.plot(df4['dist'], df4['dend_platamp'], linestyle = '--', marker = '*', markersize=10,
color = tableau(14), linewidth = 1.5, markerfacecolor="None", markeredgecolor = tableau(20), markeredgewidth=1.5, label = "Basal #22")
ax.plot(df5['dist'], df5['dend_platamp'], linestyle = '-', marker = 's', markersize=10,
color = tableau(14), linewidth = 1.5, markerfacecolor="None", markeredgecolor = tableau(20), markeredgewidth=1.5, label = "Basal #25")
ax.plot(df6['dist'], df6['dend_platamp'], linestyle = '--', marker = '8', markersize=10,
color = tableau(14), linewidth = 1.5, markerfacecolor="None", markeredgecolor = tableau(20), markeredgewidth=1.5, label = "Basal #31")
ax.set_xlim([0, 250])
ax.set_xlabel("Input distance from soma (um)", size = 22, color = 'black')
ax.set_ylabel("Amplitude in dendrite (mV)", size = 22, color = 'black')
plt.tick_params(labelsize=22, pad = 12, direction='in', length=6, width=2, colors = 'black')
plt.yticks(np.arange(0, 100, step=20))
plt.xticks(np.arange(0, 251, step=50))
plt.legend(loc = 'best', fontsize = 20)
ax.set_title("Dendritic Plateau Amplitude vs. Input Location", size = 22, color = 'black')
ttl = ax.title
ttl.set_position([0.5, 1.05])
ax.set_ylim([0, 80])
#plt.show()
name = "Dend_Dist_Platamp_BW"
# save(name, path, ext = 'ps', close = False, verbose = True)
# save(name, path, ext = 'pdf', close = False, verbose = True)
save(name, path, ext = 'png', close = True, verbose = True)
