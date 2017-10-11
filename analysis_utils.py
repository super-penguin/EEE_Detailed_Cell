"""
The analysis functions for EPSPs stimulation data.
ADD MORE HERE


Author: Peng (Penny) Gao
penggao.1987@gmail.com
"""

import json
import matplotlib.pyplot as plt
from pprint import pprint
import os
import numpy as np
import pandas as pd
import seaborn as sns   # nice plotting


########################################
### Function: to measure the plateau duration
########################################


def mean_platdur(data, thresh=5):
    """Measures plateau duration (time volt trace is above baseline + thresh)"""
    baseline = np.mean(data[1000:2000])
    # Make sure dt = 0.025 and there is no stimulation for the first 50 ms
    stable = data[2000:]
    above = [val for val in stable if val > (baseline + thresh)]
    #platamp = np.mean([val - baseline for val in above])
    platdur = 0.025*len(above)
    return platdur

########################################
### Function: to calculate the number of Spikes
########################################

def spike_count(data, thresh = 0):
    """Measure the number of Spikes

    Parameters:
    -----------
    data: list
        The electrical recording data from soma in the CA229_PFC model.
        It was recorded in h.Vector() originally, then saved as list into json
        file duirng the batch processing of simulation.

    thresh: int
        The threshold to detect spikes. By default: if the membrane potential
        is larger than 0mV, it will be detected as a spike.

    Return:
    -----------
    count: int
        Number of spikes in the data.

    """
    spike_flag = False
    count = 0
    for idx, val in enumerate(data[:-1]):
        if spike_flag == False and val < thresh and data[idx+1] >= thresh:
            spike_flag = True
        elif spike_flag == True and val >= thresh and data[idx+1] < thresh:
            count += 1
            spike_flag = False
    return count



########################################
### Function: to calculate the half width of multiple EPSPs
########################################

def half_width_2EPSP(data, thresh = 2, stim_time = 80, dt = 0.025):
    """Calculate the half width of second EPSP from stimulation data

    Parameters:
    -----------
    data: list
        The electrical recording data from soma in the CA229_PFC model.
        It was recorded in h.Vector() originally, then saved as list into json
        file duirng the batch processing of simulation.

    thresh: int
        The minimum amplitude above baseline to be considered as an EPSP.

    stim_time: int
        the timestamp for the second stimulation

    dt: float
        The internal integration timestep to use for recording.
        Recording step is 0.025ms

    Return:
    -----------

    half_width_2EPSP: int
        The half_width of the 2nd EPSP

    """
    baseline = np.mean(data[100:2000])
    # Make sure dt = 0.025 and there is no stimulation for the first 50 ms
    data_idx = int(stim_time/dt)
    new_data = data[data_idx:]

    max_val = max(new_data)
    max_idx = new_data.index(max(new_data))
    if max_val < (baseline + thresh):
        print "No EPSP found."
        return NaN
    elif new_data[0]>(max_val+baseline)/2:
        idx_one = 0
        idx_two = get_closest(new_data[max_idx:], (max_val+baseline)/2) + max_idx
    else:
        idx_one = get_closest(new_data[:max_idx], (max_val+baseline)/2)
        idx_two = get_closest(new_data[max_idx:], (max_val+baseline)/2) + max_idx

        return (idx_two - idx_one)*dt



def get_EPSPs(data, thresh = 2, dt = 0.025):
    """
    Get the time and value of each EPSP peak
    Return:
    -----------
    spikes:
        A list of turple.
        Each turple has the time and value of max EPSP.
    """
    baseline = np.mean(data[100:2000])
    stable = data[2000:]
    EPSPs = []
    for idx, val in enumerate(stable[:-1]):
        if (val >= (baseline + thresh)) and (val > stable[idx-1]) and (val >= stable[idx+1]):
            time = (idx + 2000) * dt
            EPSPs.append((time, val))

    return EPSPs


def IST_spikes (data, dt = 0.025):
    """
    Get the interspike intervals
    Return:
    -----------
    ISTs:
        The average time of interspike intervals
    """
    spikes = get_EPSPs(data, 70, dt)
    IST = []
    count = len(spikes)
    if count<=1:
        ISTs = 0
    else:
        for i in range(count-1):
            IST.append(spikes[i+1][0]-spikes[i][0])

    ISTs = np.mean(IST)
    return ISTs




def Each_EPSP(data, baseline, thresh = 2, dt = 0.025):
    """
    Get the half_width of a EPSP only when there are multiple EPSPs.
    If the max EPSP is smaller than baseline + thresh,
    the return value will be NaN.
    """
    max_val = max(data)
    max_idx = data.index(max(data))
    if max_val < (baseline + thresh):
        print "No EPSP found."
        return 0
    else:
        if data[0] > (max_val+baseline)/2:
            idx_one = data.index(data[0])
        else:
            idx_one = get_closest(data[:max_idx], (max_val+baseline)/2)
        if data[-1] < (max_val+baseline)/2:
            idx_two = data.index(data[-1])
        else:
            idx_two = get_closest(data[max_idx:], (max_val+baseline)/2) + max_idx

        return (idx_two - idx_one)*dt



########################################
### Function: to calculate the half_width of one EPSP
########################################

def half_width_one_EPSP(data, thresh = 2, dt = 0.025):
    """Calculate the half width of one EPSP from stimulation data

    Parameters:
    -----------
    data: list
        The electrical recording data from soma in the CA229_PFC model.
        It was recorded in h.Vector() originally, then saved as list into json
        file duirng the batch processing of simulation.

    thresh: int
        The minimum amplitude above baseline to be considered as an EPSP.

    dt: float
        The internal integration timestep to use for recording.
        Recording step is 0.025ms

    Outputs:
    -----------
    idx_one: int
        The index of the value in data, which is half the maximum
        amplitude on the rising phase of EPSP.
    idx_two: int
        The index of the value in data, which is half the maximum
        amplitude on the descending phase of EPSP.

    Return:
    -----------
    half width = (idx_two - idx_one) * timestep

    """
    baseline = np.mean(data[100:2000])
    # Make sure dt = 0.025 and there is no stimulation for the first 50 ms
    max_val = max(data)
    max_idx = data.index(max(data))
    if max_val < (baseline + thresh):
        print "No EPSP found."
        return NaN
    else:
        idx_one = get_closest(data[:max_idx], (max_val+baseline)/2)
        idx_two = get_closest(data[max_idx:], (max_val+baseline)/2) + max_idx

        return (idx_two - idx_one)*dt

######################################
# Get the value index in data when the value is the cloest to target value
def get_closest (data, target):
    """Get the index of value in data which is closest to target"""
    min_idx = 0
    min_val = abs(data[0]-target)
    for idx, val in enumerate(data):
        if abs(val-target) < min_val:
            min_idx = idx
            min_val = abs(val-target)
    return min_idx



######################################
# Make sure all the stimulation start after 50ms
# The frist 50 mins are for baseline

def get_max(data, thresh = 2):
    """
    Get the maximum index and value of each EPSP peak
    Return:
    -----------
    spikes:
        A list of turple.
        Each turple has the index of max EPSP, and value of max EPSP.
    """
    baseline = np.mean(data[100:2000])
    stable = data[2000:]
    Max = []
    for idx, val in enumerate(stable[:-1]):
        if (val >= (baseline + thresh)) and (val > stable[idx-1]) and (val >= stable[idx+1]):
            Max.append((idx+2000, val-baseline))

    return Max


def mean_platamp(data, thresh=2):
    """
    Measures the plateau amplitude in soma
    Methods:
        Condition 1: subthreshold EPSP, measure the max ampltude of the EPSP
        Condition 2: with more than 2 spikes (including 2)
            Measure the amplitude of the minimum value between 1st and 2nd spikes.
            (Note: I tested to measure the amplitude of the minimum value
            between the last two spikes, but the results are not reliable. It
            fluctates not linearly or at least one directional changes along with
            Glu_Stim input strengh.)
        Condition 3: One spike (this is the superthreshold situation.)
            But I am not sure how to measure it correctly. Set the value to 0 or NA

    Return:
    -----------
    platamp:
        The voltage of the plateau - baseline
    """
    baseline = np.mean(data[100:2000])
#    stable = data[2000:]
#   The threshold for spike count has to be set different for basal dendrites
    spike = spike_count(data, 10)
    if spike == 0:
        platamp = get_max(data, 1)[0][1]
    elif spike>=2:
        spikes = get_max(data, 2)
        t0 = spikes[0][0]
        t1 = spikes[1][0]
        new = data[t0:t1+1]
        for idx, val in enumerate(new[:-1]):
            if (new[idx-1] >= val) and (val < new[idx + 1]):
                platamp = val - baseline
    else:
        platamp = NaN
        # NOT FINISHED YET
    return platamp
