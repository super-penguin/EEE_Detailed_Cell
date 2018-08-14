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


######################################################
def analysis_N(Bnum = 'B34', path = "Data_05_23/"):
    level2 = level[Bnum]
    new_data = pd.DataFrame(columns = ['Bnum', 'TTX', 'dur', 'amp', 'Loc', 'peak_v'])
    i = 0 # initialization
    for l2 in level2:
        path_to_json = path + str(Bnum) + "/"+ str(l2) + "/N"
        json_files = [pos_json for pos_json in os.listdir(path_to_json) if pos_json.endswith('.json')]
        num = len(json_files)
        for index, js in enumerate(json_files):
            with open(os.path.join(path_to_json, js)) as json_file:
                data = json.load(json_file)
                filename = json_files[index]
                TTX = False
                Loc = data['curr_loc']
                amp = data['curr_amp']
                dur = data['curr_dur']
                peak_v = v_curr_inj(data['recording']['basal']['voltage_'+str(Loc)])

                new_data.loc[index + i*num] = [Bnum, TTX, dur, amp, Loc, peak_v]
        i = i + 1
    savepath = path + str(Bnum) +'/total_results.csv'
    new_data.to_csv(savepath)


######################################################
def analysis_TTX(Bnum = 'B34', path = "Data_05_23/"):
    level2 = level[Bnum]
    new_data = pd.DataFrame(columns = ['Bnum', 'TTX', 'dur', 'amp', 'Loc', 'peak_v'])
    i = 0 # initialization
    for l2 in level2:
        path_to_json = path + str(Bnum) + "/"+ str(l2) + "/TTX"
        json_files = [pos_json for pos_json in os.listdir(path_to_json) if pos_json.endswith('.json')]
        num = len(json_files)
        for index, js in enumerate(json_files):
            with open(os.path.join(path_to_json, js)) as json_file:
                data = json.load(json_file)
                filename = json_files[index]
                TTX = True
                Loc = data['curr_loc']
                amp = data['curr_amp']
                dur = data['curr_dur']
                peak_v = v_curr_inj(data['recording']['basal']['voltage_'+str(Loc)])

                new_data.loc[index + i*num] = [Bnum, TTX, dur, amp, Loc, peak_v]
        i = i + 1
    savepath = path + str(Bnum) +'/TTX_total_results.csv'
    new_data.to_csv(savepath)


######################################################
if __name__ == "__main__":
    start_time = time.time()
    path = "Data_08_13/"
    level1 = [item for item in os.listdir(path) if not item.startswith('.')]

    # The loc sites vary from different basal branch
    # Use a dictionary to store each of seperately
    level = {}
    for l1 in level1:
        level[l1] = [item for item in os.listdir(path + str(l1)) if not (item.endswith('.csv') or item.endswith('.DS_Store'))]

    for l1 in level1:
        analysis_N(l1, path)
        # analysis_TTX(l1, path)
