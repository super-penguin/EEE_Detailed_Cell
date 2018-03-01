"""
cfg.py 

Simulation configuration 

Contributors: salvadordura@gmail.com
"""

from netpyne import specs
import numpy as np

cfg = specs.SimConfig()  

###############################################################################
#
# SIMULATION CONFIGURATION
#
###############################################################################

cfg.checkErrors = True

###############################################################################
# Run parameters
###############################################################################
cfg.duration = 1000 #1200
cfg.dt = 0.05
cfg.seeds = {'conn': 4321, 'stim': 1234, 'loc': 4321} 
cfg.hParams = {'celsius': 32}  
cfg.verbose = 0
cfg.cvode_active = False
cfg.printRunTime = 0.1
cfg.printPopAvgRates = True


###############################################################################
# Recording 
###############################################################################
cfg.recordTraces = {'V_soma': {'sec': 'soma_2', 'loc': 0.5, 'var': 'v'}}
cfg.recordTraces['V_dend1'] = {'sec': 'basal_34', 'loc': 0.3, 'var': 'v'}
cfg.recordTraces['V_dend2'] = {'sec': 'basal_34', 'loc': 0.5, 'var': 'v'}
cfg.recordTraces['V_dend3'] = {'sec': 'basal_34', 'loc': 0.8, 'var': 'v'}

#cfg.recordTraces['g_NMDA'] = {'sec': 'head_55', 'loc': 0.99999, 'synMech': 'NMDA', 'var': 'g'}
#cfg.recordTraces['i_NMDA'] = {'sec': 'head_55', 'loc': 0.99999, 'synMech': 'NMDA', 'var': 'iNMDA'}
#cfg.recordTraces['i_Ca'] = {'sec': 'head_55', 'loc': 0.99999, 'synMech': 'NMDA', 'var': 'ica'}

#cfg.recordCells = ['eee7us', 'eee7ps']
cfg.recordCells = ['eeeD']
cfg.recordStims = False  
cfg.recordStep = 0.1 


###############################################################################
# Saving
###############################################################################
cfg.simLabel = 'batch_glutAmp'
cfg.saveFolder = 'batch_data'
cfg.savePickle = False
cfg.saveJson = True
cfg.saveDataInclude = ['simData', 'simConfig', 'netParams', 'net']


###############################################################################
# Analysis and plotting 
###############################################################################
cfg.analysis['plotTraces'] = {'include': ['all'], 'oneFigPer': 'cell', 'saveFig': True, 
                              'showFig': False, 'figSize': (10,8), 'timeRange': [0,cfg.duration]}


###############################################################################
# Parameters
###############################################################################

# Sodium and potassium conductance scaling
#cfg.dendNaScale = 1.0 # Scales dendritic Na conductance
#cfg.dendKScale  = 1.0 # Scales dendritic K  conductance
cfg.allNaScale  = 0.0 # Scales all Na conductances (overrides dendNaScale if not commented)
cfg.allKScale   = 1.0 # Scales all K  conductances (overrides dendKScale  if not commented)

# DMS NMDA params
cfg.NMDAAlphaScale = 1.0 # Scales original value of 4.0
cfg.NMDABetaScale  = 4.5 # 3.0 # Scales original value of 0.0015
cfg.CdurNMDAScale  = 1.0 # Scales original value of 1.0
#cfg.CmaxNMDAScale  = 1.0 # Scales original value of 1.0
cfg.NMDAgmax       = 0.05
cfg.ratioAMPANMDA  = 2.0

# glutamate stim parameters
cfg.synTime           = 100.0
cfg.numSyns           = 9
cfg.numExSyns         = 9
cfg.glutAmp           = 0.2
cfg.glutAmpExSynScale = 1.0
cfg.synLocStart       = 0.2
cfg.synLocSpread      = 0.4 # 0.4 makes the spread from 0.2 to 0.6
cfg.synDelay          = 12.5
cfg.exSynDelay        = 16.0

# other params
cfg.e_pas         = -80.0 # resting membrane potential
#cfg.ihScale       = 0.0   # Scales ih conductance
#cfg.gpasSomaScale = 1.0 # Scales soma g_pas
#cfg.dendRaScale   = 1.0
#cfg.dendRmScale   = 1.0
#cfg.RaScale       = 1.0  # Scales axial resistance in all secs
#cfg.RmScale       = 1.0  # Scales membrane resistance in all secs

cfg.ampIClamp1    = 5.0 # amplitude of current clamp
cfg.durIClamp1    = 2.0 # 1.0

###############################################################################
# NetStim inputs 
###############################################################################
cfg.addNetStim = True

cfg.NetStimSyn = {'pop': ['eeeD'], 'loc': [cfg.synLocStart, cfg.synLocStart + cfg.synLocSpread], 'sec': 'basal_34', 'synMech': ['NMDA','AMPA'], 'start': cfg.synTime, 'interval': 1000, 'noise': 0.0, 'number': 1, 'weight': cfg.glutAmp, 'delay': cfg.synDelay}

cfg.NetStimExSyn = {'pop': ['eeeD'], 'loc': [cfg.synLocStart, cfg.synLocStart + cfg.synLocSpread], 'sec': 'basal_34', 'synMech': ['NMDA'], 'start': cfg.synTime, 'interval': 1000, 'noise': 0.0, 'number': 1, 'weight': cfg.glutAmp * cfg.glutAmpExSynScale, 'delay': cfg.exSynDelay}


###############################################################################
# Current inputs 
###############################################################################
cfg.addIClamp = False
