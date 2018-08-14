"""
The analysis functions for EEE stimulation data.
TTX analysis

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
#
#
#
# # Need to organize all the analysis and plotting here
# ######################################################
new_data = pd.DataFrame(columns = ['Glu_weight','platamp', 'platdur'])
#
# # Need to check the name of data folder
# # Replace this step with a function
# # Add the correct path here:
path_to_json = 'Data_07_27/TTX/'
start_time = time.time()
json_files = [pos_json for pos_json in os.listdir(path_to_json) if pos_json.endswith('.json')]

for index, js in enumerate(json_files):
    with open(os.path.join(path_to_json, js)) as json_file:
        data = json.load(json_file)
        filename = json_files[index]
        NMDA_weight = data['SynNMDA']['weight']
        platdur = meas_platdur(data['recording']['soma']['voltage'])
        platamp = TTX_platamp(data['recording']['soma']['voltage'])

        new_data.loc[index] = [NMDA_weight, platamp, platdur]


print("--- %s seconds ---" % (time.time() - start_time))
# new_data = new_data.sort_values(by = ['Glu_weight'])
# print new_data
# Add the correct saving path here:
savepath = path_to_json + '/TTX_results.csv'
new_data.to_csv(savepath)
#
# # ##### Plotting
df = pd.read_csv('Data_07_27//N/total_results.csv', index_col = 0)
df = df.sort_values(by = ['NMDA_weight'])
df_TTX = pd.read_csv('Data_07_27/TTX/TTX_results.csv', index_col = 0)
df_TTX = df_TTX.sort_values(by = ['Glu_weight'])

#print df_TTX
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
ax.scatter(df['NMDA_weight'], df['platamp'], s = 150, marker = 'o',
c = 'white', edgecolors = tableau(6), linewidth = 2, alpha = 1, label = "Control")
ax.scatter(df_TTX['Glu_weight'], df_TTX['platamp'], s = 150, marker = '^',
c = 'white', edgecolors = tableau(0), linewidth = 2,alpha = 1, label = "TTX")
ax.set_xlim([0.0, 1.0])
plt.xlabel("Syanptic Input Weights", size = 22, color = "black")
plt.ylabel("Plateau Amplitude (mV)", size = 22, color = "black")
plt.tick_params(labelsize=22, pad = 12, colors = "black")
plt.ylim([-1, 22])
ax.set_title("Plateau Amplitude - Compare with TTX", size = 20)
legend = ax.legend(bbox_to_anchor=(0.65, 0.3), loc=2, borderaxespad=0., fontsize = 20, frameon=False)
# legend.get_frame().set_facecolor('white')
title = "Platamp_vs_TTX"
save(title, path_to_json, ext="pdf", close=False, verbose=True)
save(title, path_to_json, ext="png", close=True, verbose=True)

# #
# # # #########################################################################
# plt.clf()
# figure = plt.figure(figsize = (9,6))
# ax = plt.gca()
# ax.scatter(df1['NMDA_weight'], df1['platamp'], s = 120, marker = 'o',
# c = tableau(0), edgecolors = tableau(14), linewidth = 2, alpha = 0.5)
# ax.scatter(df2['NMDA_weight'], df2['platamp'], s = 120, marker = 'o',
# c = tableau(4), edgecolors = tableau(14), linewidth = 2,alpha = 0.5)
# ax.set_xlim([0.01, 1])
# ax.set_xscale('log')
# ax.set_xlabel("Syanptic Input Weights (Log Scale)", size = 18)
# ax.set_ylabel("Plateau Amplitude (mV)", size = 18)
# plt.tick_params(labelsize=15, pad = 12)
# ax.set_title("Plateau Amplitude vs. Glutmate Stimulation", size = 20)
# ax.set_ylim([0, 25])
# plt.savefig(path_to_json + "/Glu_logscale_Platamp.png")
# # #
# # #
# # # #########################################################################
# plt.clf()
# figure = plt.figure(figsize = (9,6))
# ax = plt.gca()
# ax.scatter(df1['NMDA_weight'], df1['spike_num'], s = 120, marker = 'o',
# c = tableau(0), edgecolors = tableau(14), linewidth = 2, alpha = 0.5)
# ax.scatter(df2['NMDA_weight'], df2['spike_num'], s = 120, marker = 'o',
# c = tableau(4), edgecolors = tableau(14), linewidth = 2,alpha = 0.5)
# ax.set_xlim([0., 0.8])
# ax.set_xlabel("Syanptic Input Weights", size = 18)
# ax.set_ylabel("Spike Numbers", size = 18)
# plt.tick_params(labelsize=15, pad = 12)
# ax.set_title("Spike Numbers vs. Glutmate Stimulation", size = 20)
# ax.set_ylim([-0.5, 6.5])
# plt.savefig(path_to_json + "/GluStim_spike_number.png")
# # #
# # # #########################################################################
# plt.clf()
# figure = plt.figure(figsize = (9,6))
# ax = plt.gca()
# ax.scatter(df1['NMDA_weight'], df1['ISI'], s = 120, marker = 'o',
# c = tableau(0), edgecolors = tableau(14), linewidth = 2, alpha = 0.5)
# ax.scatter(df2['NMDA_weight'], df2['ISI'], s = 120, marker = 'o',
# c = tableau(4), edgecolors = tableau(14), linewidth = 2,alpha = 0.5)
# ax.set_xlim([0., 0.8])
# ax.set_xlabel("Syanptic Input Weights", size = 18)
# ax.set_ylabel("Interspike intervals (ms)", size = 18)
# plt.tick_params(labelsize=15, pad = 12)
# ax.set_title("Interspike intervals vs. Glutmate Stimulation", size = 20)
# ax.set_ylim([-0.5, 30.5])
# plt.savefig(path_to_json + "/GluStim_ISI.png")
# #
# # #########################################################################
# plt.clf()
# figure = plt.figure(figsize = (9,6))
# ax = plt.gca()
# ax.scatter(df1['NMDA_weight'], df1['platdur'], s = 120, marker = 'o',
# c = tableau(0), edgecolors = tableau(14), linewidth = 2, alpha = 0.5)
# ax.scatter(df2['NMDA_weight'], df2['platdur'], s = 120, marker = 'o',
# c = tableau(4), edgecolors = tableau(14), linewidth = 2,alpha = 0.5)
# ax.set_xlim([0., 0.8])
# ax.set_xlabel("Syanptic Input Weights", size = 18)
# ax.set_ylabel("Plateau Duration (ms)", size = 18)
# plt.tick_params(labelsize=15, pad = 12)
# ax.set_title("Plateau Duration vs. Glutmate Stimulation", size = 20)
# ax.set_ylim([-0.5, 200])
# plt.savefig(path_to_json + "/GluStim_Platdur.png")
