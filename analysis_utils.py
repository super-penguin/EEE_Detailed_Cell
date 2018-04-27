"""
The analysis functions for EEE stimulation data.
1. Plateau Amplitude
2. Plateau Duration
3. Spike Numbers on plateau
4. Interspike intervals
5. EPSPs amplitude and time stamp

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
### Function: to measure plateau duration
########################################
def meas_platdur(data, thresh = 10, dt = 0.025):
    """Measures plateau duration (ms)

    Parameters:
    -----------
        data: voltage trace
        thresh (mV): measure the duration of the plateau which are bigger than baseline + thresh
        dt: the sampling rate (default is 0.025ms or 40kHz)
    Return:
    -----------
        platur (ms): plateau duration in ms
    """
    # Make sure dt = 0.025 and there is no stimulation for the first 50 ms
    # If there is anything before 50ms, change the time points for baseline
    baseline = np.mean(data[4000:6000])
    stable = data[6000:]
    above = [val for val in stable if val > (baseline + thresh)]
    platdur = dt * len(above)
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
        is larger than 0 mV, it will be detected as a spike.

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

def IST_spikes (data, dt = 0.025):
    """
    Get the interspike intervals, spike_idx, spike_mvalue and spike_midx
    Return:
    -----------
    spike_mvalue:
        The list of minimum values between each two spikes
    spike_midx:
        The list of timepoints of minimum values
    ISTs:
        The average time of interspike intervals
    """
    spikes = get_EPSPs(data, 60, dt)
    IST = []
    count = len(spikes)
    spike_mvalue = []
#    spike_midx = []
    if count <= 1:
        ISTs = 0
    else:
        for i in range(count-1):
            IST.append(spikes[i+1][0]-spikes[i][0])
            idx1 = int(round((spikes[i][0])/dt))
            idx2 = int(round((spikes[i+1][0])/dt))
            temp = min(data[idx1:idx2])
            spike_mvalue.append(temp)
        #    spike_midx.append(temp.index(min(temp)) + idx1)

        ISTs = np.mean(IST)
    return ISTs , spike_mvalue #, spike_midx
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
    baseline = np.mean(data[4000:6000])
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
    Get the maximum index and value of each EPSP peak
    Return:
    -----------
    spikes:
        A list of turple.
        Each turple has the index of max EPSP, and value of max EPSP.
    """
    baseline = np.mean(data[4000:6000])
    stable = data[6000:]
    EPSPs = []
    for idx, val in enumerate(stable[:-1]):
        if (val >= (baseline + thresh)) and (val > stable[idx-1]) and (val >= stable[idx+1]):
            time = (idx + 6000) * dt
            EPSPs.append((time, val))
    return EPSPs


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
    baseline = np.mean(data[4000:6000])
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
    """Get the index of value in data which is closest to target.
    The original calculation is slow,
    Updated on Jan 22, 2018 """
    # min_idx = 0
    # min_val = abs(data[0]-target)
    # for idx, val in enumerate(data):
    #     if abs(val-target) < min_val:
    #         min_idx = idx
    #         min_val = abs(val-target)
    # return min_idx
    t = data.index(min(data, key=lambda x:abs(x-target)))
    return t

######################################
# This one is not correct, need to update!!!
def meas_platamp(data, dt = 0.025):
    """Measures plateau amplitude (average of voltage - baseline while volt
        trace is above baseline + thresh)"""
    baseline = np.mean(data[4000:6000])
    stable = data[6000:]
    # above = [val for val in stable if val > (baseline + thresh)]
    spike_num = spike_count(stable)
    if spike_num == 0:
        platamp = max(stable) - baseline
        platdur = 0
        ISI = 0
    elif spike_num == 1: # Maybe filtering would be better?
        spikegap = 5 # ms to skip after spike
        idx = data.index(max(data)) + int(spikegap/dt)
        platamp = data[idx] - baseline
        ISI = 0
    # elif spike_num == 2:
    #     ISI, spike_mvalue = IST_spikes(data, dt)
    #     spikes = get_EPSPs(data, 12, dt)
    #     if len(spikes) > spike_num:
    #         idx1 = int(round((spikes[1][0])/dt))
    #         idx2 = int(round((spikes[2][0])/dt))
    #         spike_mvalue = min(data[idx1:idx2])
    #     # else:
    #     #     spikegap = 5 # ms to skip after spike
    #     #     idx = int(round((spikes[1][0])/dt)) + int(spikegap/dt)
    #     #     spike_mvalue = data[idx]
    #     platamp = spike_mvalue - baseline
    else:
        ISI, spike_mvalue = IST_spikes(data, dt)
        # platamp = 0
        platamp = spike_mvalue[-1] - baseline
#    platamp = np.mean([val - baseline for val in above])
    return ISI , platamp

#test = [-2,-1, 0, 3, 5, 7, 8,7, 5, 4,4, 1,1,0,-1]
def TTX_platamp(data):
    baseline = np.mean(data[4000:6000])
    stable = data[6000:]
    above = [idx for idx, val in enumerate(stable) if val > (baseline+15)]
    # platamp = max(stable) - baseline
    if len(above) <= 15:
        platamp = max(stable) - baseline
    else:
        idx1 = above[0]
        idx2 = above[-1]
        platamp = stable[int(0.75*idx2 + 0.25*idx1)] - baseline
    return platamp
#####################################
# Joe's code on plateau amp measurement when there is only one spike
# def meas_trace_plat_amp(trace, time=None, recstep=recstep, syntime=syntime,
# platthresh=platthresh, stable=stable, showwork=False, spikethresh=spikethresh):
#
#     stable_index = int(stable / recstep)
#     syntime_index = int(syntime / recstep)
#
#     if time is None:
#         timesteps = len(trace)
#         time = recstep * np.arange(0, timesteps, 1)
#
#     baseline = np.mean(trace[stable_index:syntime_index])
#     above_index = [valind for valind, val in enumerate(trace) if val > (baseline + platthresh)]
#
#     spike_times, spike_indices = meas_trace_spike_times(trace, time=time, recstep=recstep, spikethresh=spikethresh)
#
#     platamp = 0.0
#     platvolt = 0.0
#     interspike_mins = []
#
#     if len(spike_indices) == 0:
#         if len(above_index) > 0:
#             minind = np.min(above_index)
#             maxind = np.max(above_index)
#             v_above = trace[minind:maxind]
#             platvolt = np.max(v_above)
#             platamp = np.max(v_above) - baseline
#     elif len(spike_indices) == 1:
#         spikegap = 5 # ms to skip after spike
#         postspike = trace[spike_indices[0] + int(spikegap/recstep):]
#         platvolt = np.max(postspike)
#         platamp = np.max(postspike) - baseline
#     else:
#         for ind,spike_index in enumerate(spike_indices):
#             if ind < (len(spike_indices) - 1):
#                 interspike_min = np.min(trace[spike_indices[ind]:spike_indices[ind+1]])
#                 interspike_mins.append(interspike_min)
#         platvolt = np.max(interspike_mins)
#         platamp = np.max(interspike_mins) - baseline
#
#     return platamp, platvolt

#######################################
# Color
#######################################
# Scale the RGB values to the [0, 1] range, which is the format matplotlib accepts.
def tableau (num = 0):
    "The number has to be smaller than 21."
    tableau21 = [(31, 119, 180), (174, 199, 232), (255, 127, 14), (255, 187, 120),
                 (44, 160, 44), (152, 223, 138), (214, 39, 40), (255, 152, 150),
                 (148, 103, 189), (197, 176, 213), (140, 86, 75), (196, 156, 148),
                 (227, 119, 194), (247, 182, 210), (127, 127, 127), (199, 199, 199),
                 (188, 189, 34), (219, 219, 141), (23, 190, 207), (158, 218, 229),
                 (0, 0, 0)]
    for i in range(len(tableau21)):
        r, g, b = tableau21[i]
        tableau21[i] = (r / 255., g / 255., b / 255.)
    return tableau21[num]
