"""
Calcuate the somatic depolarization ampltiude vs. stimuation distance from soma.

Intrusction:
1. Run Fig3_stim_loc.py to generate loc and dist data on different basal branches.
    - This only needs to be run once and can be used in all the analysis later.
2. Run Fig3_exp_dist_amp_NMDA_new.py to generate recording after stimulation.
3. Run Fig3_ana_NMDA_new.py to analyze the somatic recording simulated from 2.
    - A normal results csv and a TTX results csv files will be saved in the subdirectory
    of each basal branch.
4. Finally to run this file to plot the ampliude vs. distance.
    - It needs to read the TTX csv file from each basal branch.
    - It also needs to read the dist info from dist.json file.
    - Combine the data together and plot.
"""
import json
import matplotlib.pyplot as plt
from pprint import pprint
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
with open('curr_inj_dist.json', 'r') as fp:
    df_dist = json.load(fp)

path = 'Data_08_13/'
basal_num = [15, 34, 14, 22, 25, 31]

#### I perfer to combine all the data mannally without loop
df1 = pd.read_csv(path + 'B' + str(15) + "/total_results.csv")
df1 = df1.sort_values(by = ['Loc'])
df1['dist'] = df_dist['15']

df2 = pd.read_csv(path + 'B' + str(34) + "/total_results.csv")
df2 = df2.sort_values(by = ['Loc'])
df2['dist'] = df_dist['34']

df3 = pd.read_csv(path + 'B' + str(14) + "/total_results.csv")
df3 = df3.sort_values(by = ['Loc'])
df3['dist'] = df_dist['14']

df4 = pd.read_csv(path + 'B' + str(22) + "/total_results.csv")
df4 = df4.sort_values(by = ['Loc'])
df4['dist'] = df_dist['22']

df5 = pd.read_csv(path + 'B' + str(25) + "/total_results.csv")
df5 = df5.sort_values(by = ['Loc'])
df5['dist'] = df_dist['25']

df6 = pd.read_csv(path + 'B' + str(31) + "/total_results.csv")
df6 = df6.sort_values(by = ['Loc'])
df6['dist'] = df_dist['31']

##############
# Preprocess data
##############
df1 = df1[(df1['Bnum'] == "B15") & (df1['dist']> 50 )]
df2 = df2[(df2['Bnum'] == "B34") & (df2['dist']> 50 )]
df3 = df3[(df3['Bnum'] == "B14") & (df3['dist']> 50 )]
df4 = df4[(df4['Bnum'] == "B22") & (df4['dist']> 50 )]
df5 = df5[(df5['Bnum'] == "B25") & (df5['dist']> 50 )]
df6 = df6[(df6['Bnum'] == "B31") & (df6['dist']> 50 )]

# print df1
##############
# Generating figs
##############
# plt.close()
# plt.clf()
# figure = plt.figure(figsize = (9,6), dpi = 300)
# left = 0.1
# bottom = 0.15
# width = 0.8
# height = 0.75
# plt.axes([left,bottom,width,height])
# ax = plt.gca()
# plt.style.use("ggplot")
# plt.rcParams['axes.edgecolor'] = "black"
# plt.rcParams['axes.facecolor'] = '#FFFFFF'
# ax.set_axis_bgcolor('white')
# ax.spines['top'].set_visible(False)
# ax.spines['right'].set_visible(False)
#
# # Only show ticks on the left and bottom spines
# ax.yaxis.set_ticks_position('left')
# ax.xaxis.set_ticks_position('bottom')
# ax.axhline(linewidth=3, color = 'black')
# ax.axvline(linewidth=3, color = 'black')
# ax.plot(df1['dist'], df1['platamp'], marker = 'o', markersize=10,
# color = tableau(0), linewidth = 2, alpha = 0.5, label = "Basal #15")
# ax.plot(df2['dist'], df2['platamp'], marker = 'v', markersize=10,
# color = tableau(2), linewidth = 2, alpha = 0.5, label = "Basal #34")
# ax.plot(df3['dist'], df3['platamp'], marker = '^', markersize=10,
# color = tableau(4), linewidth = 2, alpha = 0.5, label = "Basal #14")
# ax.plot(df4['dist'], df4['platamp'], marker = '<', markersize=10,
# color = tableau(8), linewidth = 2, alpha = 0.5, label = "Basal #22")
# ax.plot(df5['dist'], df5['platamp'], marker = 's', markersize=10,
# color = tableau(14), linewidth = 2, alpha = 0.5, label = "Basal #25")
# ax.plot(df6['dist'], df6['platamp'], marker = '>', markersize=10,
# color = tableau(6), linewidth = 2, alpha = 0.5, label = "Basal #31")
# ax.set_xlim([0, 250])
# ax.set_xlabel("Input distance from soma (um)", size = 22, color = 'black')
# ax.set_ylabel("Amplitude in soma (mV)", size = 22, color = 'black')
# plt.tick_params(labelsize=22, pad = 12, direction='in', length=6, width=2, colors = 'black')
# plt.yticks(np.arange(0, 31, step=5))
# plt.xticks(np.arange(0, 251, step=50))
# plt.legend(loc = 'best', fontsize = 20)
# ax.set_title("Plateau Amplitude vs. Input Location", size = 22, color = 'black')
# ttl = ax.title
# ttl.set_position([0.5, 1.05])
# ax.set_ylim([0, 30])
# #plt.show()
# name = "Dist_Platamp"
# save(name, path, ext = 'ps', close = False, verbose = True)
# save(name, path, ext = 'pdf', close = False, verbose = True)
# save(name, path, ext = 'png', close = True, verbose = True)


##############
# Generating B&W figs
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
ax.plot(df1['dist'], df1['peak_v'], linestyle = '-', marker = 'o', markersize=10,
color = tableau(14), linewidth = 1.5, markerfacecolor="None", markeredgecolor = tableau(20), markeredgewidth=1.5, label = "Basal #15")
ax.plot(df2['dist'], df2['peak_v'], linestyle = '--', marker = 'v', markersize=10,
color = tableau(14), linewidth = 1.5, markerfacecolor="None", markeredgecolor = tableau(20), markeredgewidth=1.5, label = "Basal #34")
ax.plot(df3['dist'], df3['peak_v'], linestyle = '-', marker = '^', markersize=10,
color = tableau(14), linewidth = 1.5, markerfacecolor="None", markeredgecolor = tableau(20), markeredgewidth=1.5, label = "Basal #14")
ax.plot(df4['dist'], df4['peak_v'], linestyle = '--', marker = '*', markersize=10,
color = tableau(14), linewidth = 1.5, markerfacecolor="None", markeredgecolor = tableau(20), markeredgewidth=1.5, label = "Basal #22")
ax.plot(df5['dist'], df5['peak_v'], linestyle = '-', marker = 's', markersize=10,
color = tableau(14), linewidth = 1.5, markerfacecolor="None", markeredgecolor = tableau(20), markeredgewidth=1.5, label = "Basal #25")
ax.plot(df6['dist'], df6['peak_v'], linestyle = '--', marker = '8', markersize=10,
color = tableau(14), linewidth = 1.5, markerfacecolor="None", markeredgecolor = tableau(20), markeredgewidth=1.5, label = "Basal #31")
ax.set_xlim([0, 250])
ax.set_xlabel("Input distance from soma (um)", size = 22, color = 'black')
ax.set_ylabel("Voltage (mV)", size = 22, color = 'black')
plt.tick_params(labelsize=22, pad = 12, direction='in', length=6, width=2, colors = 'black')
plt.yticks(np.arange(0, 120, step=20))
plt.xticks(np.arange(0, 251, step=50))
plt.legend(loc = 'best', fontsize = 20)
ax.set_title("Dendritic voltage with current injection", size = 22, color = 'black')
ttl = ax.title
ttl.set_position([0.5, 1.05])
ax.set_ylim([0, 90])
#plt.show()
name = "Dist_Curr_inj_BW_v2"
save(name, path, ext = 'ps', close = False, verbose = True)
save(name, path, ext = 'pdf', close = False, verbose = True)
save(name, path, ext = 'png', close = True, verbose = True)
