"""
Calculate the stimulatin distance for each basal dendrite
1. Make sure to stimuate same number of segments each time
2. Make sure the stimuation site is whithin a 10 - 20 um range
3. Save the stimulation loc info as dictionary in json file
Author: Peng (Penny) Gao <penggao.1987@gmail.com>
"""

from CA229 import *
import matplotlib.pyplot as plt
from neuron import h
import numpy as np
from utils import *
import json
import itertools
import time
import pdb     # For python debugging
from random import *
import math
import pandas as pd



def stim_loc(Branch):
    nseg = Branch.nseg
    loc_vec = []
    dist_vec = []
    for seg in Branch.allseg():
        loc_vec.append(seg.x)
        dist_vec.append(h.distance(seg.x, sec = Branch))
    length = dist_vec[-1] - dist_vec[0]
    each_len = math.floor((1.0/nseg) * 100)/100.0
    loc = []
    dist = []
    if each_len > 10:
        for i in range(1, len(loc_vec)):
            temp_loc = [loc_vec[i] - each_len, loc_vec[i] + each_len]
            loc.append(temp_loc)
            dist.append(dist_vec[i])
    elif each_len <= 10:
        for i in range(1, len(loc_vec)-2, 2):
            temp_loc =[loc_vec[i], loc_vec[i+2]]
            loc.append(temp_loc)
            dist.append(dist_vec[i+1])
    return loc, dist

def current_inj_loc(Branch):
    nseg = Branch.nseg
    loc_vec = []
    dist_vec = []
    for seg in Branch.allseg():
        if seg.x != 0.0 and seg.x != 1.0:
            loc_vec.append(seg.x)
            dist_vec.append(h.distance(seg.x, sec = Branch))
    return loc_vec, dist_vec

#####################################
if __name__ == "__main__":
    print("Running the model")
    start_time = time.time()
    h.load_file('stdrun.hoc') # for initialization
    loc_profile = {}
    dist_profile = {}
    curr_loc = {}
    curr_dist = {}
    # loc_profile = pd.DataFrame(columns = ['Bnum','Loc'])
    Cell = CA229()
    basal_num = [15, 34, 14, 22, 25, 31]
    i = 0
    for b in basal_num:
        loc, dist = stim_loc(Cell.basal[b])
        loc_profile[b] = loc
        dist_profile[b] = dist
        curr_loc[b], curr_dist[b] = current_inj_loc(Cell.basal[b])
    # with open('data.json', 'w') as fp:
    #     json.dump(loc_profile, fp)
    # with open('dist.json', 'w') as fp:
    #     json.dump(dist_profile, fp)
    with open('curr_inj_loc.json', 'w') as fp:
        json.dump(curr_loc, fp)
    with open('curr_inj_dist.json', 'w') as fp:
        json.dump(curr_dist, fp)

    print("Finished.")
    print("--- %s seconds ---" % (time.time() - start_time))
