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

def random_floats(low, high, size):
    return [np.random.uniform(low, high) for _ in xrange(size)]


def random_2(low, high, size):
    time_random = np.linspace(low, high, size)
    np.random.shuffle(time_random)
    return time_random

################### Test the ratio of different repceptors


def Glu_Stim(Bnum = 34, TTX = False,
amp = 0.1, dur = 3, Loc = 0.5):

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

    if (TTX == True):
        Cell.TTX()
        directory = 'Data_' + data +'/'
        title = "B_TTX_" + str(Bnum) + "_Loc_" + str(Loc) + "_amp_" + str(amp) + "_dur_" + str(dur) + "_"+ timestr
    else:
        directory = 'Data_' + data +'/'
        title = "B_" + str(Bnum) + "_Loc_" + str(Loc) + "_amp_" + str(amp) + "_dur_" + str(dur) + "_"+ timestr

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
    #spine ID
    # spineid = [ (60+5*i) for i in range(Pool1_num)]
    # loc1 = list(np.linspace(Loc[0], Loc[1], 10))
    ###########################################
    ###########################################
    ###########################################
    # Loc and time delay set up
#    loc1 = [0.5, 0.6, 0.7]*3
    #delay1 = [10, 13, 13]*3
#    delay1 = random_floats(10, 20, 3) + random_floats(13, 23, 6)
#    delay1=random_floats(10, 10 + int(100*Syn_w1), Pool1_num)
    #delay1 = random_2(10, 30, Pool1_num)
    # delay11 = [x+2 for x in delay1]
    Iclamp = h.IClamp(Cell.basal[Bnum](Loc))
    Iclamp.dur = dur
    Iclamp.amp = amp
    Iclamp.delay = 200


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
    plt.plot(t_vec, v_vec_dend1, label = 'Basal['+str(Bnum)+'](0.8)', color = 'red')
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
    data['Loc'] = Loc

    # data['SynNMDA']['Beta'] = Beta
    # data['SynNMDA']['Cdur'] = Cdur

    # data['ExNMDA']['Beta'] = Beta
    # data['ExNMDA']['Cdur'] = Cdur

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


    # basal_num = [15, 34, 14, 22, 25, 31]
    basal_num = [34]
    # loc = [[0.5, 0.6]]
    loc = [0.15, 0.25, 0.35, 0.45, 0.55, 0.65, 0.75, 0.85, 0.95]
    for b in basal_num:
        for l in loc:
            Glu_Stim(b, False, 0.2, 200, l)
                # Glu_Stim(b, True, Pool_num, Pool_num, 0.02, 10, w, w, l)


    print("Finished.")
    print("--- %s seconds ---" % (time.time() - start_time))
