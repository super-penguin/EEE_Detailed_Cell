"""
Test the effects of different syanptic inputs in the detailed PFC L5 neuron
The orginal model is from
https://senselab.med.yale.edu/ModelDB/ShowModel.cshtml?model=117207&file=/acker_antic/Model/CA%20229.hoc#tabs-2
Modified by : Peng (Penny) Gao <penggao.1987@gmail.com>

"""

from CA229_PFC import *
import matplotlib.pyplot as plt
from neuron import h
import numpy as np
from utils import *
import json
import itertools
import time
import pdb     # For python debugging
from random import *


################### Test the ratio of different repceptors


def Glu_Stim(Pool1_num = 30, Pool2_num = 2, Beta = 0.067, Cdur = 1, Syn_w1 = 0.01, Syn_w2 = 0.01):
    """
    Model the Glumate Stimulation.
    Model the Receptors in 2 pools:
        Pool 1: AMPA + NMDA (same synaptic weight, represent spine conductance)
        Pool 2: NMDA only (represent the extrasyanptic NMDARs)

    """

    Cell = CA229()
    Cell.init_once()
    #distKASD(Cell.basal[34], somaKA)
    #TTX()
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

    loc1 = list(np.linspace(0.5, 0.7, Pool1_num))

    ns = h.NetStim()
    ns.interval = 20
    ns.number = 1
    ns.start = 60
    ns.noise = 0

    for i in range(Pool1_num):
        ###########################
        # Adding AMPA
        SynAMPA.append(h.AMPA(Cell.basal[34](loc1[i])))
        SynAMPA[-1].gmax = 0.1
        #SynAMPA1[-1].Beta = 0.28
        nc_AMPA.append(h.NetCon(ns, SynAMPA[i]))
        nc_AMPA[-1].delay = 10 #uniform(1,20)
        nc_AMPA[-1].weight[0] = Syn_w1
        #nc_AMPA[-1].threshold = -20
        ###########################
        # Adding NMDA
        SynNMDA.append(h.NMDA(Cell.basal[34](loc1[i])))
        h.gmax_NMDA = 0.05
        SynNMDA[-1].Beta = Beta
        SynNMDA[-1].Cdur = Cdur
        nc_NMDA.append(h.NetCon(ns, SynNMDA[i]))
        nc_NMDA[-1].delay = 10 #uniform(1,20)
        nc_NMDA[-1].weight[0] = Syn_w1

    ###########################################
    # Adding Pool 2
    ###########################################
    ExNMDA = []
    nc_ExNMDA = []

    loc2 = list(np.linspace(0.4, 0.7, Pool2_num))

    for i in range(Pool2_num):
        ###########################
        # Adding extrasyanptic NMDA
        ExNMDA.append(h.NMDA(Cell.basal[34](loc2[i])))
        h.gmax_NMDA = 0.05
        ExNMDA[-1].Beta = Beta
        ExNMDA[-1].Cdur = Cdur
        nc_ExNMDA.append(h.NetCon(ns, ExNMDA[i]))
        nc_ExNMDA[-1].delay = 10 #uniform(1,20)
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
    v_vec_dend1.record(Cell.basal[34](0.8)._ref_v)
    v_vec_dend2.record(Cell.basal[34](0.5)._ref_v)
    v_vec_dend3.record(Cell.basal[34](0.3)._ref_v)
    #v_vec_dend2.record(postCell.basal[8](0.9)._ref_v)
    # basal[8](0.9) is about the same distance from soma as basal[34](0.6)
    # They are both about ~150 um from soma[0]


    ###########################################
    ### Run & Plot
    ### Be careful, vmax does not have value before run
    ###########################################
    h.celsius = 32
    h.v_init = -67.3
    h.init()
    h.tstop = 1000
    h.run()

#    pdb.set_trace()   #Debugging

    plt.figure(figsize = (16, 6), dpi = 100)
    plt.plot(t_vec, v_vec_soma, label = 'soma(0.5)', color = 'black')
    plt.plot(t_vec, v_vec_dend1, label = 'bdend[34](0.8)', color = 'red')
    plt.plot(t_vec, v_vec_dend2, label = 'Basal[34](0.5)', color = 'blue')
    plt.plot(t_vec, v_vec_dend3, label = 'Basal[34](0.3)', color = 'green')
    plt.ylim([-80, 60])
    plt.xlim([0, 1000])
    plt.legend(loc = 'best')
    plt.ylabel('mV')
    plt.xlabel('Time (ms)')
    plt.title ("Glumate Receptor Activated Plateau Potential")


    timestr = time.strftime("%H%M")
    title = "Pool1_"+ str(Pool1_num) + "_Pool2_" + str(Pool2_num) + "_NMDA_Beta_" + \
    str(Beta) + "_NMDA_Cdur_"+str(Cdur)+ "_Pool1_W_" + str(Syn_w1) + \
    "_Pool2_W_" + str(Syn_w2) + "_"+ timestr
    save(title, ext="png", close=True, verbose=True)


    data = Vividict()
    data['SynAMPA']['num'] = Pool1_num
    data['SynAMPA']['locs'] = loc1
    data['SynAMPA']['weight'] = Syn_w1
    data['SynNMDA']['num'] = Pool1_num
    data['SynNMDA']['locs'] = loc1
    data['SynNMDA']['weight'] = Syn_w1
    data['SynNMDA']['Beta'] = Beta
    data['SynNMDA']['Cdur'] = Cdur
    data['ExNMDA']['num'] = Pool2_num
    data['ExNMDA']['locs'] = loc2
    data['ExNMDA']['weight'] = Syn_w2
    data['ExNMDA']['Beta'] = Beta
    data['ExNMDA']['Cdur'] = Cdur

    data['recording']['time'] = list(t_vec)
    data['recording']['soma']['voltage'] = list(v_vec_soma)
    data['recording']['basal_34']['voltage_0.8'] = list(v_vec_dend1)
    data['recording']['basal_34']['voltage_0.5'] = list(v_vec_dend2)
    data['recording']['basal_34']['voltage_0.3'] = list(v_vec_dend3)

    savejson(data, title, ext = "json", verbose = False)



######################################################
if __name__ == "__main__":
    print("Running the model")

    Pool1_num = 8
    Pool2_num = 8
#    Syn_w1 = 0.01
#    Syn_w2 = 0.01
#    Beta = [0.005, 0.01, 0.03, 0.05]
#    Cdur = [1,10]
    weight = np.linspace(0.01, 0.5, 10)
#    for a in ratio:
    for w in weight:
#            for c in Beta:
#                for d in Cdur:
        Glu_Stim(Pool1_num, Pool2_num, 0.03, 100*w, w, w)

    print("Finished.")
