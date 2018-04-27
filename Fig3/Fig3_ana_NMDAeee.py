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

# def list_files(dir):
#     r = []
#     for root, dirs, files in os.walk(dir):
#         # r = [name for name in files if name.endswith('.json')]
#         for name in files:
#             r.append(os.path.join(root, name))
#     return r
#
# def listdir_nohidden(path):
#     for f in os.listdir(path):
#         if not f.startswith('.'):
#             yield f

# Need to organize all the analysis and plotting here
######################################################
new_data = pd.DataFrame(columns = ['TTX', 'Bnum', 'Loc', 'AMPA_num', 'AMPA_locs', 'AMPA_weight',
'NMDA_num', 'NMDA_locs', 'NMDA_weight', 'NMDA_Beta', 'NMDA_Cdur',
'spike_num','platamp', 'ISI', 'platdur'])
start_time = time.time()
path = "Fig3_NMDAeee/"
level1 = [item for item in os.listdir(path) if not item.startswith('.')]
for l1 in level1:
    level2 = [item for item in os.listdir(path + str(l1)) if not item.endswith('.csv')]

i = 0
for l1 in level1:
    for l2 in level2:
        path_to_json = path + str(l1) + "/"+ str(l2) + "/N"
        json_files = [pos_json for pos_json in os.listdir(path_to_json) if pos_json.endswith('.json')]
        num = len(json_files)
        for index, js in enumerate(json_files):
            with open(os.path.join(path_to_json, js)) as json_file:
                data = json.load(json_file)
                filename = json_files[index]
                TTX = False
                Bnum = str(l1)
                Loc = str(l2)
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
                # # For TTX
                # platamp = TTX_platamp(data['recording']['soma']['voltage'])
                # ISI = 0
                new_data.loc[index + i*num] = [TTX, Bnum, Loc, AMPA_num, AMPA_locs, AMPA_weight,
                    NMDA_num, NMDA_locs, NMDA_weight, NMDA_Beta, NMDA_Cdur,
                    spike_num, platamp, ISI, platdur]
            i = i+1

savepath = path + '/total_results.csv'
new_data.to_csv(savepath)


######################################################
new_data = pd.DataFrame(columns = ['TTX', 'Bnum', 'Loc', 'AMPA_num', 'AMPA_locs', 'AMPA_weight',
'NMDA_num', 'NMDA_locs', 'NMDA_weight', 'NMDA_Beta', 'NMDA_Cdur',
'spike_num','platamp', 'ISI', 'platdur'])
start_time = time.time()
# path = "Data_04_24/"
level1 = [item for item in os.listdir(path) if not (item.startswith('.') or item.endswith('.csv'))]
for l1 in level1:
    level2 = [item for item in os.listdir(path + str(l1)) if not item.startswith('.')]

i = 0
for l1 in level1:
    for l2 in level2:
        path_to_json = path + str(l1) + "/"+ str(l2) + "/TTX"
        json_files = [pos_json for pos_json in os.listdir(path_to_json) if pos_json.endswith('.json')]
        num = len(json_files)
        for index, js in enumerate(json_files):
            with open(os.path.join(path_to_json, js)) as json_file:
                data = json.load(json_file)
                filename = json_files[index]
                TTX = True
                Bnum = str(l1)
                Loc = str(l2)
                AMPA_num = data['SynAMPA']['num']
                AMPA_locs = data['SynAMPA']['locs']
                AMPA_weight = data['SynAMPA']['weight']
                NMDA_num = data['SynNMDA']['num']
                NMDA_locs = data['SynNMDA']['locs']
                NMDA_weight = data['SynNMDA']['weight']
                NMDA_Beta = data['SynNMDA']['Beta']
                NMDA_Cdur = data['SynNMDA']['Cdur']
                spike_num = 0
                # ISI, platamp = meas_platamp(data['recording']['soma']['voltage'])
                platdur = meas_platdur(data['recording']['soma']['voltage'])
                # For TTX
                platamp = TTX_platamp(data['recording']['soma']['voltage'])
                ISI = 0
                new_data.loc[index + i*num] = [TTX, Bnum, Loc, AMPA_num, AMPA_locs, AMPA_weight,
                    NMDA_num, NMDA_locs, NMDA_weight, NMDA_Beta, NMDA_Cdur,
                    spike_num, platamp, ISI, platdur]
            i = i+1

savepath = path + '/TTX_total_results.csv'
new_data.to_csv(savepath)
