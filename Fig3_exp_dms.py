"""
Test the effects of different syanptic inputs in the detailed PFC L5 neuron
to generate plateau potential

The orginal model is from
https://senselab.med.yale.edu/ModelDB/ShowModel.cshtml?model=117207&file=/acker_antic/Model/CA%20229.hoc#tabs-2
Modified by : Peng Penny Gao <penggao.1987@gmail.com>

Run simulation with NMDA.mod file - DMS model
"""
import CA229 as de # from CA229 import *
import matplotlib.pyplot as plt
from neuron import h
import numpy as np
import utils as ut #from utils import *
import json
import itertools
import time
# import pdb     # For python debugging
#from random import *

h.load_file('stdrun.hoc') # for initialization

##############################
# Function to determine the randomness of activation time of AMPA and NMDA
# Uniform random seen in Fig 2. E1
# Remove the seed to get true randomness
def random_2(low, high, size):
    time_random = np.linspace(low, high, size)
    np.random.seed(10)
    np.random.shuffle(time_random)
    return time_random

# Alpha random seen in Fig 2. E2
def random_beta(low, high, size):
    time_random = np.random.beta(2, 8, size=size)
    np.random.seed(10)
    time_random = (high - low)*time_random + low
    return time_random

################### Test the ratio of different repceptors

def Glu_Stim(TTX = False, Pool1_num = 9, Pool2_num = 9, Beta = 0.067,
Cdur = 1, Syn_w1 = 0.01, Syn_w2 = 0.01, Loc = [0.2, 0.6]):
    """
    Model the Glumate Stimulation.
    Model the Receptors in 2 pools:
        Pool 1: AMPA + NMDA (same synaptic weight, represent spine conductance)
        Pool 2: NMDA only (represent the extrasyanptic NMDARs)

    Parameters:
    -----------
    TTX: True or False.
        True: setting all the sodium channel conductance to 0 to mimic
              TTX application in experiments
        False: default
    Pool1_num: syanptic AMPA/NMDA numbers
    Pool2_num: extrasyanptic NMDA numbers
    Beta: parameter for NMDA Receptors
    Cdur: parameter for NMDA Receptors
    Syn_w1: the syanptic weight of AMPA/NMDA receptors in pool1
    Syn_w2: the syanptic weight of AMPA/NMDA receptors in pool2
    Loc: the stimulation location
    -----------
    Outputs:
        Figures: recording from soma and 3 different locations from basal dendrites
        json: soma and dendritc voltage recording and parameters info
    """
    Cell = de.CA229()
    # Can adjust channel conductance ratio here:
    # eg. Cell = CA229(KA_ratio = 0.5)
    ###########################################
    timestr = time.strftime("%H%M")
    data = time.strftime("%m_%d")
    # directory = 'Data_' + data +'/'
    directory_root = 'Fig3/'
    directory = directory_root + 'DMS/Plot/'
    # directory = directory_root + 'DMS/Analysis/'

    if (TTX == True):
        Cell.TTX()
        title = "TTX_Pool1_"+ str(Pool1_num) + "_Pool2_" + str(Pool2_num) + "_NMDA_Beta_" + \
            str(Beta) + "_NMDA_Cdur_"+str(Cdur)+ "_Pool1_W_" + str(Syn_w1) + \
            "_Pool2_W_" + str(Syn_w2) + "_"+ timestr
    else:
        title = "Pool1_"+ str(Pool1_num) + "_Pool2_" + str(Pool2_num) + "_NMDA_Beta_" + \
            str(Beta) + "_NMDA_Cdur_"+str(Cdur)+ "_Pool1_W_" + str(Syn_w1) + \
            "_Pool2_W_" + str(Syn_w2) + "_"+ timestr

    ###########################################
    # Adding Pool 1
    ###########################################
    ##### AMPA
    SynAMPA = []
    nc_AMPA = []
    SynNMDA = []
    nc_NMDA = []

    ###########################################
    loc1 = list(np.linspace(Loc[0], Loc[1], Pool1_num))
    ###########################################
    # Loc and time delay set up
    delay1 = random_2(10, 50 + int(Syn_w1*50), Pool1_num)
    # delay1 = random_beta(10, 50 + int(Syn_w1*50), Pool1_num)
    ns = h.NetStim()
    ns.interval = 20
    ns.number = 1
    ns.start = 190
    ns.noise = 0
    ###########################################
    for i in range(Pool1_num):
        ###########################
        # Adding AMPA
        SynAMPA.append(h.AMPA(Cell.basal[34](loc1[i])))
        SynAMPA[-1].gmax = 0.05
        nc_AMPA.append(h.NetCon(ns, SynAMPA[i]))
        nc_AMPA[-1].delay = delay1[i]
        nc_AMPA[-1].weight[0] = Syn_w1
        ###########################
        #Adding NMDA
        SynNMDA.append(h.NMDA(Cell.basal[34](loc1[i])))
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
#    delay2 = list(np.linspace(5, 10, Pool2_num))
    delay2 = random_2(15, 55 + int(Syn_w2*60), Pool2_num)
    # delay2 = random_beta(15, 55 + int(Syn_w2*60), Pool2_num)
    for i in range(Pool2_num):
        ###########################
        # Adding extrasyanptic NMDA
        ExNMDA.append(h.NMDA(Cell.basal[34](loc2[i])))
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
    cai_soma = h.Vector()
    cai_dend = h.Vector()

    v_vec_soma.record(Cell.soma[2](0.5)._ref_v)
    v_vec_dend1.record(Cell.basal[34](0.8)._ref_v)
    v_vec_dend2.record(Cell.basal[34](0.5)._ref_v)
    v_vec_dend3.record(Cell.basal[34](0.3)._ref_v)
    cai_soma.record(Cell.soma[2](0.5)._ref_cai)
    cai_dend.record(Cell.basal[34](0.3)._ref_cai)


    ###########################################
    ### Run & Plot
    ###########################################
    h.celsius = 32
    h.v_init =  -73.6927850677
    h.init()
    h.tstop = 1000
    h.run()

#    pdb.set_trace()   #Debugging
    # print v_vec_soma[-1]
    # plt.clf()
    # plt.close()
    # plt.figure(figsize = (16, 6), dpi = 100)
    # plt.plot(t_vec, v_vec_soma, label = 'soma(0.5)', color = 'black')
    # plt.plot(t_vec, v_vec_dend1, label = 'bdend[34](0.8)', color = 'red')
    # plt.plot(t_vec, v_vec_dend2, label = 'Basal[34](0.5)', color = 'blue')
    # plt.plot(t_vec, v_vec_dend3, label = 'Basal[34](0.3)', color = 'green')
    # plt.ylim([-90, 40])
    # plt.xlim([0, 800])
    # plt.legend(loc = 'best')
    # plt.ylabel('mV')
    # plt.xlabel('Time (ms)')
    # plt.title ("Glumate Receptor Activated Plateau Potential")
    #
    # save(title, directory, ext="png", close=True, verbose=True)

    #######################
    # Plot the intracelluar calcium concentration
    # plt.clf()
    # plt.close()
    # plt.figure(figsize = (16, 6), dpi = 100)
    # plt.plot(t_vec, cai_soma, label = 'soma(0.5)', color = 'black')
    # #plt.plot(t_vec, cai_dend, label = 'bdend[34](0.3)', color = 'red')
    #
    # # plt.ylim([-90, 60])
    # plt.xlim([0, 800])
    # plt.legend(loc = 'best')
    # plt.ylabel('mM')
    # plt.xlabel('Time (ms)')
    # plt.title ("Calcium concentration")
    # title1 = "Calcium_" + title
    # ut.save(title1, directory, ext="png", close=True, verbose=True)

    data = ut.Vividict()
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
    data['recording']['soma']['ica'] = list(cai_soma)
    data['recording']['basal_34']['ica_0.3'] = list(cai_dend)


    ut.savejson(data, title, directory, ext = "json", verbose = False)

######################################################
if __name__ == "__main__":
    print("Running the model")
    start_time = time.time()

    loc = [0.25, 0.6]
    # Plot weight for Fig2
    weight = [0.1, 0.15, 0.20, 0.25, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8]
    # Analysis weight for Fig2
    # weight = [0.1, 0.2, 0.21, 0.22, 0.23, 0.24, 0.25, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]

    for w in weight:
        Pool_num = 8 + int(20*w)
        Glu_Stim(False, Pool_num, Pool_num, 0.02, 50 + int(100*w), w, w, loc)
        # Glu_Stim(True, Pool_num, Pool_num, 0.02, 50 + int(100*w), w, w, loc)
    print("Finished.")
    print("--- %s seconds ---" % (time.time() - start_time))
