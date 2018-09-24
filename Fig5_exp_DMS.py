"""
Simulation code for Fig 5. - Model 1
Test the effects of different syanptic input locations
for the generation of plateau potential

Author: Peng Penny Gao
<penggao.1987@gmail.com>

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

h.load_file('stdrun.hoc') # for initialization

def random_2(low, high, size):
    time_random = np.linspace(low, high, size)
    np.random.shuffle(time_random)
    return time_random

################### Test the ratio of different repceptors

def Glu_Stim(Bnum = 34, TTX = False, Pool1_num = 9, Pool2_num = 9,
Beta = 0.067, Cdur = 1, Syn_w1 = 0.01, Syn_w2 = 0.01, Loc = [0.2, 0.6], DenLoc = 0.5):

    """
    Model the Glumate Stimulation.
    Model the Receptors in 2 pools:
        Pool 1: AMPA + NMDA (same synaptic weight, represent spine conductance)
        Pool 2: NMDA only (represent the extrasyanptic NMDARs)

    Parameters:
    -----------
    Bnum: the number of basal branch to explore
    TTX: True or False.
        True: setting all the sodium channel conductance to 0.
        False: default
    Pool1_num: syanptic AMPA/NMDA numbers
    Pool2_num: extrasyanptic NMDA numbers
    Beta: parameter of NMDA Receptors
    Cdur: parameter ofNMDA Receptors
    Syn_w1: the syanptic weight of AMPA/NMDA receptors in pool1
    Syn_w2: the syanptic weight of AMPA/NMDA receptors in pool2
    Loc: the stimulation location
    DenLoc: the targeted recording location on dendrite
    -----------
    Outputs:
        Figures: recording from soma and 3 different locations from basal dendrites
        json: soma and dendritc voltage recording and parameters info
    """
    Cell = CA229()
    timestr = time.strftime("%Y%m%d-%H%M")
    data = time.strftime("%m_%d")
    directory_root = "Fig5/DMS/"


    L1 = "{:.2f}".format(Loc[0])
    L2 = "{:.2f}".format(Loc[1])
    if (TTX == True):
        Cell.TTX()
        directory = directory_root + "B" + str(Bnum) + "/Loc" + L1 + "_" + L2 + "/TTX/"
        title =  "TTX_Pool1_"+ \
        str(Pool1_num) + "_Pool2_" + str(Pool2_num) + "_NMDA_Beta_" + \
        str(Beta) + "_NMDA_Cdur_" + str(Cdur) + "_Pool1_W_" + str(Syn_w1) + \
        "_Pool2_W_" + str(Syn_w2) + "_"+ timestr
    else:
        directory = directory_root + "B" + str(Bnum) + "/Loc" + L1 + "_" + L2 + "/N/"
        title = "Pool1_"+ \
        str(Pool1_num) + "_Pool2_" + str(Pool2_num) + "_NMDA_Beta_" + \
        str(Beta) + "_NMDA_Cdur_" + str(Cdur) + "_Pool1_W_" + str(Syn_w1) + \
        "_Pool2_W_" + str(Syn_w2) + "_"+ timestr

    ###########################################
    # Adding Pool 1
    ###########################################
    ##### AMPA
    SynAMPA = []
    nc_AMPA = []
    SynNMDA = []
    nc_NMDA = []

    loc1 = list(np.linspace(Loc[0], Loc[1], Pool1_num))
    ###########################################
    delay1 = random_2(10, 20 + int(Syn_w1*50), Pool1_num)
    ns = h.NetStim()
    ns.interval = 20
    ns.number = 1
    ns.start = 190
    ns.noise = 0

    for i in range(Pool1_num):
        ###########################
        # Adding AMPA
        SynAMPA.append(h.AMPA(Cell.basal[Bnum](loc1[i])))
        SynAMPA[-1].gmax = 0.05
        #SynAMPA1[-1].Beta = 0.28
        nc_AMPA.append(h.NetCon(ns, SynAMPA[i]))
        nc_AMPA[-1].delay = delay1[i]
        nc_AMPA[-1].weight[0] = Syn_w1
        ###########################
        #Adding NMDA
        SynNMDA.append(h.NMDA(Cell.basal[Bnum](loc1[i])))
        SynNMDA[-1].gmax = 0.005
        SynNMDA[-1].Beta = Beta
        SynNMDA[-1].Cdur = Cdur
        nc_NMDA.append(h.NetCon(ns, SynNMDA[i]))
        nc_NMDA[-1].delay = delay1[i]
        nc_NMDA[-1].weight[0] = Syn_w1

    ###########################################
    # Adding Pool 2
    ###########################################
    ExNMDA = []
    nc_ExNMDA = []

    loc2 = list(np.linspace(Loc[0], Loc[1], Pool2_num))
    delay2 = random_2(15, 25 + int(Syn_w2*60), Pool2_num)
    for i in range(Pool2_num):
        ###########################
        # Adding extrasyanptic NMDA
        ExNMDA.append(h.NMDA(Cell.basal[Bnum](loc2[i])))
        ExNMDA[-1].gmax = 0.005
        ExNMDA[-1].Beta = Beta
        ExNMDA[-1].Cdur = Cdur
        nc_ExNMDA.append(h.NetCon(ns, ExNMDA[i]))
        nc_ExNMDA[-1].delay = delay2[i]
        nc_ExNMDA[-1].weight[0] = Syn_w2

    ###########################################
    ### Recording
    ###########################################
    t_vec = h.Vector()
    t_vec.record(h._ref_t)
    v_vec_soma = h.Vector()
    v_vec_dend1 = h.Vector()
    v_vec_dend2 = h.Vector()
    v_vec_dend3 = h.Vector()
    v_vec_dend = h.Vector()

    v_vec_soma.record(Cell.soma[2](0.5)._ref_v)
    v_vec_dend1.record(Cell.basal[Bnum](0.8)._ref_v)
    v_vec_dend2.record(Cell.basal[Bnum](0.5)._ref_v)
    v_vec_dend3.record(Cell.basal[Bnum](0.3)._ref_v)
    v_vec_dend.record(Cell.basal[Bnum](DenLoc)._ref_v)


    ###########################################
    ### Run & Plot
    ###########################################
    h.celsius = 32
    h.v_init =  -73.6927850677
    h.init()
    h.tstop = 1000
    h.run()

#    pdb.set_trace()   #Debugging
    # plt.figure(figsize = (16, 6), dpi = 100)
    # plt.plot(t_vec, v_vec_soma, label = 'soma(0.5)', color = 'black')
    # plt.plot(t_vec, v_vec_dend1, label = 'bdend['+str(Bnum)+'](0.8)', color = 'red')
    # plt.plot(t_vec, v_vec_dend2, label = 'Basal['+str(Bnum)+'](0.5)', color = 'blue')
    # plt.plot(t_vec, v_vec_dend3, label = 'Basal['+str(Bnum)+'](0.3)', color = 'green')
    # plt.ylim([-90, 40])
    # plt.xlim([0, 700])
    # plt.legend(loc = 'best')
    # plt.ylabel('mV')
    # plt.xlabel('Time (ms)')
    # plt.title ("Glumate Receptor Activated Plateau Potential")
    #
    # save(title, directory, ext="png", close=True, verbose=True)


    data = Vividict()
    data['TTX'] = TTX
    data['SynAMPA']['num'] = Pool1_num
    data['SynAMPA']['locs'] = Loc
    data['SynAMPA']['weight'] = Syn_w1
    data['SynNMDA']['num'] = Pool1_num
    data['SynNMDA']['locs'] = Loc
    data['SynNMDA']['weight'] = Syn_w1
    data['SynNMDA']['Beta'] = Beta
    data['SynNMDA']['Cdur'] = Cdur
    data['ExNMDA']['num'] = Pool2_num
    data['ExNMDA']['locs'] = Loc
    data['ExNMDA']['weight'] = Syn_w2
    data['ExNMDA']['Beta'] = Beta
    data['ExNMDA']['Cdur'] = Cdur

    data['recording']['time'] = list(t_vec)
    data['recording']['soma']['voltage'] = list(v_vec_soma)
    data['recording']['basal']['voltage_0.8'] = list(v_vec_dend1)
    data['recording']['basal']['voltage_0.5'] = list(v_vec_dend2)
    data['recording']['basal']['voltage_0.3'] = list(v_vec_dend3)
    data['recording']['basal']['voltage_input'] = list(v_vec_dend)

    savejson(data, title, directory, ext = "json", verbose = False)

######################################################
if __name__ == "__main__":
    print("Running the model")
    start_time = time.time()
    Pool_num = 12
    weight = [0.9]
    # weight = [1.2, 1.5] # For generating multiple APs - Fig 5. D3
    # weight = [0.1, 0.3, 0.5, 0.7]  # For the demo traces

    basal_num = [15, 34, 14, 22, 25, 31]
    with open('data.json', 'r') as fp:
        data = json.load(fp)
    with open('dend_measure_data.json', 'r') as fp1:
        Ndata = json.load(fp1)

    for b in basal_num:
        loc = data[str(b)]
        DenLoc = Ndata[str(b)]
        for l1, l2 in zip(loc, DenLoc):
            for w in weight:
                Glu_Stim(b, False, Pool_num, Pool_num, 0.02, 10, w, w, l1, l2)
                Glu_Stim(b, True, Pool_num, Pool_num, 0.02, 10, w, w, l1, l2)


    print("Finished.")
    print("--- %s seconds ---" % (time.time() - start_time))
