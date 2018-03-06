"""
CA229simp.py : Simplified morphology of reconstructed morphology of prefrontal layer V pyramidal cell from Acker, Antic (2008)

Original:
https://senselab.med.yale.edu/ModelDB/ShowModel.cshtml?model=117207&file=/acker_antic/Model/CA%20229.hoc#tabs-2
Modified by : Peng (Penny) Gao <penggao.1987@gmail.com>
Dec 01, 2017

Modified by Joe Graham <joe.w.graham@gmail.com>
2018-02-13
"""

import sys
from neuron import h #, gui
from matplotlib import pyplot
from math import sqrt, pi, log, exp

#########################################
# Parameters
#########################################
# Cell passive properties
global_Ra = 90
spineFACTOR = 1.5
somaRm = 1000/0.04
dendRm = somaRm/spineFACTOR
somaCm = 1
dendCm = somaCm*spineFACTOR
spinedist = 50 # distance at which spines start
Vk = -95 # -100 #-105 # -80
VNa = 65 #60 #65 #42 #60 # # 45 #60 #55 # 60
pasVm = -80 #-80 #-85 #-89 #-90 #-65

# Specify cell biophysics
somaNa = 150 # 900  # [pS/um2]
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

somaCa = 0.5 # total calcium channel conductance density of soma [pS/um^2]
# This value is original 2, set to 1 and 0.5 for better match with TTX trace
dendCa = 0.4 # dendritic total calcium conductance density
SomaCaT = 1 # 6 #1
# This value is original 8, set to 4,2,1 or 0 for better match with TTX trace
dendCaT = 1.6 #0.5
cadistB = 30  # dendritic calcium channel conductance equals that of soma up until this distance
cadistA = 30
#gcaratio = 0.2 #portion of gHVA to gHVA+gIT total, 1 is all HVA, 0 is all IT#
gkl = 0.005
ILdist = 15

#############kBK.mod
kBK_gpeak = 2.68e-4 #2.68e-4 #7.67842640257e-05 # Tried 2.68e-4 # original value of 268e-4 too high for this model
# 7.67842640257e-05 or 6.68e-4 both works, can change it based on the interspike invervals we are aiming for
kBK_caVhminShift = 45 #50 #45.0 # shift upwards to get lower effect on subthreshold


#########################################
# Set up the CA229simp cell class
#########################################

class CA229simp:
    """
    A detailed model of Prefrontal layer V pyramidal neuron in Rat.

    Channel distributions and all other biophysical properties of 
    model basal dendrites of prefrontal layer V pyramidal cell
    from Acker, Antic (2008) Membrane Exitability and Action 
    Potential Backpropagation in Basal Dendrites of Prefrontal
    Cortical Pyramidal Neurons.

    soma_2: soma compartment
    apical: apical dendrites
    basal: basal dendrites
    axon: axon
    all: SectionList of all the above compartments
    """

    def __init__(self):
        self.all = []
        self.create_cell()
        self.add_all()
        self.addsomachan()
        self.addapicalchan()
        self.addbasalchan()
        self.addaxonchan()
        self.gna_control()
        self.distCa()
        self.distKV()
        self.distKA()
        self.distspines()
        self.add_ih()
        self.add_CaK()


    ###################
    # Add basic properties
    ###################
    def add_all(self):
        for sec in self.all:
            sec.insert('vmax')
            sec.insert('pas')
            sec.e_pas = pasVm
            sec.insert('na')
            sec.insert('na_ion')
            sec.insert('k_ion')
            sec.ena = VNa
            h.vshift_na = vshiftna
            sec.ek = Vk
            sec.insert('kv')


        for sec in self.all_no_axon:
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
            sec.insert('ca_ion')
            sec.eca = 140
            h.vshift_ca = 10
            sec.insert('cad')
            h.taur_cad = 100

    ###################
    # Set up properties only in soma
    ###################
    def addsomachan(self):
        for sec in self.soma_2:
            sec.cm = somaCm
            sec.g_pas = 1./somaRm
            # if h.ismembrane('na', sec = sec):
            #     sec.ena = VNa
            #     h.vshift_na = vshiftna
            # if h.ismembrane ('ca_ion', sec = sec):
            #     sec.eca = 140
            #     h.ion_style("ca_ion", 0, 1, 0, 0, 0)
            #     h.vshift_ca = 10

    ###################
    # Set up properties in apical dendrites
    ###################
    def addapicalchan(self):
        for sec in self.apical:
            sec.insert('kad')

    ###################
    # Set up properties in basal dendrites
    ###################
    def addbasalchan(self):
        for sec in self.basals:
            sec.insert('kad')

    ###################
    # Set up properties only in axon
    ###################
    def addaxonchan(self):
        #for sec in self.axon:
            sec = self.axon

            sec.cm = somaCm
            sec.g_pas = 1./somaRm
            h.thi1_na = -58
            h.thi2_na = -58
            sec.insert('kl')
            #h.distance(0,0.5,sec=self.soma[0])
            h.distance(0,0.5,sec=self.soma_2)
            for seg in sec.allseg():
                dist = h.distance(seg.x, sec=sec)
                if (dist>= ILdist):
                    sec(seg.x).gbar_kl = gkl
                else:
                    sec(seg.x).gbar_kl = 0

#########################################
# Distribution of sodium channels
#########################################
    def gna_control(self):
        for sec in self.soma_2:
            sec.gbar_na = somaNa

        for sec in self.basals:
            h.distance(0, 0.5, sec = self.soma_2)
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

        #for sec in self.axon:
        sec = self.axon
        h.distance(0, 0.5, sec = self.soma_2)
        for seg in sec.allseg():
            dist = h.distance(seg.x, sec = sec)
            if (dist >= 50 and dist <= 100):
                sec(seg.x).gbar_na = axonNa
            else:
                sec(seg.x).gbar_na = somaNa

        for sec in self.apical:
            sec.gbar_na = apicalNa

#########################################
# Distribution of potassium channels
#########################################
    def distKV(self):
        for sec in self.soma_2:
            sec.gbar_kv = somaKv

        for sec in self.basals:
            h.distance(0,0.5,sec=self.soma_2)
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

        for sec in self.soma_2:
            gkabar_kap = somaKA/1e4

        for sec in self.basals:
            h.distance(0,0.5,sec=self.soma_2)
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
            h.distance(0,0.5,sec=self.soma_2)
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
        for sec in self.soma_2:
            sec.gbar_ca = somaCa
            sec.gbar_it = SomaCaT/1e4

        for sec in self.basals:
            h.distance(0,0.5,sec = self.soma_2)
            for seg in sec.allseg():
                dist = h.distance(seg.x, sec = sec)
                if (dist > cadistB):
                    sec(seg.x).gbar_ca = dendCa
                    sec(seg.x).gbar_it = dendCaT/1e4
                else:
                    sec(seg.x).gbar_ca = somaCa
                    sec(seg.x).gbar_it = SomaCaT/1e4

        for sec in self.apical:
            h.distance(0,0.5,sec = self.soma_2)
            for seg in sec.allseg():
                dist = h.distance(seg.x, sec=sec)
                if (dist > cadistA):
                    sec(seg.x).gbar_ca = dendCa
                    sec(seg.x).gbar_it = dendCaT/1e4
                else:
                    sec(seg.x).gbar_ca = somaCa
                    sec(seg.x).gbar_it = SomaCaT/1e4

#########################################
# Distribution of spines on dendrites (This should be optimized!!!)
#########################################
    def distspines(self):
        for sec in self.basals:
            h.distance(0,0.5,sec = self.soma_2)
            for seg in sec.allseg():
                dist = h.distance(seg.x, sec=sec)
                if (dist >= spinedist):
                    sec(seg.x).cm = dendCm
                    sec(seg.x).g_pas = 1./dendRm
                else:
                    sec(seg.x).cm = somaCm
                    sec(seg.x).g_pas = 1./somaRm

        for sec in self.apical:
            h.distance(0,0.5,sec = self.soma_2)
            for seg in sec.allseg():
                dist = h.distance(seg.x, sec=sec)
                if (dist >= spinedist):
                    sec(seg.x).cm = dendCm
                    sec(seg.x).g_pas = 1./dendRm
                else:
                    sec(seg.x).cm = somaCm
                    sec(seg.x).g_pas = 1./somaRm

#########################################
# Add Ih channels
#########################################
    def add_ih(self):
        #for sec in self.soma:
        sec = self.soma_2
        sec.insert('Ih')
        sec.gIhbar_Ih = 0.0001

        for sec in self.basals:
            sec.insert('Ih')
            sec.gIhbar_Ih = 0.0001

        for sec in self.apical:
            sec.insert('Ih')
            h.distance(0,0.5,sec=self.soma_2)
            for seg in sec.allseg():
                dist = h.distance(seg.x, sec=sec)
                sec(seg.x).gIhbar_Ih = 0.0002*(-0.8696 + 2.0870*exp(dist/323))

#########################################
# Add calcium activated potassium current
#########################################
    # def add_SK(self):
    #     for sec in self.soma:
    #         sec.insert('SK_E2')
    #         sec.gSK_E2bar_SK_E2 = 0.00024 #0.0024 #0.00441
    #     # for sec in self.basals:
    #     #     sec.insert('SK_E2')
    #     #     sec.gSK_E2bar_SK_E2 = 0.0004 #0.0024 #0.00441
    #     for sec in self.apical:
    #         sec.insert('SK_E2')
    #         sec.gSK_E2bar_SK_E2 = 0.0012

    def add_CaK(self):
        for sec in self.apical:
            sec.insert('kBK')
            sec.gpeak_kBK = kBK_gpeak
            sec.caVhmin_kBK = -46.08 + kBK_caVhminShift
        for sec in self.basals:
            sec.insert('kBK')
            sec.gpeak_kBK = kBK_gpeak
            sec.caVhmin_kBK = -46.08 + kBK_caVhminShift
        #for sec in self.soma:
        sec = self.soma_2
        sec.insert('kBK')
        sec.gpeak_kBK = kBK_gpeak
        sec.caVhmin_kBK = -46.08 + kBK_caVhminShift

#########################################
# TTX
#########################################
    def TTX(self):
        for sec in self.all:
            sec.gbar_na = 0


#########################################
# No calcium
#########################################
    def no_ca(self):
        #for sec in self.soma:
        sec = self.soma_2
        sec.gbar_ca = 0
        sec.gbar_it = 0
        for sec in self.apical:
            sec.gbar_ca = 0
            sec.gbar_it = 0
        for sec in self.basals:
            sec.gbar_ca = 0
            sec.gbar_it = 0


#########################################
# 3D geometry of the cell
#########################################
    def create_cell(self):
        """
        Simplified morphology
        """
        # Geometric properties
        somaL     = 48.4 
        somaDiam  = 28.2
        axonL     = 594.3
        axonDiam  = 1.41 
        apicL     = 261.9 
        apicDiam  = 1.58 
        bdendL    = 200.0 
        bdendDiam = 2.28 
        
        bdendnseg = 99
        axonnseg  = 3

        self.add_comp('soma_2')
        self.add_comp('axon')
        self.add_comp('Bdend1')
        self.add_comp('Bdend2')
        self.add_comp('Adend1')
        self.add_comp('Adend2')
        self.add_comp('Adend3')
        self.apical = [self.Adend1, self.Adend2, self.Adend3]
        self.basals = [self.Bdend1, self.Bdend2]
        self.all_no_axon = [self.soma_2, self.Adend1, self.Adend2, self.Adend3, self.Bdend1, self.Bdend2]
        self.alldend = [self.Adend1, self.Adend2, self.Adend3, self.Bdend1, self.Bdend2]
        
        self.axon.L = axonL; self.axon.diam = axonDiam;
        self.soma_2.L = somaL; self.soma_2.diam = somaDiam
        for sec in self.apical: 
            sec.L, sec.diam = apicL, apicDiam
        self.Bdend1.L = bdendL; self.Bdend1.diam = bdendDiam
        self.Bdend2.L = bdendL; self.Bdend2.diam = bdendDiam
        
        #self.axon.nseg = axonnseg
        self.Bdend1.nseg = bdendnseg
        self.Bdend2.nseg = bdendnseg

        self.axon.connect(self.soma_2,     0.0, 0.0)
        self.Bdend1.connect(self.soma_2,   0.5, 0.0) # soma 0.5 to Bdend1 0
        self.Bdend2.connect(self.soma_2,   0.5, 0.0) 
        self.Adend1.connect(self.soma_2,   1.0, 0.0)
        self.Adend2.connect(self.Adend1, 1.0, 0.0)
        self.Adend3.connect(self.Adend2, 1.0, 0.0)

    def add_comp(self, name):
        self.__dict__[name] = h.Section(name=name, cell=self)
        self.all.append(self.__dict__[name]) 


############################################
# Function for importing cell into NetPyNE
############################################
def MakeCA229simp():
    cell = CA229simp()
    return cell
