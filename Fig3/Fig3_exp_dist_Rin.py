"""
Test the effects of different syanptic inputs in the detailed PFC L5 neuron
The orginal model is from
https://senselab.med.yale.edu/ModelDB/ShowModel.cshtml?model=117207&file=/acker_antic/Model/CA%20229.hoc#tabs-2
Modified by : Peng (Penny) Gao <penggao.1987@gmail.com>
For Major's model, same setting need a little bit bigger input strength to
measure the plateau amplitude and duration.
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


def Cur_Stim(Bnum = 34, TTX = False, dur = 100, amp = 0.5, Loc = 0.6):

    """
    """
    Cell = CA229()
    timestr = time.strftime("%Y%m%d-%H%M")
    data = time.strftime("%m_%d")

    L = "{:.2f}".format(Loc)
    if (TTX == True):
        Cell.TTX()
        directory = 'Data_' + data +'/' + "B" + str(Bnum) + "/Loc" + L + "/TTX/"
        title =  "TTX_Current_injection" + "_"+ timestr
    else:
        directory = 'Data_' + data +'/' + "B" + str(Bnum) + "/Loc" + L + "/N/"
        title = "Current_injection" + "_"+ timestr

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
    v_vec_dend1.record(Cell.basal[Bnum](Loc)._ref_v)

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
    plt.plot(t_vec, v_vec_dend1, label = 'Basal['+str(Bnum)+']'+str(Loc), color = 'red')
    plt.ylim([-90, 40])
    plt.xlim([0, 700])
    plt.legend(loc = 'best')
    plt.ylabel('mV')
    plt.xlabel('Time (ms)')
    plt.title ("Current injection")

    save(title, directory, ext="png", close=True, verbose=True)


    data = Vividict()
    data['TTX'] = TTX
    # data['TTX'] = N
    data['curr_dur'] = dur
    data['curr_amp'] = amp
    data['curr_loc'] = Loc
    # data['ExNMDA']['Beta'] = Beta
    # data['ExNMDA']['Cdur'] = Cdur

    data['recording']['time'] = list(t_vec)
    data['recording']['soma']['voltage'] = list(v_vec_soma)
    data['recording']['basal']['voltage_'+str(Loc)] = list(v_vec_dend1)

    savejson(data, title, directory, ext = "json", verbose = False)

######################################################
if __name__ == "__main__":
    print("Running the model")
    start_time = time.time()
    # basal_num = [15]
    basal_num = [34, 14, 22, 25, 31]
    with open('curr_inj_loc.json', 'r') as fp:
        data = json.load(fp)

    for b in basal_num:
        loc = data[str(b)]
        for l in loc:
            if l != 0.0 and l!= 1.0:
                # Cur_Stim(b, True, 100, 0.1, l)
                Cur_Stim(b, False, 100, 0.1, l)


    print("Finished.")
    print("--- %s seconds ---" % (time.time() - start_time))
