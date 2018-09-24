"""
The analysis functions for EEE stimulation data.
Fig 5. C1 - Model2

Author: Peng Penny Gao
penggao.1987@gmail.com
"""

import json
import matplotlib.pyplot as plt
import os
import numpy as np
import pandas as pd
from analysis_utils import *
from utils import *
import seaborn as sns


######################################################
def analysis_N(Bnum = 'B34', path = "Fig5/Major/"):
    level2 = level[Bnum]
    new_data = pd.DataFrame(columns = ['TTX', 'Bnum', 'Loc', 'AMPA_num', 'AMPA_locs', 'AMPA_weight',
    'NMDA_num', 'NMDA_locs', 'NMDA_weight',
    'spike_num','soma_platamp', 'soma_platdur', 'dend_platamp', 'dend_platdur'])
    i = 0 # initialization
    for l2 in level2:
        path_to_json = path + str(Bnum) + "/"+ str(l2) + "/N"
        json_files = [pos_json for pos_json in os.listdir(path_to_json) if pos_json.endswith('.json')]
        num = len(json_files)
        for index, js in enumerate(json_files):
            with open(os.path.join(path_to_json, js)) as json_file:
                data = json.load(json_file)
                filename = json_files[index]
                TTX = data['TTX']
                Loc = str(l2)
                AMPA_num = data['SynAMPA']['num']
                AMPA_locs = data['SynAMPA']['locs']
                AMPA_weight = data['SynAMPA']['weight']
                NMDA_num = data['SynNMDA']['num']
                NMDA_locs = data['SynNMDA']['locs']
                NMDA_weight = data['SynNMDA']['weight']
                spike_num = spike_count(data['recording']['soma']['voltage'])
                idx, soma_platamp = soma_plat(data['recording']['soma']['voltage'])
                dend_platamp, dend_platdur = dend_plat(data['recording']['basal']['voltage_input'], idx)
                soma_platdur = dend_platdur

                new_data.loc[index + i*num] = [TTX, Bnum, Loc, AMPA_num, AMPA_locs, AMPA_weight,
                    NMDA_num, NMDA_locs, NMDA_weight, spike_num, soma_platamp, soma_platdur, dend_platamp, dend_platdur]
        i = i + 1
    savepath = path + str(Bnum) +'/total_results.csv'
    new_data.to_csv(savepath)


######################################################
def analysis_TTX(Bnum = 'B34', path = "Fig5/Major/"):
    level2 = level[Bnum]
    new_data = pd.DataFrame(columns = ['TTX', 'Bnum', 'Loc', 'AMPA_num', 'AMPA_locs', 'AMPA_weight',
    'NMDA_num', 'NMDA_locs', 'NMDA_weight',
    'spike_num', 'soma_platamp','soma_platdur', 'dend_platamp', 'dend_platdur'])
    i = 0 # initialization
    for l2 in level2:
        path_to_json = path + str(Bnum) + "/"+ str(l2) + "/TTX"
        json_files = [pos_json for pos_json in os.listdir(path_to_json) if pos_json.endswith('.json')]
        num = len(json_files)
        for index, js in enumerate(json_files):
            with open(os.path.join(path_to_json, js)) as json_file:
                data = json.load(json_file)
                filename = json_files[index]
                TTX = data['TTX']
                Loc = str(l2)
                AMPA_num = data['SynAMPA']['num']
                AMPA_locs = data['SynAMPA']['locs']
                AMPA_weight = data['SynAMPA']['weight']
                NMDA_num = data['SynNMDA']['num']
                NMDA_locs = data['SynNMDA']['locs']
                NMDA_weight = data['SynNMDA']['weight']
                spike_num = 0
                idx, soma_platamp = soma_platamp_TTX(data['recording']['soma']['voltage'])
                soma_platdur = soma_platdur_TTX(data['recording']['soma']['voltage'])
                dend_platamp, dend_platdur =  TTX_dend_plat(data['recording']['basal']['voltage_input'], idx)

                new_data.loc[index + i*num] = [TTX, Bnum, Loc, AMPA_num, AMPA_locs, AMPA_weight, NMDA_num, NMDA_locs, NMDA_weight,  spike_num, soma_platamp, soma_platdur, dend_platamp, dend_platdur]
        i = i + 1
    savepath = path + str(Bnum) +'/TTX_total_results.csv'
    new_data.to_csv(savepath)

######################################################
if __name__ == "__main__":
    start_time = time.time()
    path = "Fig5/Major/"
    level1 = [item for item in os.listdir(path) if not item.startswith('.')]

    # The loc sites vary from different basal branch
    # Use a dictionary to store each of seperately
    level = {}
    for l1 in level1:
        level[l1] = [item for item in os.listdir(path + str(l1)) if not (item.endswith('.csv') or item.endswith('.DS_Store'))]

    for l1 in level1:
        analysis_N(l1, path)
        analysis_TTX(l1, path)

    print("Finished.")
    print("--- %s seconds ---" % (time.time() - start_time))
