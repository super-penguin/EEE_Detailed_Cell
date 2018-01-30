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
path_to_json = 'Data_01_25/Sim1'
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

        new_data.loc[index] = [AMPA_num, AMPA_locs, AMPA_weight,
        NMDA_num, NMDA_locs, NMDA_weight, NMDA_Beta, NMDA_Cdur,
        spike_num, platamp, ISI, platdur]


print("--- %s seconds ---" % (time.time() - start_time))

# print new_data
# # Add the correct saving path here:
# savepath = 'Data_01_25/Sim1/total_results.csv'
# new_data.to_csv(savepath)
#
# # ##### Plotting
# df = pd.read_csv(savepath, index_col = 0)
# df = df.sort_values(by = ['NMDA_weight'])
# df1 = df[df['spike_num'] == 0]
# df2 = df[df['spike_num'] != 0]
# #
# plt.clf()
# figure = plt.figure(figsize = (9,6))
# # left = 0.05
# # bottom = 0.05
# # width = 0.9
# # height = 0.9
# # plt.axes([left,bottom,width,height])
# ax = plt.gca()
# ax.scatter(df1['NMDA_weight'], df1['platamp'], s = 120, marker = 'o',
# c = tableau(0), edgecolors = tableau(14), linewidth = 2, alpha = 0.5)
# ax.scatter(df2['NMDA_weight'], df2['platamp'], s = 120, marker = 'o',
# c = tableau(4), edgecolors = tableau(14), linewidth = 2,alpha = 0.5)
# ax.set_xlim([0, 0.8])
# ax.set_xlabel("Syanptic Input Weights", size = 18)
# ax.set_ylabel("Plateau Amplitude (mV)", size = 18)
# plt.tick_params(labelsize=15, pad = 12)
# ax.set_title("Plateau Amplitude vs. Glutmate Stimulation", size = 20)
# ax.set_ylim([0, 25])
# #plt.show()
# plt.savefig("Data_01_25/Sim1//GluStim_Platamp.png")
# #
# # #########################################################################
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
# plt.savefig("Data_01_25/Sim1/Glu_logscale_Platamp.png")
# #
# #
# # #########################################################################
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
# ax.set_ylim([-0.5, 3.5])
# plt.savefig("Data_01_25/Sim1/GluStim_spike_number.png")
# #
# # #########################################################################
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
# plt.savefig("Data_01_25/Sim1/GluStim_ISI.png")
#
# #########################################################################
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
# plt.savefig("Data_01_25/Sim1/GluStim_Platdur.png")
