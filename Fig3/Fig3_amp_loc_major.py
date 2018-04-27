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
# Load data
##############
path = "Data_04_26/"
# Analysis data with plateau amp and dur
df_N = pd.read_csv(path + "total_results.csv")
df_TTX = pd.read_csv(path + "TTX_total_results.csv")
# cd ..
# Location info with distance to soma
df = pd.read_csv("Location_Amp_adj.csv")
##############
# Preprocess data
##############
df_T = df_TTX[df_TTX['NMDA_weight'] == 0.7][['Bnum', 'Loc', 'NMDA_weight', 'platamp', 'platdur']]
df_new = pd.merge(df, df_T, on=['Bnum', 'Loc'], how='left')
# Distance and amp info for each basal branch
df1 = df_new[(df_new['Bnum'] == "B14") & (df_new['distance']> 75 )][['distance', 'platamp', 'platdur']]
# Note: the first measurements in basal14 has some problem at location 0.2-0.3
df2 = df_new[(df_new['Bnum'] == "B15") & (df_new['distance']> 75 )][['distance', 'platamp', 'platdur']]
df3 = df_new[(df_new['Bnum'] == "B22") & (df_new['distance']> 120 )][['distance', 'platamp', 'platdur']]
df4 = df_new[(df_new['Bnum'] == "B25") & (df_new['distance']> 90 )][['distance', 'platamp', 'platdur']]
df5 = df_new[(df_new['Bnum'] == "B34") & (df_new['distance']> 60 )][['distance', 'platamp', 'platdur']]
df6 = df_new[(df_new['Bnum'] == "B31") & (df_new['distance']> 100 )][['distance', 'platamp', 'platdur']]

##############
# Generating figs
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
ax.plot(df1['distance'], df1['platamp'], marker = 'o', markersize=10,
color = tableau(0), linewidth = 2, alpha = 0.5, label = "Basal #14")
ax.plot(df2['distance'], df2['platamp'], marker = 'v', markersize=10,
color = tableau(2), linewidth = 2, alpha = 0.5, label = "Basal #15")
ax.plot(df3['distance'], df3['platamp'], marker = '^', markersize=10,
color = tableau(4), linewidth = 2, alpha = 0.5, label = "Basal #22")
ax.plot(df4['distance'], df4['platamp'], marker = '<', markersize=10,
color = tableau(8), linewidth = 2, alpha = 0.5, label = "Basal #25")
ax.plot(df6['distance'], df6['platamp'], marker = 's', markersize=10,
color = tableau(14), linewidth = 2, alpha = 0.5, label = "Basal #31")
ax.plot(df5['distance'], df5['platamp'], marker = '>', markersize=10,
color = tableau(6), linewidth = 2, alpha = 0.5, label = "Basal #34")
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
ax.set_ylim([0, 25])
#plt.show()
name = "Dist_Platamp"
save(name, path, ext = 'ps', close = False, verbose = True)
save(name, path, ext = 'png', close = True, verbose = True)



#########################################
# plt.close()
# plt.clf()
# figure = plt.figure(figsize = (9,6), dpi = 300)
# left = 0.1
# bottom = 0.12
# width = 0.8
# height = 0.75
# plt.axes([left,bottom,width,height])
# ax = plt.gca()
# # ax.set_frame_on(False)
# # Hide the right and top spines
# ax.spines['right'].set_visible(False)
# ax.spines['top'].set_visible(False)
#
# # Only show ticks on the left and bottom spines
# ax.yaxis.set_ticks_position('left')
# ax.xaxis.set_ticks_position('bottom')
# ax.plot(df1['distance'], df1['Duration'], marker = 'o', markersize=10,
# color = tableau(0), linewidth = 2, alpha = 0.5, label = "Basal #14")
# ax.plot(df2['distance'], df2['Duration'], marker = 'v', markersize=10,
# color = tableau(2), linewidth = 2, alpha = 0.5, label = "Basal #15")
# ax.plot(df3['distance'], df3['Duration'], marker = '^', markersize=10,
# color = tableau(4), linewidth = 2, alpha = 0.5, label = "Basal #22")
# ax.plot(df4['distance'], df4['Duration'], marker = '<', markersize=10,
# color = tableau(8), linewidth = 2, alpha = 0.5, label = "Basal #25")
# ax.plot(df6['distance'], df6['Duration'], marker = 's', markersize=10,
# color = tableau(14), linewidth = 2, alpha = 0.5, label = "Basal #31")
# ax.plot(df5['distance'], df5['Duration'], marker = '>', markersize=10,
# color = tableau(6), linewidth = 2, alpha = 0.5, label = "Basal #34")
# ax.set_xlim([0, 250])
# ax.set_xlabel("Input distance from soma (um)", size = 18)
# ax.set_ylabel("Plateau duration(>= 10mV) (ms)", size = 18)
# plt.tick_params(labelsize=15, pad = 12)
# plt.legend(loc = 'best')
# ax.set_title("Plateau Duration vs. Input Location", size = 20)
# ttl = ax.title
# ttl.set_position([0.5, 1.05])
# ax.set_ylim([-5, 170])
# #plt.show()
# plt.savefig("Dist_Platdur.ps")
# # plt.savefig("Dist_Platdur.png")
