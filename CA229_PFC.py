
"""
CA229.py    : Reconstructed morphology of prefrontal layer V pyramidal cell from
   Acker, Antic (2008)

Original    :
https://senselab.med.yale.edu/ModelDB/ShowModel.cshtml?model=117207&file=/acker_antic/Model/CA%20229.hoc#tabs-2
Modified by : Peng (Penny) Gao <penggao.1987@gmail.com>
"""

import sys
from neuron import h

#########################################
# Parameters
#########################################
# Cell passive properties
global_Ra=90
spineFACTOR = 1.5
somaRm = 1000/0.04
dendRm = somaRm/spineFACTOR
somaCm = 1
dendCm = somaCm*spineFACTOR
spinedist = 50 # distance at which spines start
Vk = -80
VNa = 60
pasVm = -65

# Specify cell biophysics
somaNa = 900  # [pS/um2]
axonNa = 5000  # [pS/um2]
basalNa = 150  # [pS/um2]
mNa = 0.5  # decrease in sodium channel conductance in basal dendrites [pS/um2/um]
apicalNa = 375
gNamax = 2000  # maximum basal sodium conductance
vshiftna = -10

somaKv = 40 # somatic, apical, and initial basal Kv conductance
mKV = 0  # increase in KV conductance in basal dendrites
gKVmax = 500  # maximum basal KV conductance
axonKv = 100
somaKA = 150  # initial basal total GKA conductance [pS/um2] equals somatic
mgka = 0.7  # linear rise in IA channel density
mgkaratio = 1./300 # linear drop in KAP portion, 1 at soma
apicalKA = 300 # apical total GKA conductance
gkamax = 2000  # pS/um2

somaCa = 10 # total calcium channel conductance density of soma [pS/um^2]
dendCa = 2 # dendritic total calcium conductance density
cadist = 30  # dendritic calcium channel conductance equals that of soma up until this distance
gcaratio = 0.2 #portion of gHVA to gHVA+gIT total, 1 is all HVA, 0 is all IT#
gkl = 0.005
ILdist = 15

#########################################
# Set up the global Ra and measure the maximum Amplitude (V)
# at each nseg of each compartment
#########################################


class CA229:
    """
    A detailed model of Prefrontal layer V pyramidal neuron in Rat.

    Channel distributions and all other biophysical properties of model basal
    dendrites of prefrontal layer V pyramidal cell from Acker, Antic (2008)
    Membrane Exitability and Action Potential Backpropagation in Basal Dendrites
    of Prefrontal Cortical Pyramidal Neurons.

    soma: soma compartments (soma[0] - soma[3])
    apical: apical dendrites (apical[0] - apical[44])
    apical_list: python list of all the apical compartments
    basal: basal dendrites (basal[0] - basal[35])
    basal_list: all basal dendrites but excluing basal[16]
    axon: python list of basal[16] (basal[16] is modeled as axon here)
    """
    def __init__(self):
        h.load_file('stdrun.hoc') # for initialization
        h.load_file('CA229.hoc')

        self.soma = h.soma
#        # name   L
#        #soma[0] 0.0100002288818
#        #soma[1] 5.21938715973
#        #soma[2] 2.59000015259
#        #soma[3] 10.758930225
        self.apical = h.apical
        self.apical_list = [sec for sec in h.apicals]
        self.axon = [sec for sec in h.axon]
        self.basal = h.basal
        self.basal_list = [sec for sec in h.basals]
        # Attention: basal[16] is removed from basal_list
        self.record_basal = []    # Define which tips we are interested in
        BasalIndex = [0,1,2,3,4,5,6,7,8,9,10,11,12]
        for i in BasalIndex:
            self.record_basal.append(self.basal[i])

        #self.init_once()

    def init_once(self):
        """
        Initialize channel distributions and biophysical properties.
        """
        for sec in h.allsec():
            sec.Ra = global_Ra
            sec.insert('vmax') # Measure the maximum potential

        #########################################
        # Set up properties for soma
        #########################################

        for sec in self.soma:
            sec.cm = somaCm
            sec.insert('pas')
            sec.g_pas = 1./somaRm
            sec.e_pas = pasVm
            sec.insert('na')
            if h.ismembrane('na', sec = sec):
                sec.ena = VNa
                h.vshift_na = vshiftna
            sec.insert('kv')
            sec.ek = Vk
            sec.insert('kap')
            sec.insert('ca')
            sec.insert('it')  # Properties from CaT.mod
            sec.vh1_it = 56
            sec.vh2_it = 415
            sec.ah_it = 30
            sec.v12m_it = 45
            sec.v12h_it = 65
            sec.am_it = 3
            sec.vshift_it = 10
            sec.vm1_it = 50
            sec.vm2_it = 125

            if h.ismembrane ('ca_ion', sec = sec):
                sec.eca = 140
                h.ion_style("ca_ion", 0, 1, 0, 0, 0)
                h.vshift_ca = 10

            sec.insert('cad')

        #########################################
        # Set up properties for basal dendrites, not including basal[16]
        #########################################


        for sec in self.basal_list:
            sec.insert('pas')
            sec.e_pas = pasVm
            sec.insert('na')
            if h.ismembrane('na', sec = sec):
                sec.ena = VNa
                h.vshift_na = vshiftna
            sec.insert('kv')
            sec.ek = Vk
            sec.insert('kap')
            sec.insert('kad')
            sec.insert('ca')
            sec.insert('it')  # Properties from CaT.mod
            sec.vh1_it = 56
            sec.vh2_it = 415
            sec.ah_it = 30
            sec.v12m_it = 45
            sec.v12h_it = 65
            sec.am_it = 3
            sec.vshift_it = 10
            sec.vm1_it = 50
            sec.vm2_it = 125

            if h.ismembrane ('ca_ion', sec = sec):
                sec.eca = 140
                h.ion_style("ca_ion", 0, 1, 0, 0, 0)
                h.vshift_ca = 10

            sec.insert('cad')

        #########################################
        # Set up properties for axon, which is basal[16]
        #########################################
        for sec in self.axon:
            sec.cm = somaCm
            sec.insert('pas')
            sec.g_pas = 1./somaRm
            sec.e_pas = pasVm
            sec.insert('na')
            if h.ismembrane('na', sec = sec):
                sec.ena = VNa
                h.vshift_na = vshiftna
                h.thi1_na = -58
                h.thi2_na = -58
            sec.insert('kv')
            sec.ek = Vk

            sec.insert('kl')
            h.distance(0,0.5,sec=self.soma[0])
            for seg in sec.allseg():
                dist = h.distance(seg.x, sec=sec)
                if (dist>= ILdist):
                    sec(seg.x).gbar_kl = gkl
                else:
                    sec(seg.x).gbar_kl = 0



        #########################################
        # Set up properties for apical dendrites
        #########################################
        for sec in self.apical:
            sec.insert('pas')
            sec.e_pas = pasVm
            sec.insert('na')
            if h.ismembrane('na', sec = sec):
                sec.ena = VNa
                h.vshift_na = vshiftna
            sec.insert('kv')
            sec.ek = Vk
            sec.insert('kap')
            sec.insert('kad')
            sec.insert('ca')
            sec.insert('it')  # Properties from CaT.mod
            sec.vh1_it = 56
            sec.vh2_it = 415
            sec.ah_it = 30
            sec.v12m_it = 45
            sec.v12h_it = 65
            sec.am_it = 3
            sec.vshift_it = 10
            sec.vm1_it = 50
            sec.vm2_it = 125

            if h.ismembrane ('ca_ion', sec = sec):
                sec.eca = 140
                h.ion_style("ca_ion", 0, 1, 0, 0, 0)
                h.vshift_ca = 10

            sec.insert('cad')

        self.gna_control()
        self.distCa()
        self.distKV()
        self.distKA()
        self.distspines()


#########################################
# Distribution of sodium channels
#########################################
    def gna_control(self):
        for sec in self.soma:
            sec.gbar_na = somaNa


        for sec in self.basal_list:
            h.distance(0, 0.5, sec = self.soma[0])
            for seg in sec.allseg():
                dist = h.distance(seg.x, sec = sec)
                gNalin = basalNa - mNa * dist
                if (gNalin > gNamax):
                    gNalin = gNamax
                    print "Setting basal Na to maximum ",gNamax,
                    " at distance ",dist," in basal dendrite ", sec.name()
                elif (gNalin < 0):
                    gNalin = 0
                    print "Setting basal Na to zero at distance ",dist,
                    " in basal dendrite ",sec.name()
                sec(seg.x).gbar_na = gNalin

        for sec in self.axon:
            sec.gbar_na = axonNa

        for sec in self.apical:
            sec.gbar_na = apicalNa

#########################################
# Distribution of potassium channels
#########################################
    def distKV(self):


        for sec in self.soma:
            sec.gbar_kv = somaKv

        for sec in self.basal_list:
            h.distance(0,0.5,sec=self.soma[0])
            for seg in sec.allseg():
                dist = h.distance(seg.x, sec=sec)
                gKVlin = somaKv + mKV * dist
                if (gKVlin > gKVmax):
                    gKVlin = gKVmax
                    print "Setting basal GKV to maximum ",gKVmax," at distance ",dist," in basal dendrite",sec.name()
                elif (gKVlin < 0):
                    gKVlin = 0
                    print "Setting basal GKV to zero at distance ",dist," in basal dendrite ",sec.name()
                sec(seg.x).gbar_kv = gKVlin

        for sec in self.axon:
            sec.gbar_kv = axonKv

        for sec in self.apical:
            sec.gbar_kv = somaKv

#########################################
# Distribution of potassium channels
#########################################
    def distKA(self):

        for sec in self.soma:
            gkabar_kap = somaKA/1e4

        for sec in self.basal_list:
            h.distance(0,0.5,sec=self.soma[0])
            for seg in sec.allseg():
                dist = h.distance(seg.x, sec=sec)
                gkalin = somaKA + mgka*dist
                ratiolin = 1 - mgkaratio*dist
                if (ratiolin < 0):
                    ratio = 0
                else:
                    ratio = ratiolin

                if (gkalin > gkamax):
                    gkalin = gkamax
                    print "Setting GKA to maximum ",gkamax," in basal dendrite",sec.name()
                elif (gkalin < 0):
                    gkalin = 0
                    print "Setting GKA to 0 in basal dendrite",sec.name()
                sec(seg.x).gkabar_kap = gkalin * ratio/1e4
                sec(seg.x).gkabar_kad = gkalin * (1-ratio)/1e4

        for sec in self.apical:
            h.distance(0,0.5,sec=self.soma[0])
            for seg in sec.allseg():
                dist = h.distance(seg.x, sec=sec)
                ratiolin = 1 - mgkaratio*dist
                if (ratiolin < 0):
                    ratio = 0
                else:
                    ratio = ratiolin
                sec(seg.x).gkabar_kap = apicalKA*ratio/1e4
                sec(seg.x).gkabar_kad = apicalKA*(1-ratio)/1e4

#########################################
# Distribution of Ca channels
#########################################
    def distCa(self):
        for sec in self.soma:
            sec.gbar_ca = somaCa * gcaratio
            sec.gbar_it = somaCa *(1-gcaratio)/1e4

        for sec in self.basal_list:
            h.distance(0,0.5,sec = self.soma[0])
            for seg in sec.allseg():
                dist = h.distance(seg.x, sec = sec)
                if (dist > cadist):
                    sec(seg.x).gbar_ca = dendCa * gcaratio
                    sec(seg.x).gbar_it = dendCa * (1-gcaratio)/1e4
                else:
                    sec(seg.x).gbar_ca = somaCa * gcaratio
                    sec(seg.x).gbar_it = somaCa * (1-gcaratio)/1e4

        for sec in self.apical:
            h.distance(0,0.5,sec = self.soma[0])
            for seg in sec.allseg():
                dist = h.distance(seg.x, sec=sec)
                if (dist > cadist):
                    sec(seg.x).gbar_ca = dendCa * gcaratio
                    sec(seg.x).gbar_it = dendCa * (1-gcaratio)/1e4
                else:
                    sec(seg.x).gbar_ca = somaCa * gcaratio
                    sec(seg.x).gbar_it = somaCa * (1-gcaratio)/1e4

#########################################
# Distribution of spines on dendrites (This should be optimized!!!)
#########################################
    def distspines(self):

        for sec in self.basal_list:
            h.distance(0,0.5,sec = self.soma[0])
            for seg in sec.allseg():
                dist = h.distance(seg.x, sec=sec)
                if (dist >= spinedist):
                    sec(seg.x).cm = dendCm
                    sec(seg.x).g_pas = 1./dendRm
                else:
                    sec(seg.x).cm = somaCm
                    sec(seg.x).g_pas = 1./somaRm

        for sec in self.apical:
            h.distance(0,0.5,sec = self.soma[0])
            for seg in sec.allseg():
                dist = h.distance(seg.x, sec=sec)
                if (dist >= spinedist):
                    sec(seg.x).cm = dendCm
                    sec(seg.x).g_pas = 1./dendRm
                else:
                    sec(seg.x).cm = somaCm
                    sec(seg.x).g_pas = 1./somaRm



#    def recalculate_x_dist(self):
#        for sec in h.allsec():
#            h.distance(0,0.5,sec=self.soma[0])
#            for seg in sec.allseg():
#                seg.x_savedist = h.distance(seg.x, sec=sec)

############################################
### Other functions
############################################
def distNaSD(section, b_Na):
    """
    Change sodium channel density on the targeted basal dendrites
    """
    h.distance(0,0.5,sec=h.soma[0])
    for seg in section.allseg():
        dist = h.distance(seg.x, sec=section)
        gNalin = b_Na - mNa * dist
        if (gNalin > gNamax):
            gNalin = gNamax
            print "Setting basal Na to maximum ",gNamax," at distance ",dist," in basal dendrite ",section.name()
        elif (gNalin < 0):
            gNalin = 0
            print "Setting basal Na to zero at distance ",dist," in basal dendrite ",section.name()
        section(seg.x).gbar_na = gNalin


def distKASD (section, soma_KA):
    """
    Change potassium channel density on the targeted basal dendrites
    """
    h.distance(0,0.5,sec=h.soma[0])
    for seg in section.allseg():
        dist = h.distance(seg.x, sec=section)
        gkalin = soma_KA + mgka*dist
        ratiolin = 1 - mgkaratio*dist
        if (ratiolin < 0):
            ratio = 0
        else:
            ratio = ratiolin
        if (gkalin > gkamax):
            section(seg.x).gkabar_kap = gkamax * ratio/1e4
            section(seg.x).gkabar_kad = gkamax * (1-ratio)/1e4
        else:
            section(seg.x).gkabar_kap = gkalin * ratio/1e4
            section(seg.x).gkabar_kad = gkalin * (1-ratio)/1e4


def TTX():
    for sec in h.allsec():
        sec.gbar_na = 0

############################################
# Function for importing cell into NetPyNE
############################################
def MakeCA229 ():
    cell = CA229()
    cell.init_once()
    return cell
