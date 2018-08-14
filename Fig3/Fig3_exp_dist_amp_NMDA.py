"""
Test the effects of different syanptic inputs in the detailed PFC L5 neuron
The orginal model is from
https://senselab.med.yale.edu/ModelDB/ShowModel.cshtml?model=117207&file=/acker_antic/Model/CA%20229.hoc#tabs-2
Modified by : Peng (Penny) Gao <penggao.1987@gmail.com>

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

def random_floats(low, high, size):
    return [np.random.uniform(low, high) for _ in xrange(size)]


def random_2(low, high, size):
    time_random = np.linspace(low, high, size)
    np.random.shuffle(time_random)
    return time_random


# def stim_loc(Branch):
#     nseg = Branch.nseg
#     loc_vec = []
#     dist_vec = []
#     for seg in Branch.allseg():
#         loc_vec.append(seg.x)
#         dist_vec.append(h.distance(seg.x, sec = Branch))
#     length = dist_vec[-1] - dist_vec[0]
#     each_len = math.floor((1.0/nseg) * 100)/100.0
#     loc = []
#     if each_len > 10:
#         for i in range(1, len(loc_vec)):
#             temp_loc = [loc_vec[i] - each_len, loc_vec[i] + each_len]
#             loc.append(temp_loc)
#     elif each_len <= 10:
#         for i in range(1, len(loc_vec)-2, 2):
#             temp_loc =[loc_vec[i], loc_vec[i+2]]
#             loc.append(temp_loc)
#     return loc

################### Test the ratio of different repceptors


def Glu_Stim(Bnum = 34, TTX = False, Pool1_num = 9, Pool2_num = 9,
Beta = 0.067, Cdur = 1, Syn_w1 = 0.01, Syn_w2 = 0.01, Loc = [0.2, 0.6]):

    """
    Model the Glumate Stimulation.
    Model the Receptors in 2 pools:
        Pool 1: AMPA + NMDA (same synaptic weight, represent spine conductance)
        Pool 2: NMDA only (represent the extrasyanptic NMDARs)

    Parameters:
    -----------
    Bnum: the number of basal branch to explore
    TTX: True or False.
        True: setting all the calcium channel conductance to 0.
        False: default
    Pool1_num: syanptic AMPA/NMDA numbers
    Pool2_num: extrasyanptic NMDA numbers
    Beta: NMDA Receptors
    Cdur: NMDA Receptors
    Syn_w1: the syanptic weight of AMPA/NMDA receptors in pool1
    Syn_w2: the syanptic weight of AMPA/NMDA receptors in pool2
    Loc: the stimulation location
    -----------
    Outputs:
        Figures: recording from soma and 3 different locations from basal dendrites
        json: soma and dendritc voltage recording and parameters info
    """
    Cell = CA229()
    timestr = time.strftime("%Y%m%d-%H%M")
    data = time.strftime("%m_%d")

    L1 = "{:.2f}".format(Loc[0])
    L2 = "{:.2f}".format(Loc[1])
    if (TTX == True):
        Cell.TTX()
        directory = 'Data_' + data +'/' + "B" + str(Bnum) + "/Loc" + L1 + "_" + L2 + "/TTX/"
        title =  "TTX_Pool1_"+ \
        str(Pool1_num) + "_Pool2_" + str(Pool2_num) + "_NMDA_Beta_" + \
        str(Beta) + "_NMDA_Cdur_" + str(Cdur) + "_Pool1_W_" + str(Syn_w1) + \
        "_Pool2_W_" + str(Syn_w2) + "_"+ timestr
    else:
        directory = 'Data_' + data +'/' + "B" + str(Bnum) + "/Loc" + L1 + "_" + L2 + "/N/"
        title = "Pool1_"+ \
        str(Pool1_num) + "_Pool2_" + str(Pool2_num) + "_NMDA_Beta_" + \
        str(Beta) + "_NMDA_Cdur_" + str(Cdur) + "_Pool1_W_" + str(Syn_w1) + \
        "_Pool2_W_" + str(Syn_w2) + "_"+ timestr

    ###########################################
    # Syanptic weights
    # --- Need to confirm
    ###########################################

    #ampaweight = Syn_w #0.00058
    #Pyramidal to pyramidal AMPA conductance (Wang,Gao,2000).

    #nmdaweight = Syn_w
    #Pyramidal to pyramidal NMDA conductance, for 1.1 iNMDA-to-iAMPA ratio (Wang,Gao,2000).
    #For ratio 0.9 use: 0.16/For ratio 1.3 use:0.25

    ###########################################
    # Adding Pool 1
    ###########################################
    ##### AMPA
    SynAMPA = []
    nc_AMPA = []
    SynNMDA = []
    nc_NMDA = []

    #spine ID
    # spineid = [ (60+5*i) for i in range(Pool1_num)]
    loc1 = list(np.linspace(Loc[0], Loc[1], Pool1_num))
    ###########################################
    ###########################################
    ###########################################
    # Loc and time delay set up
#    loc1 = [0.5, 0.6, 0.7]*3
    #delay1 = [10, 13, 13]*3
#    delay1 = random_floats(10, 20, 3) + random_floats(13, 23, 6)
#    delay1=random_floats(10, 10 + int(100*Syn_w1), Pool1_num)
    delay1 = random_2(10, 20 + int(Syn_w1*50), Pool1_num)
    # delay1 = random_2(10, 30, Pool1_num)
    # delay11 = [x+2 for x in delay1]
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
        nc_AMPA[-1].delay = delay1[i] # delay1[i] #uniform(1,20)
        nc_AMPA[-1].weight[0] = Syn_w1
        #nc_AMPA[-1].threshold = -20
        ###########################
        #Adding NMDA
        SynNMDA.append(h.NMDA(Cell.basal[Bnum](loc1[i])))
        SynNMDA[-1].gmax = 0.005
        SynNMDA[-1].Beta = Beta
        SynNMDA[-1].Cdur = Cdur
        nc_NMDA.append(h.NetCon(ns, SynNMDA[i]))
        nc_NMDA[-1].delay = delay1[i] #uniform(1,20)
        nc_NMDA[-1].weight[0] = Syn_w1

    ###########################################
    # Adding Pool 2
    ###########################################
    ExNMDA = []
    nc_ExNMDA = []

    loc2 = list(np.linspace(Loc[0], Loc[1], Pool2_num))
#    delay2 = list(np.linspace(20, 20 + int(150*Syn_w2), Pool2_num))
    delay2 = random_2(15, 25 + int(Syn_w2*60), Pool2_num)
    # delay2 = random_2(10, 150 + int(100*Syn_w2), Pool2_num)
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

    v_vec_soma.record(Cell.soma[2](0.5)._ref_v)
    v_vec_dend1.record(Cell.basal[Bnum](0.8)._ref_v)
    v_vec_dend2.record(Cell.basal[Bnum](0.5)._ref_v)
    v_vec_dend3.record(Cell.basal[Bnum](0.3)._ref_v)


    ###########################################
    ### Run & Plot
    ### Be careful, vmax does not have value before run
    ###########################################
    h.celsius = 32 # 32
    h.v_init =  -73.6927850677 #-78.1162028163 #-67.3
    h.init()
    h.tstop = 1000
    h.run()

#    pdb.set_trace()   #Debugging
    plt.figure(figsize = (16, 6), dpi = 100)
    plt.plot(t_vec, v_vec_soma, label = 'soma(0.5)', color = 'black')
    plt.plot(t_vec, v_vec_dend1, label = 'bdend['+str(Bnum)+'](0.8)', color = 'red')
    plt.plot(t_vec, v_vec_dend2, label = 'Basal['+str(Bnum)+'](0.5)', color = 'blue')
    plt.plot(t_vec, v_vec_dend3, label = 'Basal['+str(Bnum)+'](0.3)', color = 'green')
    plt.ylim([-90, 40])
    plt.xlim([0, 700])
    plt.legend(loc = 'best')
    plt.ylabel('mV')
    plt.xlabel('Time (ms)')
    plt.title ("Glumate Receptor Activated Plateau Potential")

    save(title, directory, ext="png", close=True, verbose=True)


    data = Vividict()
    data['TTX'] = TTX
    # data['TTX'] = N
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

    savejson(data, title, directory, ext = "json", verbose = False)

######################################################
if __name__ == "__main__":
    print("Running the model")
    start_time = time.time()
    Pool_num = 12
    weight = [0.1, 0.3, 0.5, 0.7]
    # weight = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8]
    # weight = [0.05, 0.055, 0.06, 0.065, 0.07, 0.075, 0.08, 0.085, 0.09, 0.095, 0.1,
    # 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1]
    #weight = [0.08]
    # basal_num = [15]
    basal_num = [15, 34, 14, 22, 25, 31]
    with open('data.json', 'r') as fp:
        data = json.load(fp)

    for b in basal_num:
        loc = data[str(b)]
        for l in loc:
            for w in weight:
                # Pool_num = 8
                Glu_Stim(b, False, Pool_num, Pool_num, 0.02, 10, w, w, l)
                Glu_Stim(b, True, Pool_num, Pool_num, 0.02, 10, w, w, l)


    print("Finished.")
    print("--- %s seconds ---" % (time.time() - start_time))
