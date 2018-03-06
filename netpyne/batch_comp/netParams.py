"""
netParams.py 
Specifications for EEE model using NetPyNE

Originally:
High-level specifications for M1 network model using NetPyNE
Contributors: salvadordura@gmail.com
"""

from netpyne import specs, sim
import os
import numpy as np
from neuron import h
import sys

# Find path to cells directory
curpath = os.getcwd()
while os.path.split(curpath)[1] != "sim":
    oldpath = curpath
    curpath = os.path.split(curpath)[0]
    if oldpath == curpath:
        raise Exception("Couldn't find cells directory. Try running from within eee/sim file tree.")
cellpath = os.path.join(curpath, "cells")

try:
    import batch_utils
except:
    sys.path.append(curpath)
    import batch_utils

try:
    from __main__ import cfg  # import SimConfig object with params from parent module
except:
    print("Couldn't import cfg from __main__")
    print("Attempting to import cfg from cfg.")
    try:
        from cfg import cfg  # if no simConfig in parent module, import directly from cfg module
    except:
        print("Couldn't import cfg from cfg")
        cfg, null = sim.readCmdLineArgs()

###############################################################################
#
# NETWORK PARAMETERS
#
###############################################################################

netParams = specs.NetParams()   # object of class NetParams to store the network parameters
netParams.defaultThreshold = -20.0

###############################################################################
# Cell parameters
###############################################################################

# EEE cell model with uniform spine distribution (7 comps)
#cellRule = netParams.importCellParams(label='eee7us', conds={'cellType': 'eee7us', 'cellModel': 'HH_reduced'}, fileName=os.path.join(cellpath, 'eee7us.py'), cellName='eee7us')

# EEE cell model with physiological spine distribution (7 comps)
#cellRule = netParams.importCellParams(label='eee7', conds={'cellType': 'eee7', 'cellModel': 'HH_reduced'}, fileName=os.path.join(cellpath, 'eee7.py'), cellName='eee7')

# Detailed EEE cell model
cellRule = netParams.importCellParams(label='eeeD', conds={'cellType': 'eeeD', 'cellModel': 'PFC_full'}, fileName='CA229.py', cellName='MakeCA229')

cellRule = netParams.importCellParams(label='eeeS', conds={'cellType': 'eeeS', 'cellModel': 'PFC_simp'}, fileName='CA229simp.py', cellName='MakeCA229simp')

# define section lists
cellRule['secLists']['alldend'] = ['Bdend1', 'Bdend2', 'Adend1', 'Adend2', 'Adend3']
cellRule['secLists']['apicdend'] = ['Adend1', 'Adend2', 'Adend3']
cellRule['secLists']['basaldend'] = ['Bdend1', 'Bdend2']
cellRule['secLists']['stimheads'] = []
cellRule['secLists']['stimnecks'] = []

# apply values to parameters
for cell_label, cell_params in netParams.cellParams.iteritems():

    for secName,sec in cell_params['secs'].iteritems(): 
        sec['vinit'] = cfg.e_pas  # set vinit for all secs
    
        if hasattr(cfg, 'allNaScale') or hasattr(cfg, 'dendNaScale'):
            if 'na' in sec['mechs']:
                orig_na = sec['mechs']['na']['gbar']
                if hasattr(cfg, 'dendNaScale') and ("basal" in secName or "apical" in secName):
                    sec['mechs']['na']['gbar'] = list(np.array(orig_na, ndmin=1) * cfg.dendNaScale) 
                    print("Scaling gbar Na in %s by %s" % (secName, str(cfg.dendNaScale)))
                if hasattr(cfg, 'allNaScale'):
                    sec['mechs']['na']['gbar'] = list(np.array(orig_na, ndmin=1) * cfg.allNaScale)
                    print("Scaling Na in %s by %s" % (secName, str(cfg.allNaScale)))
        
        if hasattr(cfg, 'allKScale') or hasattr(cfg, 'dendKScale'):
            
            if 'kv' in sec['mechs']:
                orig_kv = sec['mechs']['kv']['gbar']
                if hasattr(cfg, 'dendKScale') and ("basal" in secName or "apical" in secName):
                    sec['mechs']['kv']['gbar'] = list(np.array(orig_kv, ndmin=1) * cfg.dendKScale)
                    print("Scaling gbar kv in %s by %s" % (secName, str(cfg.dendKScale)))
                if hasattr(cfg, 'allKScale'):
                    sec['mechs']['kv']['gbar'] = list(np.array(orig_kv, ndmin=1) * cfg.allKScale)
                    print("Scaling gbar kv in %s by %s" % (secName, str(cfg.allKScale))) 

            if 'kap' in sec['mechs']:
                orig_kap = sec['mechs']['kap']['gkabar']
                if hasattr(cfg, 'dendKScale') and ("basal" in secName or "apical" in secName):
                    sec['mechs']['kap']['gkabar'] = list(np.array(orig_kap, ndmin=1) * cfg.dendKScale)
                    print("Scaling gkabar kap in %s by %s" % (secName, str(cfg.dendKScale)))
                if hasattr(cfg, 'allKScale'):
                    sec['mechs']['kap']['gkabar'] = list(np.array(orig_kap, ndmin=1) * cfg.allKScale)
                    print("Scaling gbar kap in %s by %s" % (secName, str(cfg.allKScale)))

            if 'kad' in sec['mechs']:
                orig_kad = sec['mechs']['kad']['gkabar']
                if hasattr(cfg, 'dendKScale') and ("basal" in secName or "apical" in secName):
                    sec['mechs']['kad']['gkabar'] = list(np.array(orig_kad, ndmin=1) * cfg.dendKScale)
                    print("Scaling gkabar kad in %s by %s" % (secName, str(cfg.dendKScale)))
                if hasattr(cfg, 'allKScale'):
                    sec['mechs']['kad']['gkabar'] = list(np.array(orig_kad, ndmin=1) * cfg.allKScale)
                    print("Scaling gbar kad in %s by %s" % (secName, str(cfg.allKScale)))

            if 'kBK' in sec['mechs']:
                orig_kBK = sec['mechs']['kBK']['gpeak']
                if hasattr(cfg, 'dendKScale') and ("basal" in secName or "apical" in secName):
                    sec['mechs']['kBK']['gpeak'] = list(np.array(orig_kBK, ndmin=1) * cfg.dendKScale)
                    print("Scaling gpeak kBK in %s by %s" % (secName, str(cfg.dendKScale)))
                if hasattr(cfg, 'allKScale'):
                    sec['mechs']['kBK']['gpeak'] = list(np.array(orig_kBK, ndmin=1) * cfg.allKScale)
                    print("Scaling gpeak kBK in %s by %s" % (secName, str(cfg.allKScale)))

        if hasattr(cfg, 'ihScale'):
            if 'ih' in sec['mechs']:
                sec['mechs']['ih']['gbar'] = cfg.ihScale * sec['mechs']['ih']['gbar']

        if hasattr(cfg, 'RmScale'):
            sec['mechs']['pas']['g'] = (1.0/cfg.RmScale) * sec['mechs']['pas']['g']

        if hasattr(cfg, 'e_pas'):
            if 'pas' in sec['mechs']:
                sec['mechs']['pas']['e'] = cfg.e_pas

        if "soma" in secName:
            if hasattr(cfg, 'gpasSomaScale'):
                orig_gpas = sec['mechs']['pas']['g']
                sec['mechs']['pas']['g'] = cfg.gpasSomaScale * orig_gpas

        if hasattr(cfg, 'dendRaScale'):
            if "dend" in secName:
                orig_ra = sec['geom']['Ra']
                sec['geom']['Ra'] = cfg.dendRaScale * sec['geom']['Ra']

        if hasattr(cfg, 'dendRmScale'):
            if "dend" in secName:
                orig_gpas = sec['mechs']['pas']['g']
                sec['mechs']['pas']['g'] = (1/cfg.dendRmScale) * orig_gpas
                



###############################################################################
# Population parameters
###############################################################################

netParams.popParams['eeeD']= {'cellModel':'PFC_full', 'cellType':'eeeD', 'numCells':1}
netParams.popParams['eeeS']= {'cellModel':'PFC_simp', 'cellType':'eeeS', 'numCells':1}


###############################################################################
# Synaptic mechanism parameters
###############################################################################

#netParams.synMechParams['NMDA'] = {'mod': 'NMDA', 'Cdur': cfg.CdurNMDAScale * 1.0, 'Cmax': cfg.CmaxNMDAScale * 1.0, 'Alpha': cfg.NMDAAlphaScale * 4.0, 'Beta': cfg.NMDABetaScale * 0.0015, 'gmax': cfg.NMDAgmax}
netParams.synMechParams['NMDA'] = {'mod': 'NMDA', 'Cdur': cfg.CdurNMDAScale * 1.0, 'Alpha': cfg.NMDAAlphaScale * 4.0, 'Beta': cfg.NMDABetaScale * 0.0015, 'gmax': cfg.NMDAgmax}

netParams.synMechParams['AMPA'] = {'mod': 'AMPA', 'gmax': cfg.ratioAMPANMDA * cfg.NMDAgmax}


###############################################################################
# NetStim inputs
###############################################################################
if cfg.addNetStim:
    for nslabel in [k for k in dir(cfg) if k.startswith('NetStim')]:
        ns = getattr(cfg, nslabel, None)

        for cur_pop in ns['pop']:

            #cur_pop = ns['pop'][0]
                
            if "ExSyn" in nslabel:
                cur_weight = cfg.glutAmp * cfg.glutAmpExSynScale
            elif "Syn" in nslabel:
                cur_weight = cfg.glutAmp
            else:
                raise Exception("NetStim must have Syn or ExSyn in name")

            # add stim source
            netParams.stimSourceParams[nslabel] = {'type': 'NetStim', 'start': ns['start'], 'interval': ns['interval'], 'noise': ns['noise'], 'number': ns['number']}

            # connect stim source to target
            for i in range(len(ns['synMech'])):
                # netParams.stimTargetParams[nslabel+'_'+cur_pop+'_'+ns['synMech'][i]] = \
                #     {'source': nslabel, 'conds': {'pop': ns['pop']}, 'sec': ns['sec'], 'synsPerConn': cfg.numSyns, 'loc': list(np.linspace(cfg.synLocStart, cfg.synLocStart + cfg.synLocSpread, cfg.numSyns)), 'synMech': ns['synMech'][i], 'weight': cur_weight, 'delay': ns['delay']}
                netParams.stimTargetParams[nslabel+'_'+cur_pop+'_'+ns['synMech'][i]] = \
                    {'source': nslabel, 'conds': {'pop': cur_pop}, 'sec': ns['sec'], 'synsPerConn': cfg.numSyns, 'loc': list(np.linspace(cfg.synLocStart, cfg.synLocStart + cfg.synLocSpread, cfg.numSyns)), 'synMech': ns['synMech'][i], 'weight': cur_weight, 'delay': ns['delay']}

            
###############################################################################
# Current inputs (IClamp)
###############################################################################

if cfg.addIClamp:   
    for iclabel in [k for k in dir(cfg) if k.startswith('IClamp')]:
        ic = getattr(cfg, iclabel, None)  # get dict with params

        # add stim source
        #netParams.stimSourceParams[iclabel] = {'type': 'IClamp', 'del': ic['start'], 'dur': ic['dur'], 'amp': cfg.ampIClamp1}
        netParams.stimSourceParams[iclabel] = {'type': 'IClamp', 'del': ic['start'], 'dur': cfg.durIClamp1, 'amp': cfg.ampIClamp1}
        
        for curpop in ic['pop']:
            netParams.stimTargetParams[iclabel+'_'+curpop] = \
                {'source': iclabel, 'conds': {'popLabel': ic['pop']}, 'sec': ic['sec'], 'loc': ic['loc']}



