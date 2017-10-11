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


def Synaptic_Input_1Stim(stim_num_AMPA = 30, stim_num_NMDA = 2, Beta = 0.067, Cdur = 1, Syn_w = 0.01):
    """
    Need to add description here!!!
    Test glutamatergic inputs: AMPA and NMDA
    """

    postCell = CA229()
    postCell.init_once()
    #distKASD(postCell.basal[34], somaKA)
    #TTX()
    ###########################################
    # Syanptic weights
    # --- Need to confirm
    ###########################################

    ampaweight = Syn_w #0.00058
    #Pyramidal to pyramidal AMPA conductance (Wang,Gao,2000).

    nmdaweight = Syn_w
    #Pyramidal to pyramidal NMDA conductance, for 1.1 iNMDA-to-iAMPA ratio (Wang,Gao,2000).
    #For ratio 0.9 use: 0.16/For ratio 1.3 use:0.25

    ###########################################
    # Adding Syanpses
    ###########################################
    ##### AMPA
    SynAMPA = []
    nc_AMPA = []

    loc_AMPA = list(np.linspace(0.4, 0.7, stim_num_AMPA))

    ns = h.NetStim()
    ns.interval = 20
    ns.number = 1
    ns.start = 60
    ns.noise = 0

    for i in range(stim_num_AMPA):
        SynAMPA.append(h.AMPA(postCell.basal[34](loc_AMPA[i])))
        SynAMPA[-1].gmax = 0.2
        #SynAMPA1[-1].Beta = 0.28
        nc_AMPA.append(h.NetCon(ns, SynAMPA[i]))
        nc_AMPA[-1].delay = 10 #uniform(1,20)
        nc_AMPA[-1].weight[0] = ampaweight
        nc_AMPA[-1].threshold = -20

    ##### NMDA
    SynNMDA = []
    nc_NMDA = []
    loc_NMDA = list(np.linspace(0.4, 0.7, stim_num_NMDA))


    for i in range(stim_num_NMDA):
        SynNMDA.append(h.NMDA(postCell.basal[34](loc_NMDA[i])))
        SynNMDA[-1].gmax = 0.1
        SynNMDA[-1].Beta = Beta
        SynNMDA[-1].Cdur = Cdur
        nc_NMDA.append(h.NetCon(ns, SynNMDA[i]))
        nc_NMDA[-1].delay = 10 #uniform(1,20)
        nc_NMDA[-1].weight[0] = nmdaweight

    ###########################################
    ### Recording
    ###########################################
    t_vec = h.Vector()
    t_vec.record(h._ref_t)
    v_vec_soma = h.Vector()
    v_vec_dend1 = h.Vector()
    v_vec_dend2 = h.Vector()
    v_vec_dend3 = h.Vector()

    v_vec_soma.record(postCell.soma[2](0.5)._ref_v)
    v_vec_dend1.record(postCell.basal[34](0.8)._ref_v)
    v_vec_dend2.record(postCell.basal[34](0.5)._ref_v)
    v_vec_dend3.record(postCell.basal[34](0.3)._ref_v)
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


    timestr = time.strftime("%Y%m%d-%H%M%S")
    title = "AMPA_"+ str(stim_num_AMPA) + "_NMDA_" + str(stim_num_NMDA) + "_NMDA_Beta_" + \
    str(Beta) + "_NMDA_Cdur_"+str(Cdur)+ "_Syn_Weight_" + str(Syn_w) + "_"+ timestr
    save(title, ext="png", close=True, verbose=True)


    data = Vividict()
    data['AMPA']['num'] = stim_num_AMPA
    data['AMPA']['locs'] = loc_AMPA
    data['AMPA']['weight'] = ampaweight
    data['NMDA']['num'] = stim_num_NMDA
    data['NMDA']['locs'] = loc_NMDA
    data['NMDA']['weight'] = nmdaweight
    data['NMDA']['Beta'] = Beta
    data['NMDA']['Cdur'] = Cdur
    data['recording']['time'] = list(t_vec)
    data['recording']['soma']['voltage'] = list(v_vec_soma)
    data['recording']['basal_34']['voltage_0.8'] = list(v_vec_dend1)
    data['recording']['basal_34']['voltage_0.5'] = list(v_vec_dend2)
    data['recording']['basal_34']['voltage_0.3'] = list(v_vec_dend3)

    savejson(data, title, ext = "json", verbose = False)



######################################################
if __name__ == "__main__":
    print("Running the model")

#    AMPA_num = [x for x in range (20, 101, 20)]

#    ratio = [1,2]
#    Syn_num = [x for x in range(3, 31, 3)]

#    Beta = [0.005, 0.01, 0.03, 0.05]
#    Cdur = [1,10]
    weight = np.linspace(0.2, 0.4, 20)
#    for a in ratio:
    for w in weight:
#            for c in Beta:
#                for d in Cdur:
        Synaptic_Input_1Stim(8, 8, 0.03, 1, w)

    print("Finished.")
