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

h.load_file('stdrun.hoc') # for initialization



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
    ###########################################
    Cell = CA229()
    timestr = time.strftime("%Y%m%d-%H%M")
    data = time.strftime("%m_%d")
    directory = 'Data_' + data +'/'

    if (TTX == True):
        Cell.TTX()
        title = "TTX_Pool1_"+ str(Pool1_num) + "_Pool2_" + str(Pool2_num) + "_NMDA_Beta_" + \
            str(Beta) + "_NMDA_Cdur_"+str(Cdur)+ "_Pool1_W_" + str(Syn_w1) + \
            "_Pool2_W_" + str(Syn_w2) + "_"+ timestr + "_joe"
    else:
        title = "Pool1_"+ str(Pool1_num) + "_Pool2_" + str(Pool2_num) + "_NMDA_Beta_" + \
            str(Beta) + "_NMDA_Cdur_"+str(Cdur)+ "_Pool1_W_" + str(Syn_w1) + \
            "_Pool2_W_" + str(Syn_w2) + "_"+ timestr + "_joe"

    ##########

    glutAmp           = Syn_w1
    glutAmpExSynScale = Syn_w2 / Syn_w1
    glutAmpDecay      = 0.0 #5.0 # percent/um
    synLocMiddle      = (loc[0] + loc[1])/2
    synLocRadius      = synLocMiddle - loc[0] 
    initDelay         = 10.0
    synDelay          = 0.5 # ms/um
    exSynDelay        = 1.0 # ms/um

    branch_length     = 166.25942491682142 # CA229.basal[34].L 
    numSyns           = Pool1_num
    numExSyns         = Pool2_num
    glutAmp           = Syn_w1

    syn_locs = np.linspace(synLocMiddle-synLocRadius, synLocMiddle+synLocRadius, numSyns)
    syn_dists = branch_length * np.abs(syn_locs - synLocMiddle)
    syn_weights = glutAmp * (1 - syn_dists * glutAmpDecay/100)
    syn_weights = [weight if weight > 0.0 else 0.0 for weight in syn_weights]
    syn_delays = initDelay + (synDelay * syn_dists)

    exsyn_locs = np.linspace(synLocMiddle-synLocRadius, synLocMiddle+synLocRadius, numExSyns)
    exsyn_dists = branch_length * np.abs(exsyn_locs - synLocMiddle)
    exsyn_weights = glutAmpExSynScale * glutAmp * (1 - exsyn_dists * glutAmpDecay/100)
    exsyn_weights = [weight if weight > 0.0 else 0.0 for weight in exsyn_weights]
    exsyn_delays = initDelay + (exSynDelay * exsyn_dists)


    ###########################################
    # Adding Pool 1
    ###########################################
    ##### AMPA
    SynAMPA = []
    nc_AMPA = []
    SynNMDA = []
    nc_NMDA = []

    loc1 = list(np.linspace(Loc[0], Loc[1], Pool1_num))
    #delay1 = random_2(10, 50 + int(Syn_w1*50), Pool1_num)
    delay1 = syn_delays
    ns = h.NetStim()
    ns.interval = 20
    ns.number = 1
    ns.start = 190
    ns.noise = 0

    print
    print("delay1")
    print(delay1)
    print
    print("mean: %f" % (np.mean(delay1)))
    print("std : %f" % (np.std(delay1)))

    for i in range(Pool1_num):
        ###########################
        # Adding AMPA
        SynAMPA.append(h.AMPA(Cell.basal[34](loc1[i])))
        SynAMPA[-1].gmax = 0.04
        #SynAMPA1[-1].Beta = 0.28
        nc_AMPA.append(h.NetCon(ns, SynAMPA[i]))
        nc_AMPA[-1].delay = delay1[i] # delay1[i] #uniform(1,20)
        nc_AMPA[-1].weight[0] = syn_weights[i] # Syn_w1
        #nc_AMPA[-1].threshold = -20
        ###########################
        #Adding NMDA
        # SynNMDA.append(h.NMDA(Cell.basal[34](loc1[i])))
        # Using NMDAeee.mod file
        SynNMDA.append(h.NMDAeee(Cell.basal[34](loc1[i])))
        SynNMDA[-1].gmax = 0.01
        SynNMDA[-1].Beta = Beta
        SynNMDA[-1].Cdur = Cdur
        nc_NMDA.append(h.NetCon(ns, SynNMDA[i]))
        nc_NMDA[-1].delay = delay1[i] #uniform(1,20)
        nc_NMDA[-1].weight[0] = syn_weights[i] # Syn_w1

    ###########################################
    # Adding Pool 2
    ###########################################
    ExNMDA = []
    nc_ExNMDA = []

    loc2 = list(np.linspace(Loc[0], Loc[1], Pool2_num))
    #delay2 = random_2(15, 55 + int(Syn_w2*60), Pool2_num)
    delay2 = exsyn_delays
    
    print
    print("delay2")
    print(delay2)
    print
    print("mean: %f" % (np.mean(delay2)))
    print("std : %f" % (np.std(delay2)))

    for i in range(Pool2_num):
        ###########################
        # Adding extrasyanptic NMDA
        # ExNMDA.append(h.NMDA(Cell.basal[34](loc2[i])))
        # Using NMDAeee.mod file
        ExNMDA.append(h.NMDAeee(Cell.basal[34](loc2[i])))
        ExNMDA[-1].gmax = 0.01
        ExNMDA[-1].Beta = Beta
        ExNMDA[-1].Cdur = Cdur
        nc_ExNMDA.append(h.NetCon(ns, ExNMDA[i]))
        nc_ExNMDA[-1].delay = delay2[i] #uniform(1,20)
        nc_ExNMDA[-1].weight[0] = exsyn_weights[i] # Syn_w2 #(i/5.0)*Syn_w2

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
    ### Be careful, vmax does not have value before run
    ###########################################
    h.celsius = 32 # 32
    h.v_init =  -79.1863191308 #-81.0866900034 #-78.1162028163 #-67.3
    h.init()
    h.tstop = 1000
    h.run()

    plt.clf()
    plt.close()
    plt.figure(figsize = (16, 6), dpi = 100)
    plt.plot(t_vec, v_vec_soma, label = 'soma(0.5)', color = 'black')
    plt.plot(t_vec, v_vec_dend1, label = 'bdend[34](0.8)', color = 'red')
    plt.plot(t_vec, v_vec_dend2, label = 'Basal[34](0.5)', color = 'blue')
    plt.plot(t_vec, v_vec_dend3, label = 'Basal[34](0.3)', color = 'green')
    plt.ylim([-90, 40])
    plt.xlim([0, 800])
    plt.legend(loc = 'best')
    plt.ylabel('mV')
    plt.xlabel('Time (ms)')
    plt.title ("Glumate Receptor Activated Plateau Potential")

    save(title, directory, ext="png", close=True, verbose=True)

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
    # save(title1, directory, ext="png", close=True, verbose=True)


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
    data['recording']['soma']['ica'] = list(cai_soma)
    data['recording']['basal_34']['ica_0.3'] = list(cai_dend)

    savejson(data, title, directory, ext = "json", verbose = False)


######################################################
if __name__ == "__main__":
    print("Running the model")
    start_time = time.time()

    loc = [0.3, 0.6]
    weight = [0.8, 0.9, 1.0, 1.1, 1.2]
    
    for w in weight:
        
        Pool_num = 8 + int(20*w)
        
        #Glu_Stim(TTX, Pool1_num, Pool2_num, Beta, Cdur, Syn_w1, Syn_w2, Loc)
        Glu_Stim(False, Pool_num, Pool_num, 0.02, 50 + int(100*w), w, w, loc)
        Glu_Stim(True, Pool_num, Pool_num, 0.02, 50 + int(100*w), w, w, loc)

    print("Finished.")
    print("--- %s seconds ---" % (time.time() - start_time))
