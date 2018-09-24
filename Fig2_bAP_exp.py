"""
Simulation of bAP to basal dendrite in the detailed cell model
The orginal model is from
https://senselab.med.yale.edu/ModelDB/ShowModel.cshtml?model=117207&file=/acker_antic/Model/CA%20229.hoc#tabs-2
Modified by : Peng Penny Gao <penggao.1987@gmail.com>

1. Run 3 different condition: TTX, 3-AP and control
2. Run on all basal branches
"""
from CA229 import *
import matplotlib.pyplot as plt
from neuron import h
import numpy as np
from utils import *
import json
import itertools
import time
# import pdb     # For python debugging
from random import *

h.load_file('stdrun.hoc') # for initialization

################### Test the ratio of different repceptors
def bAP(Bnum = 34, TTX = False, Atype = False, vec = []):
    """
    Bnum: the recording branch
    -----------
    Outputs:
        json: soma and dendritc voltage recording and parameters info
    """
    timestr = time.strftime("%H%M")
    data = time.strftime("%m_%d")
    directory = 'Fig2/'
    # directory = 'Data_' + data +'/'
    Cell = CA229()
    ###########################################
    if (TTX == False and Atype == False):
        title = "Control_" + "Bnum_" + str(Bnum) + "_" + timestr
        ###########################################
        # Current injection in soma
        ###########################################
        ic = h.IClamp(Cell.soma[2](0.5))
        ic.dur = 1.75
        ic.delay = 150
        ic.amp = 3
    elif (TTX == True):
        Cell.TTX_bAP()
        Vstim = h.SEClamp(Cell.soma[2](0.5))
        Vstim.rs= 0.01
        Vstim.dur1 = 1e9
        vec.play(Vstim._ref_amp1, h.dt)
        title = "TTX_" + "Bnum_" + str(Bnum) + "_" + timestr
    else:
        Cell = CA229(KA_ratio = 0.0)
        ic = h.IClamp(Cell.soma[2](0.5))
        ic.dur = 1.75
        ic.delay = 150
        ic.amp = 3
        title = "4AP_" + "Bnum_" + str(Bnum) + "_" + timestr

    ###########################################
    ### Recording
    ###########################################
    t_vec = h.Vector()
    t_vec.record(h._ref_t)
    v_vec_soma = h.Vector()
    v_vec_soma.record(Cell.soma[2](0.5)._ref_v)

    dist = []
    Loc = []
    for seg in Cell.basal[Bnum]:
        Loc.append(seg.x)
        dist.append(h.distance(seg.x, sec = Cell.basal[Bnum]))

    v_vec_dend = []
    for loc in Loc:
        v_vec_dend.append(h.Vector())
        v_vec_dend[-1].record(Cell.basal[Bnum](loc)._ref_v)
    ###########################################
    ### Run & Plot
    ### Be careful, vmax does not have value before run
    ###########################################
    h.celsius = 32 # 32
    h.v_init =  -73.6927850677
    h.init()
    h.tstop = 300
    h.run()

#    pdb.set_trace()   #Debugging
    # print v_vec_soma[-1]
    # plt.clf()
    # plt.close()
    # plt.figure(figsize = (16, 6), dpi = 100)
    # plt.plot(t_vec, v_vec_soma, label = 'soma(0.5)', color = 'black')
    # for index, loc in enumerate(Loc):
    #     plt.plot(t_vec, v_vec_dend[index], label = 'dend-loc'+"{0:.2f}".format(loc))
    # plt.ylim([-90, 40])
    # plt.xlim([0, 300])
    # plt.legend(loc = 'upper right')
    # plt.ylabel('mV')
    # plt.xlabel('Time (ms)')
    # plt.title ("bAP")
    # save(title, directory, ext="png", close=True, verbose=True)

    #######################
    data = Vividict()
    data['Bnum'] = Bnum
    data['Loc'] = Loc
    data['dist'] = dist
    data['recording']['time'] = list(t_vec)
    data['recording']['soma']['voltage'] = list(v_vec_soma)
    for index, dist in enumerate(dist):
        data['recording']['dend']["{0:.2f}".format(dist)] = list(v_vec_dend[index])
    savejson(data, title, directory, ext = "json", verbose = False)

    if (TTX == False and Atype == False):
        return v_vec_soma

######################################################
if __name__ == "__main__":
    print("Running the model")
    start_time = time.time()
    for i in range(0,36):
        if i != 16:
            V = bAP(Bnum = i, TTX = False, Atype = False)
            bAP(Bnum = i, TTX = True, Atype = False, vec = V)
            bAP(Bnum = i, TTX = False, Atype = True)

    print("Finished.")
    print("--- %s seconds ---" % (time.time() - start_time))
