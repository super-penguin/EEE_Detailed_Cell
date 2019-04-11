"""
The analysis for AP Backpropagation

In the new NEURON version, seg.x does not include 0 and 1 location anymore.
Therefore if I only measure distance and AP at every seg.x of each basal dendrite,
The final plot (AP amp or AP latency vs. distance) would not be ccontinuous.
Distance and recording of 0 and 1 for each branch are added to make the plot pretter.

Bin the data based on distance:
All the data are bined based on the distance from soma.
Bin size = 20 um
Final plot: x = mean distance in each bin
            y = mean of AP amp or AP latency in each bin

Author: Peng Penny Gao
penggao.1987@gmail.com
"""
import json
import matplotlib.pyplot as plt
import os
import numpy as np
import pandas as pd
import analysis_utils as ana
from analysis_utils import tableau #from analysis_utils import *
import utils as ut #from utils import *
import seaborn as sns
import itertools
import time

#################################
# Analysis all the json files with recording to get AP peak time and peak Amplitude against dist to soma
# Save the analysed results
#################################
new_data = pd.DataFrame(columns = ['Bnum', 'condition', 'dist', 'Peak_amp', 'Peak_t', 'Soma_v'])
path_to_json = 'Fig2/'
start_time = time.time()
json_files = [pos_json for pos_json in os.listdir(path_to_json) if pos_json.endswith('.json')]

i = 0
for index, js in enumerate(json_files):
    with open(os.path.join(path_to_json, js)) as json_file:
        data = json.load(json_file)
        if 'TTX' in js:
            condition = 'TTX'
        elif '4AP' in js:
            condition = '4AP'
        else:
            condition = 'Control'
        Bnum = data['Bnum']
        soma_v, soma_t = ana.single_spike(data['recording']['soma']['voltage'])

        for key, value in data['recording']['dend'].iteritems():
            dist = key
            dend_v, dend_t = ana.single_spike(value)
            peak_del = dend_t - soma_t
            i += 1
            new_data.loc[i] = [Bnum, condition, dist, dend_v, peak_del, soma_v]

df = new_data.sort_values(by = ['dist'])
savepath = path_to_json + 'bAP_total_results.csv'
df.to_csv(savepath)

#################################
# Combine data and plot
#################################
path = path_to_json + 'bAP_total_results.csv'
df = pd.read_csv(path, index_col = 0)
df.set_index(['Bnum'], inplace=True)
df_con = df[df['condition'] == 'Control'].sort_values(by = ['dist'],ascending=True)
df_TTX = df[df['condition'] == 'TTX'].sort_values(by = ['dist'],ascending=True)
df_4AP = df[df['condition'] == '4AP'].sort_values(by = ['dist'],ascending=True)

##### Bin the data
def map_bin(x, bins):
    """
    Map the data in each bin
        x: data value
        bins: numpy array of bin frequency
    Return
        [low_limit, upper_limit] of the bin where the x belongs
    """
    kwargs = {}
    if x == max(bins):
        kwargs['right'] = True
    bin = bins[np.digitize([x], bins, **kwargs)[0]]
    bin_lower = bins[np.digitize([x], bins, **kwargs)[0]-1]
    return '[{0}-{1}]'.format(bin_lower, bin)


freq_bins = np.arange(0, 300, 20)
df_con['Binned'] = df_con['dist'].apply(map_bin, bins=freq_bins)
df_TTX['Binned'] = df_TTX['dist'].apply(map_bin, bins=freq_bins)
df_4AP['Binned'] = df_4AP['dist'].apply(map_bin, bins=freq_bins)

df_con_group = df_con.groupby(['Binned'], sort=True).mean()
df_con_group = df_con_group.sort_values(by = ['dist']).iloc[0:12]
df_TTX_group = df_TTX.groupby('Binned').mean()
df_TTX_group = df_TTX_group.sort_values(by = ['dist']).iloc[0:12]
df_4AP_group = df_4AP.groupby('Binned').mean()
df_4AP_group = df_4AP_group.sort_values(by = ['dist']).iloc[0:12]


#################################
# Plot and save the figures
path_to_figure = path_to_json + 'New_Figs/'
plt.close()
plt.clf()
plt.figure(figsize = (9,6), dpi = 300)
plt.subplots_adjust(left=0.15, right=0.9, top=0.85, bottom=0.15)
ax = plt.gca()
plt.style.use("ggplot")
plt.rcParams['axes.edgecolor'] = "black"
plt.rcParams['axes.facecolor'] = "white"
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)
ax.yaxis.set_ticks_position('left')
ax.xaxis.set_ticks_position('bottom')
df_con.groupby('Bnum').plot(x='dist', y='Peak_amp', ax=ax, legend = False, color = tableau(15), linewidth = 1, alpha = 0.3)
df_con_group.plot(x = 'dist', y = 'Peak_amp', ax = ax, legend = False, markersize = 5, color = tableau(20), linewidth = 2, alpha = 1)
df_TTX.groupby('Bnum').plot(x='dist', y='Peak_amp', ax=ax, legend = False, color = tableau(7), linewidth = 1, alpha = 0.3)
df_TTX_group.plot(x = 'dist', y = 'Peak_amp', ax = ax, legend = False, markersize = 5, color = tableau(6), linewidth = 2, alpha = 1)
df_4AP.groupby('Bnum').plot(x='dist', y='Peak_amp', ax=ax, legend = False, color = tableau(5), linewidth = 1, alpha = 0.3)
df_4AP_group.plot(x = 'dist', y = 'Peak_amp', ax = ax, legend = False, markersize = 5, color = tableau(4), linewidth = 2, alpha = 1)
plt.xlabel("Distance to soma (um)", size = 22, color = "black")
plt.ylabel("Peak Amplitude (mV)", size = 22, color = "black")
plt.tick_params(labelsize=22, pad = 12, colors = "black")
# plt.xticks([])
plt.title("AP Amplitude vs. Distance", size = 20)
plt.ylim([20, 110])
plt.yticks(np.arange(20, 110, 20))
# ax.grid(False)
#ax.set_axis_bgcolor('white')
title1 = "bAP_Amplitude"
# ut.save(title1, path_to_figure, ext="pdf", close=False, verbose=True)
ut.save(title1, path_to_figure, ext="png", close=True, verbose=True)


plt.close()
plt.clf()
plt.figure(figsize = (9,6), dpi = 300)
plt.subplots_adjust(left=0.15, right=0.9, top=0.85, bottom=0.15)
ax = plt.gca()
plt.style.use("ggplot")
plt.rcParams['axes.edgecolor'] = "black"
plt.rcParams['axes.facecolor'] = "white"
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)
ax.yaxis.set_ticks_position('left')
ax.xaxis.set_ticks_position('bottom')
df_con.groupby('Bnum').plot(x='dist', y='Peak_t', ax=ax, legend = False, color = tableau(15), linewidth = 1, alpha = 0.3)
df_con_group.plot(x = 'dist', y = 'Peak_t', ax = ax, legend = False, markersize = 5, color = tableau(20), linewidth = 2, alpha = 1)
df_TTX.groupby('Bnum').plot(x='dist', y='Peak_t', ax=ax, legend = False, color = tableau(7), linewidth = 1, alpha = 0.3)
df_TTX_group.plot(x = 'dist', y = 'Peak_t', ax = ax, legend = False, markersize = 5, color = tableau(6), linewidth = 2, alpha = 1)
df_4AP.groupby('Bnum').plot(x='dist', y='Peak_t', ax=ax, legend = False, color = tableau(5), linewidth = 1, alpha = 0.3)
df_4AP_group.plot(x = 'dist', y = 'Peak_t', ax = ax, legend = False, markersize = 5, color = tableau(4), linewidth = 2, alpha = 1)
plt.xlabel("Distance to soma (um)", size = 22, color = "black")
plt.ylabel("Latency (ms)", size = 22, color = "black")
plt.tick_params(labelsize=22, pad = 12, colors = "black")
# plt.xticks([])
plt.title("AP Latency vs. Distance", size = 20)
plt.ylim([0, 1.5])
# plt.yticks(np.arange(20, 110, 20))
# ax.grid(False)
#ax.set_axis_bgcolor('white')
title2 = "bAP_Latency"
# save(title2, path_to_figure, ext="pdf", close=False, verbose=True)
ut.save(title2, path_to_figure, ext="png", close=True, verbose=True)
