"""
CA229.py
: Reconstructed prefrontal layer V pyramidal neuron with detailed morphology
and active channels  ---  Acker and Antic (2009)

Original:
https://senselab.med.yale.edu/ModelDB/ShowModel.cshtml?model=117207&file=/acker_antic/Model/CA%20229.hoc#tabs-2
Modified by : Peng Penny Gao <penggao.1987@gmail.com>
Feb 01, 2018
The cell class has 3d morphology infomation,
and can be placed in a network (logical 3d location).

Improved on March 01, 2018 to have better membrane time constant & resting membrane potential.
Previous model has time constant ~ 6ms, most experimental data of
neocortex pyramidal L5-6 neurons have time constant ~ 10ms.
somaRm increased from 1000/0.4 to 1500/0.04
somaCm increased from 1 to 1.45
dendCm increased to somaCm*spineFACTOR
pasVm increased from -80 to -65

Udated on April 03, 2018 to have better resting membrane potential
global_Ra = 100
spinedist = 40 :decreased from 50
Vk = -87 :increased from -100 shift the RMP towards higher potential
Vna = 75 :increased from 65
pasVm = -65

Update again on July 25, 2018. Go back to the original value of Vna
Vna = 60 : same as the 2009 model
SomaNa = 900 : increased from 150 to get a similar bAP responses as the 2009 model

Ref:
https://senselab.med.yale.edu/ModelDB/ShowModel.cshtml?model=117207&file=/acker_antic/Model/CA%20229.hoc#tabs-2
https://neuroelectro.org/neuron/111/
https://senselab.med.yale.edu/ModelDB/ShowModel.cshtml?model=168148&file=/stadler2014_layerV/LayerVinit.hoc#tabs-2

"""
import sys
from neuron import h, gui
from matplotlib import pyplot
from math import sqrt, pi, log, exp

#########################################
# Parameters
#########################################
# Cell passive properties
global_Ra = 100
spineFACTOR = 1.5
somaRm = 1500/0.04
dendRm = somaRm/spineFACTOR
somaCm = 1.45
############
dendCm = somaCm*spineFACTOR
spinedist = 40 # distance from soma where the spines start
Vk = -87
VNa = 60
pasVm = -65
# Specify cell biophysics
somaNa = 900  # [pS/um2]
axonNa = 5000   # [pS/um2]
basalNa = 150 # Increased to 200 in Fig2. D2 - boosted gNa [pS/um2]
mNa = 0.5 # decrease in sodium channel conductance in basal dendrites [pS/um2/um]
apicalNa = 375
gNamax = 2000  # maximum basal sodium conductance
vshiftna = -10
somaKv = 40 # somatic, apical, and initial basal Kv conductance
mKV = 0  # increase in KV conductance in basal dendrites
gKVmax = 500  # maximum basal KV conductance
axonKv = 100
somaKA = 150
mgka = 0.7  # linear rise in IA channel density
mgkaratio = 1./300 # linear drop in KAP portion, 1 at soma
apicalKA = 300  # apical total GKA conductance
gkamax = 2000  # pS/um2
somaCa = 2 # total calcium channel conductance density of soma [pS/um^2]
dendCa = 0.4 # dendritic total calcium conductance density
SomaCaT = 2 # This value was original 8, decrease to 2 for better match
dendCaT = 1.6
cadistB = 30 # basal dendritic calcium channel conductance equals that of soma up until this distance
cadistA = 30 # apical dendritic calcium channel conductance equals that of soma up until this distance
gkl = 0.005
ILdist = 15
#############BK.mod
kBK_gpeak = 2.68e-4
kBK_caVhminShift = 45 #shift upwards to get lower effect on subthreshold

#########################################
# Set up the CA229 cell class
#########################################

class CA229:
    """
    A detailed model of Prefrontal layer V pyramidal neuron in mice.

    Channel distributions and other biophysical properties are from
    the Acker and Antic 2009 model.

    Section name:
        soma: soma compartments (soma[0] - soma[3])
        apical: apical dendrites (apical[0] - apical[44])
        basal: basal dendrites (basal[0] - basal[35])
        basals: SectionList of all basal but excluing basal[16]
        axon: SectionList of basal[16] (basal[16] is modeled as axon here)
        all: SectionList of all the above compartments
    """

    #############
    def __init__(self, Na_ratio = 1.0, HVA_ratio = 1.0, LVA_ratio = 1.0,
    KA_ratio = 1.0, BK_ratio = 1.0):
        # Define the ratio of parameters to adjust systematically
        self.Na_ratio = Na_ratio
        self.HVA_ratio = HVA_ratio
        self.LVA_ratio = LVA_ratio
        self.KA_ratio = KA_ratio
        self.BK_ratio = BK_ratio
        self.create_cell()
        self.optimize_nseg()
        self.add_axon()
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
    # Set up nseg numbers for each branch
    ###################
    def geom_nseg (self):
        # local freq, d_lambda, before, after, tmp
        # these are reasonable values for most models
        freq = 100 # Hz, frequency at which AC length constant will be computed
        d_lambda = 0.05
        before = 0
        after = 0
        for sec in self.all: before += sec.nseg
        for sec in self.all:
            # creates the number of segments per section
            # lambda_f takes in the current section
            sec.nseg = int((sec.L/(d_lambda*self.lambda_f(sec))+0.9)/2)*2 + 1
        for sec in self.all: after += sec.nseg
        # print "geom_nseg: ", after, " total segments"

    def lambda_f (self, section):
        # these are reasonable values for most models
        freq = 100
        # The lowest number of n3d() is 2
        if (section.n3d() < 2):
            return 1e5*sqrt(section.diam/(4*pi*freq*section.Ra*section.cm))
        # above was too inaccurate with large variation in 3d diameter
        # so now we use all 3-d points to get a better approximate lambda
        x1 = section.arc3d(0)
        d1 = section.diam3d(0)
        self.lam = 0
        #print section, " n3d:", section.n3d(), " diam3d:", section.diam3d(0)
        for i in range(section.n3d()): #h.n3d()-1
            x2 = section.arc3d(i)
            d2 = section.diam3d(i)
            self.lam += (x2 - x1)/sqrt(d1 + d2)
            x1 = x2
            d1 = d2
            #  length of the section in units of lambda
        self.lam *= sqrt(2) * 1e-5*sqrt(4*pi*freq*section.Ra*section.cm)
        return section.L/self.lam

    def optimize_nseg (self):
        """
        Set up nseg
        """
        # Set up sectionList - easy to modify the properties of all branches
        self.all = h.SectionList()
        self.all_no_axon = h.SectionList()
        for section in self.soma:
            self.all.append(sec = section)
            self.all_no_axon.append(sec = section)
        for section in self.basal:
            self.all.append(sec = section)
        for section in self.apical:
            self.all.append(sec = section)
            self.all_no_axon.append(sec = section)
        self.basals = h.SectionList()
        self.axon = h.SectionList()
        self.axon.append(sec = self.basal[16])
        for section in self.basal:
            self.basals.append(sec = section)
        self.basals.remove(sec = self.basal[16])
        for section in self.basals:
            self.all_no_axon.append(sec = section)

        for sec in self.all:
            # Set up Ra and cm first:
            # the nseg calculation depends on the value of Ra and cm
            sec.Ra = global_Ra
            sec.cm = 1
        # give each compartment segment number
        self.geom_nseg()

    ###################
    # Reset axon length
    ###################
    def add_axon(self):
        """
        Set up the SectionLists and temporal axon branch.
        """
        self.basal[16].L = 200
        self.basal[16].nseg = 15
        h.distance(0,0.5,sec=self.soma[0])
        for seg in self.basal[16].allseg():
            dist = h.distance(seg.x, sec=self.basal[16])
            if (dist <= 15):
                self.basal[16](seg.x).diam = 1.725
            elif (dist > 15 and dist<= 30):
                self.basal[16](seg.x).diam = 1.119
            else:
                self.basal[16](seg.x).diam = 0.96

    ###################
    # Add channel properties
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
    # Set up channel properties only in soma
    ###################
    def addsomachan(self):
        for sec in self.soma:
            sec.cm = somaCm
            sec.g_pas = 1./somaRm

    ###################
    # Set up channel properties only in apical dendrites
    ###################
    def addapicalchan(self):
        for sec in self.apical:
            sec.insert('kad')

    ###################
    # Set up channel properties only in basal dendrites
    ###################
    def addbasalchan(self):
        for sec in self.basals:
            sec.insert('kad')

    ###################
    # Set up channel properties only in axon
    ###################
    def addaxonchan(self):
        for sec in self.axon:
            sec.cm = somaCm
            sec.g_pas = 1./somaRm
            h.thi1_na = -58
            h.thi2_na = -58

            sec.insert('kl')
            h.distance(0,0.5,sec=self.soma[0])
            for seg in sec.allseg():
                dist = h.distance(seg.x, sec=sec)
                if (dist>= ILdist):
                    sec(seg.x).gbar_kl = gkl
                else:
                    sec(seg.x).gbar_kl = 0

#########################################
# Distribution of sodium channel density
#########################################
    def gna_control(self):
        for sec in self.soma:
            sec.gbar_na = somaNa * self.Na_ratio

        for sec in self.basals:
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
                sec(seg.x).gbar_na = gNalin * self.Na_ratio

        # Note: don't add ratio to axon, only modify basal, apical and soma sodium channel conductances
        for sec in self.axon:
            h.distance(0, 0.5, sec = self.soma[0])
            for seg in sec.allseg():
                dist = h.distance(seg.x, sec = sec)
                if (dist >= 35 and dist <= 50):
                    sec(seg.x).gbar_na = axonNa
                else:
                    sec(seg.x).gbar_na = somaNa

        for sec in self.apical:
            sec.gbar_na = apicalNa * self.Na_ratio

#########################################
# Distribution of potassium channel density
#########################################
    def distKV(self):
        for sec in self.soma:
            sec.gbar_kv = somaKv

        for sec in self.basals:
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
# Distribution of A-type potassium channel density
#########################################
    def distKA(self):

        for sec in self.soma:
            gkabar_kap = somaKA/1e4 * self.KA_ratio

        for sec in self.basals:
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
                sec(seg.x).gkabar_kap = gkalin * ratio/1e4 * self.KA_ratio
                sec(seg.x).gkabar_kad = gkalin * (1-ratio)/1e4 * self.KA_ratio

        for sec in self.apical:
            h.distance(0,0.5,sec=self.soma[0])
            for seg in sec.allseg():
                dist = h.distance(seg.x, sec=sec)
                ratiolin = 1 - mgkaratio*dist
                if (ratiolin < 0):
                    ratio = 0
                else:
                    ratio = ratiolin
                sec(seg.x).gkabar_kap = apicalKA*ratio/1e4 * self.KA_ratio
                sec(seg.x).gkabar_kad = apicalKA*(1-ratio)/1e4 * self.KA_ratio

#########################################
# Distribution of Ca channel density
#########################################
    def distCa(self):
        for sec in self.soma:
            sec.gbar_ca = somaCa * self.HVA_ratio
            sec.gbar_it = SomaCaT/1e4 * self.LVA_ratio

        for sec in self.basals:
            h.distance(0,0.5,sec = self.soma[0])
            for seg in sec.allseg():
                dist = h.distance(seg.x, sec = sec)
                if (dist > cadistB):
                    sec(seg.x).gbar_ca = dendCa * self.HVA_ratio
                    sec(seg.x).gbar_it = dendCaT/1e4 * self.LVA_ratio
                else:
                    sec(seg.x).gbar_ca = somaCa * self.HVA_ratio
                    sec(seg.x).gbar_it = SomaCaT/1e4 * self.LVA_ratio

        for sec in self.apical:
            h.distance(0,0.5,sec = self.soma[0])
            for seg in sec.allseg():
                dist = h.distance(seg.x, sec=sec)
                if (dist > cadistA):
                    sec(seg.x).gbar_ca = dendCa * self.HVA_ratio
                    sec(seg.x).gbar_it = dendCaT/1e4 * self.LVA_ratio
                else:
                    sec(seg.x).gbar_ca = somaCa * self.HVA_ratio
                    sec(seg.x).gbar_it = SomaCaT/1e4 * self.LVA_ratio

#########################################
# Distribution of spines on dendrites
#########################################
    def distspines(self):
        for sec in self.basals:
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

#########################################
# Add Ih channels
#########################################
    def add_ih(self):
        for sec in self.soma:
            sec.insert('Ih')
            sec.gIhbar_Ih = 0.0001

        for sec in self.basals:
            sec.insert('Ih')
            sec.gIhbar_Ih = 0.0001

        for sec in self.apical:
            sec.insert('Ih')
            h.distance(0,0.5,sec=self.soma[0])
            for seg in sec.allseg():
                dist = h.distance(seg.x, sec=sec)
                sec(seg.x).gIhbar_Ih = 0.0002*(-0.8696 + 2.0870*exp(dist/323))

#########################################
# Add calcium activated potassium channels
#########################################
    def add_CaK(self, ratio = 1.0):
        for sec in self.apical:
            sec.insert('kBK')
            sec.gpeak_kBK = kBK_gpeak * self.BK_ratio
            sec.caVhmin_kBK = -46.08 + kBK_caVhminShift
        for sec in self.basals:
            sec.insert('kBK')
            sec.gpeak_kBK = kBK_gpeak * self.BK_ratio
            sec.caVhmin_kBK = -46.08 + kBK_caVhminShift
        for sec in self.soma:
            sec.insert('kBK')
            sec.gpeak_kBK = kBK_gpeak * self.BK_ratio
            sec.caVhmin_kBK = -46.08 + kBK_caVhminShift

#########################################
# Model the experiment with TTX application
#########################################
    def TTX(self):
        for sec in self.all:
            sec.gbar_na = 0

    def TTX_bAP(self):
        for sec in self.basals:
            sec.gbar_na = 0

#########################################
# No calcium
#########################################
    def no_ca(self):
        for sec in self.soma:
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
        3D morphology of CA229 cell.
        The diam and L of each compartment is determined by 3D structure.
        Same as hoc 3D morphology: CA229.hoc
        """
        self.soma = [h.Section(name='soma[%d]' % i) for i in xrange(4)]
        self.apical = [h.Section(name='apical[%d]' % i) for i in xrange(45)]
        self.basal = [h.Section(name='basal[%d]' % i) for i in xrange(36)]

        # Set up the 3d morphology and connection of soma
        h.pt3dclear(sec = self.soma[0])
        h.pt3dstyle(1, -53.42,3.52,-5.95,13.43, sec = self.soma[0])
        h.pt3dadd(-53.42,3.52,-5.96,13.43, sec = self.soma[0])
        # Default diameter of 500 um and a length of 1e-9 um is using without setting
        # Add this to be able to measure input resistance at location soma[0]
        h.pt3dadd(-53.42,3.53,-5.96,13.43, sec = self.soma[0])

        self.soma[1].connect(self.soma[0])
        h.pt3dclear(sec = self.soma[1])
        h.pt3dadd(-53.42,3.52,-5.96,13.43, sec = self.soma[1])
        h.pt3dadd(-53.74,0.93,-5.96,15.35, sec = self.soma[1])
        h.pt3dadd(-54.06,-1.66,-5.96,11.51, sec = self.soma[1])

        self.soma[3].connect(self.soma[0])
        h.pt3dclear(sec = self.soma[3])
        h.pt3dadd(-53.42,3.52,-5.96,13.43, sec = self.soma[3])
        h.pt3dadd(-53.1,6.12,-5.96,11.19, sec = self.soma[3])
        h.pt3dadd(-52.78,8.71,-5.96,9.59, sec = self.soma[3])
        h.pt3dadd(-52.78,11.62,-5.96,7.36, sec = self.soma[3])
        h.pt3dadd(-53.1,14.22,-5.96,5.76, sec = self.soma[3])

        self.soma[2].connect(self.soma[1])
        h.pt3dclear(sec = self.soma[2])
        h.pt3dadd(-54.06,-1.66,-5.96,11.51, sec = self.soma[2])
        h.pt3dadd(-54.06,-4.25,-5.96,7.99, sec = self.soma[2])

        # Set up the 3d morphology and connection of basal dendrites
        self.basal[0].connect(self.soma[1])
        h.pt3dclear(sec = self.basal[0])
        h.pt3dadd(-54.06,-1.66,-5.96,2.5, sec = self.basal[0])
        h.pt3dadd(-46.01,-2.93,-0.02,2.24, sec = self.basal[0])
        h.pt3dadd(-40.25,-4.54,-1.6,1.6, sec = self.basal[0])
        h.pt3dadd(-36.368,-6.407,-1.016,1.6, sec = self.basal[0])
        h.pt3dadd(-33.866,-7.55,0.69,1.6, sec = self.basal[0])

        self.basal[1].connect(self.basal[0])
        h.pt3dclear(sec = self.basal[1])
        h.pt3dadd(-33.866,-7.55,0.69,1.6, sec = self.basal[1])
        h.pt3dadd(-29.246,-9.33,-9.55,1.28, sec = self.basal[1])

        self.basal[2].connect(self.basal[1])
        h.pt3dclear(sec = self.basal[2])
        h.pt3dadd(-29.246,-9.33,-9.55,1.28, sec = self.basal[2])
        h.pt3dadd(-25.336,-8.93,-9.03,0.96, sec = self.basal[2])
        h.pt3dadd(-18.626,-8.93,-10.91,0.96, sec = self.basal[2])
        h.pt3dadd(-13.826,-6.99,-10.91,0.96, sec = self.basal[2])
        h.pt3dadd(-9.356,-6.02,-8.59,0.96, sec = self.basal[2])
        h.pt3dadd(-4.556,-5.04,-8.59,0.96, sec = self.basal[2])
        h.pt3dadd(-0.396,-4.07,-10.83,0.96, sec = self.basal[2])
        h.pt3dadd(5.044,-1.8,-7.45,0.64, sec = self.basal[2])

        self.basal[3].connect(self.basal[2])
        h.pt3dclear(sec = self.basal[3])
        h.pt3dadd(5.044,-1.8,-7.45,0.64, sec = self.basal[3])
        h.pt3dadd(8.234,1.44,-4.49,0.64, sec = self.basal[3])
        h.pt3dadd(11.434,3.05,-5.77,0.64, sec = self.basal[3])
        h.pt3dadd(14.314,7.59,-3.25,0.64, sec = self.basal[3])

        self.basal[4].connect(self.basal[2])
        h.pt3dclear(sec = self.basal[4])
        h.pt3dadd(5.044,-1.8,-7.45,0.64, sec = self.basal[4])
        h.pt3dadd(8.874,-3.1,-7.57,0.64, sec = self.basal[4])
        h.pt3dadd(12.394,-4.72,-7.57,0.64, sec = self.basal[4])
        h.pt3dadd(16.874,-6.02,-3.27,0.64, sec = self.basal[4])
        h.pt3dadd(21.024,-4.72,-3.27,0.64, sec = self.basal[4])
        h.pt3dadd(27.104,-5.69,-3.27,0.64, sec = self.basal[4])
        h.pt3dadd(34.144,-5.04,-3.27,0.64, sec = self.basal[4])
        h.pt3dadd(42.134,-5.37,-5.95,0.64, sec = self.basal[4])

        self.basal[5].connect(self.basal[1])
        h.pt3dclear(sec = self.basal[5])
        h.pt3dadd(-29.246,-9.33,-9.55,1.28, sec = self.basal[5])
        h.pt3dadd(-28.926,-14.19,-13.17,1.28, sec = self.basal[5])

        self.basal[6].connect(self.basal[5])
        h.pt3dclear(sec = self.basal[6])
        h.pt3dadd(-28.926,-14.19,-13.17,1.28, sec = self.basal[6])
        h.pt3dadd(-25.836,-15.3,-16.87,0.64, sec = self.basal[6])
        h.pt3dadd(-26.156,-17.89,-16.87,0.64, sec = self.basal[6])
        h.pt3dadd(-24.024,-22.264,-18.55,0.64, sec = self.basal[6])
        h.pt3dadd(-20.516,-26.376,-20.924,0.64, sec = self.basal[6])
        h.pt3dadd(-19.246,-30.256,-23.784,0.64, sec = self.basal[6])
        h.pt3dadd(-19.886,-33.496,-26.964,0.64, sec = self.basal[6])
        h.pt3dadd(-17.326,-36.416,-28.544,0.494, sec = self.basal[6])
        h.pt3dadd(-15.726,-39.336,-32.184,0.53, sec = self.basal[6])
        h.pt3dadd(-15.086,-40.306,-42.104,0.612, sec = self.basal[6])

        self.basal[7].connect(self.basal[6])
        h.pt3dclear(sec = self.basal[7])
        h.pt3dadd(-15.086,-40.306,-42.104,0.612, sec = self.basal[7])
        h.pt3dadd(-11.566,-38.036,-42.944,0.64, sec = self.basal[7])
        h.pt3dadd(-8.366,-37.716,-42.944,0.64, sec = self.basal[7])
        h.pt3dadd(-5.486,-39.006,-46.344,0.64, sec = self.basal[7])
        h.pt3dadd(-3.896,-41.596,-46.344,0.64, sec = self.basal[7])
        h.pt3dadd(-1.976,-44.196,-46.344,0.64, sec = self.basal[7])
        h.pt3dadd(0.264,-46.786,-50.644,0.52, sec = self.basal[7])
        h.pt3dadd(2.824,-48.726,-50.684,0.476, sec = self.basal[7])
        h.pt3dadd(5.064,-50.026,-55.644,0.5, sec = self.basal[7])
        h.pt3dadd(10.814,-52.616,-61.884,0.456, sec = self.basal[7])
        h.pt3dadd(14.514,-55.326,-64.804,0.422, sec = self.basal[7])
        h.pt3dadd(16.434,-57.266,-64.804,0.304, sec = self.basal[7])
        h.pt3dadd(18.994,-60.186,-70.144,0.32, sec = self.basal[7])

        self.basal[8].connect(self.basal[6])
        h.pt3dclear(sec = self.basal[8])
        h.pt3dadd(-15.086,-40.306,-42.104,0.612, sec = self.basal[8])
        h.pt3dadd(-14.126,-42.571,-44.114,0.504, sec = self.basal[8])
        h.pt3dadd(-12.728,-46.195,-45.327,0.476, sec = self.basal[8])
        h.pt3dadd(-11.732,-50.174,-47.162,0.448, sec = self.basal[8])
        h.pt3dadd(-10.199,-52.853,-48.131,0.394, sec = self.basal[8])
        h.pt3dadd(-5.399,-56.093,-50.231,0.388, sec = self.basal[8])
        h.pt3dadd(-4.759,-58.363,-50.331,0.428, sec = self.basal[8])
        h.pt3dadd(-2.839,-60.633,-52.211,0.37, sec = self.basal[8])
        h.pt3dadd(-1.889,-63.873,-52.211,0.424, sec = self.basal[8])
        h.pt3dadd(0.671,-65.813,-52.211,0.406, sec = self.basal[8])
        h.pt3dadd(1.311,-71.643,-60.271,0.382, sec = self.basal[8])
        h.pt3dadd(3.551,-74.883,-63.351,0.414, sec = self.basal[8])
        h.pt3dadd(5.151,-78.123,-67.451,0.296, sec = self.basal[8])
        h.pt3dadd(5.151,-81.693,-71.031,0.32, sec = self.basal[8])

        self.basal[9].connect(self.basal[5])
        h.pt3dclear(sec = self.basal[9])
        h.pt3dadd(-28.926,-14.19,-13.17,1.28, sec = self.basal[9])
        h.pt3dadd(-30.846,-17.11,-16.15,1.082, sec = self.basal[9])
        h.pt3dadd(-32.766,-18.73,-16.15,1.08, sec = self.basal[9])
        h.pt3dadd(-32.126,-23.27,-17.47,1.102, sec = self.basal[9])
        h.pt3dadd(-33.406,-25.21,-17.47,1.068, sec = self.basal[9])
        h.pt3dadd(-35.646,-27.8,-18.05,1.098, sec = self.basal[9])
        h.pt3dadd(-39.156,-30.72,-18.77,1.094, sec = self.basal[9])
        h.pt3dadd(-40.116,-34.6,-20.11,1.132, sec = self.basal[9])

        self.basal[10].connect(self.basal[9])
        h.pt3dclear(sec = self.basal[10])
        h.pt3dadd(-40.116,-34.6,-20.11,1.132, sec = self.basal[10])
        h.pt3dadd(-39.906,-40.24,-24.57,0.96, sec = self.basal[10])
        h.pt3dadd(-39.906,-45.75,-24.57,0.96, sec = self.basal[10])
        h.pt3dadd(-38.668,-51.661,-25.382,0.96, sec = self.basal[10])
        h.pt3dadd(-38.572,-56.527,-25.946,0.96, sec = self.basal[10])
        h.pt3dadd(-39.342,-61.021,-26.78,0.96, sec = self.basal[10])
        h.pt3dadd(-40.302,-64.911,-26.78,1.008, sec = self.basal[10])
        h.pt3dadd(-39.662,-71.391,-28.04,0.96, sec = self.basal[10])
        h.pt3dadd(-39.982,-76.571,-29.98,0.64, sec = self.basal[10])
        h.pt3dadd(-41.216,-80.587,-31.934,0.64, sec = self.basal[10])
        h.pt3dadd(-42.92,-84.501,-32.904,0.64, sec = self.basal[10])
        h.pt3dadd(-45.16,-87.741,-30.504,0.64, sec = self.basal[10])
        h.pt3dadd(-46.44,-90.651,-31.344,0.64, sec = self.basal[10])
        h.pt3dadd(-47.4,-94.541,-31.344,0.64, sec = self.basal[10])
        h.pt3dadd(-47.4,-98.431,-32.864,0.64, sec = self.basal[10])
        h.pt3dadd(-47.72,-102.641,-34.304,0.64, sec = self.basal[10])
        h.pt3dadd(-49,-105.561,-34.304,0.64, sec = self.basal[10])
        h.pt3dadd(-48.68,-109.441,-35.684,0.64, sec = self.basal[10])
        h.pt3dadd(-47.4,-113.331,-35.684,0.64, sec = self.basal[10])
        h.pt3dadd(-46.76,-116.251,-34.264,0.64, sec = self.basal[10])
        h.pt3dadd(-46.76,-120.141,-31.004,0.446, sec = self.basal[10])
        h.pt3dadd(-46.12,-123.381,-26.584,0.386, sec = self.basal[10])
        h.pt3dadd(-44.2,-126.621,-26.584,0.398, sec = self.basal[10])

        self.basal[11].connect(self.basal[9])
        h.pt3dclear(sec = self.basal[11])
        h.pt3dadd(-40.116,-34.6,-20.11,1.132, sec = self.basal[11])
        h.pt3dadd(-41.716,-35.41,-23.29,1.13, sec = self.basal[11])
        h.pt3dadd(-45.096,-37.479,-24.752,1.124, sec = self.basal[11])
        h.pt3dadd(-47.299,-41.094,-25.735,1.036, sec = self.basal[11])
        h.pt3dadd(-48.612,-44.234,-27.368,1.092, sec = self.basal[11])
        h.pt3dadd(-49.572,-48.454,-30.748,1.086, sec = self.basal[11])
        h.pt3dadd(-51.812,-53.634,-30.748,0.99, sec = self.basal[11])
        h.pt3dadd(-52.02,-58.504,-31.286,1.008, sec = self.basal[11])
        h.pt3dadd(-51.485,-63.294,-31.63,1.058, sec = self.basal[11])
        h.pt3dadd(-51.508,-68.69,-33.076,1.012, sec = self.basal[11])
        h.pt3dadd(-53.108,-72.26,-35.296,0.958, sec = self.basal[11])
        h.pt3dadd(-54.388,-76.47,-37.036,0.774, sec = self.basal[11])
        h.pt3dadd(-56.938,-80.36,-39.256,0.772, sec = self.basal[11])
        h.pt3dadd(-56.298,-84.89,-40.956,0.798, sec = self.basal[11])
        h.pt3dadd(-57.698,-89.24,-45.596,0.738, sec = self.basal[11])
        h.pt3dadd(-58.968,-92.8,-52.736,0.64, sec = self.basal[11])

        self.basal[12].connect(self.basal[11])
        h.pt3dclear(sec = self.basal[12])
        h.pt3dadd(-58.968,-92.8,-52.736,0.64, sec = self.basal[12])
        h.pt3dadd(-57.698,-97.98,-51.616,0.64, sec = self.basal[12])

        self.basal[13].connect(self.basal[11])
        h.pt3dclear(sec = self.basal[13])
        h.pt3dadd(-58.968,-92.8,-52.736,0.64, sec = self.basal[13])
        h.pt3dadd(-62.488,-94.74,-53.496,0.548, sec = self.basal[13])
        h.pt3dadd(-66.008,-97.66,-55.516,0.452, sec = self.basal[13])
        h.pt3dadd(-68.888,-100.25,-57.636,0.39, sec = self.basal[13])
        h.pt3dadd(-72.408,-102.52,-59.716,0.32, sec = self.basal[13])

        self.basal[14].connect(self.basal[0])
        h.pt3dclear(sec = self.basal[14])
        h.pt3dadd(-33.866,-7.55,0.69,1.6, sec = self.basal[14])
        h.pt3dadd(-33.454,-9.753,0.736,1.38, sec = self.basal[14])
        h.pt3dadd(-32.081,-13.934,0.337,1.228, sec = self.basal[14])
        h.pt3dadd(-30.188,-16.751,0.108,1.242, sec = self.basal[14])
        h.pt3dadd(-26.988,-17.081,2.608,1.12, sec = self.basal[14])
        h.pt3dadd(-26.988,-20.321,3.708,1.124, sec = self.basal[14])
        h.pt3dadd(-27.628,-23.231,8.008,0.972, sec = self.basal[14])
        h.pt3dadd(-26.668,-26.471,10.388,1.032, sec = self.basal[14])
        h.pt3dadd(-24.758,-30.361,14.628,1, sec = self.basal[14])
        h.pt3dadd(-22.838,-32.951,14.628,0.962, sec = self.basal[14])
        h.pt3dadd(-22.518,-36.191,14.208,1.016, sec = self.basal[14])
        h.pt3dadd(-21.238,-38.461,14.208,0.922, sec = self.basal[14])
        h.pt3dadd(-20.918,-41.701,14.208,0.912, sec = self.basal[14])
        h.pt3dadd(-21.238,-44.291,15.168,0.89, sec = self.basal[14])
        h.pt3dadd(-19.638,-47.861,15.168,0.872, sec = self.basal[14])
        h.pt3dadd(-17.458,-53.202,15.019,0.82, sec = self.basal[14])
        h.pt3dadd(-16.847,-57.954,13.855,0.866, sec = self.basal[14])
        h.pt3dadd(-14.927,-62.494,13.775,0.788, sec = self.basal[14])
        h.pt3dadd(-13.007,-63.794,12.175,0.678, sec = self.basal[14])
        h.pt3dadd(-12.687,-67.354,12.175,0.672, sec = self.basal[14])
        h.pt3dadd(-9.817,-69.624,12.175,0.54, sec = self.basal[14])
        h.pt3dadd(-8.574,-74.473,11.45,0.7, sec = self.basal[14])
        h.pt3dadd(-5.827,-78.113,11.213,0.698, sec = self.basal[14])
        h.pt3dadd(-3.08,-81.753,10.977,0.692, sec = self.basal[14])
        h.pt3dadd(-1.16,-85.963,10.977,0.66, sec = self.basal[14])
        h.pt3dadd(2.68,-89.523,10.977,0.62, sec = self.basal[14])
        h.pt3dadd(4.6,-91.793,10.977,0.65, sec = self.basal[14])
        h.pt3dadd(4.6,-96.003,10.977,0.592, sec = self.basal[14])
        h.pt3dadd(4.6,-100.543,9.397,0.548, sec = self.basal[14])
        h.pt3dadd(7.504,-105.61,8.349,0.554, sec = self.basal[14])
        h.pt3dadd(12.467,-109.418,8.221,0.526, sec = self.basal[14])
        h.pt3dadd(14.387,-112.008,8.221,0.524, sec = self.basal[14])
        h.pt3dadd(15.337,-116.548,7.741,0.59, sec = self.basal[14])
        h.pt3dadd(16.297,-121.728,7.741,0.578, sec = self.basal[14])
        h.pt3dadd(18.537,-125.618,9.161,0.492, sec = self.basal[14])
        h.pt3dadd(20.457,-131.128,9.221,0.504, sec = self.basal[14])
        h.pt3dadd(20.457,-135.018,7.521,0.412, sec = self.basal[14])
        h.pt3dadd(19.497,-136.958,6.101,0.432, sec = self.basal[14])
        h.pt3dadd(20.457,-146.678,7.981,0.32, sec = self.basal[14])
        h.pt3dadd(20.607,-149.468,9.521,0.32, sec = self.basal[14])

        self.basal[15].connect(self.soma[2])
        h.pt3dclear(sec = self.basal[15])
        h.pt3dadd(-54.06,-4.25,-5.96,2.5, sec = self.basal[15])
        h.pt3dadd(-49.95,-7.22,3.6,2.156, sec = self.basal[15])
        h.pt3dadd(-48.67,-12.08,3.78,1.47, sec = self.basal[15])
        h.pt3dadd(-48.67,-17.27,4.7,1.206, sec = self.basal[15])
        h.pt3dadd(-47.39,-19.86,5.6,1.118, sec = self.basal[15])
        h.pt3dadd(-47.523,-24.137,7.008,1.088, sec = self.basal[15])
        h.pt3dadd(-47.787,-28.401,7.217,1.076, sec = self.basal[15])
        h.pt3dadd(-46.397,-32.726,7.605,1.096, sec = self.basal[15])
        h.pt3dadd(-46.523,-36.824,8.233,1.11, sec = self.basal[15])
        h.pt3dadd(-44.603,-41.034,6.453,1.036, sec = self.basal[15])
        h.pt3dadd(-42.043,-46.864,5.833,0.82, sec = self.basal[15])
        h.pt3dadd(-40.931,-51.092,1.762,0.72, sec = self.basal[15])
        h.pt3dadd(-39.371,-55.006,0.727,0.64, sec = self.basal[15])
        h.pt3dadd(-36.979,-57.042,0.736,0.64, sec = self.basal[15])
        h.pt3dadd(-34.782,-59.944,0.399,0.64, sec = self.basal[15])
        h.pt3dadd(-32.088,-62.488,0.371,0.64, sec = self.basal[15])
        h.pt3dadd(-29.848,-65.078,0.371,0.64, sec = self.basal[15])
        h.pt3dadd(-28.248,-68.968,-2.169,0.64, sec = self.basal[15])
        h.pt3dadd(-25.368,-69.938,-2.169,0.64, sec = self.basal[15])
        h.pt3dadd(-22.808,-71.558,-2.969,0.64, sec = self.basal[15])
        h.pt3dadd(-22.168,-74.798,-1.929,0.64, sec = self.basal[15])
        h.pt3dadd(-19.928,-78.368,-0.229,0.64, sec = self.basal[15])
        h.pt3dadd(-17.698,-82.898,-0.229,0.64, sec = self.basal[15])
        h.pt3dadd(-17.378,-88.088,-3.449,0.64, sec = self.basal[15])
        h.pt3dadd(-17.058,-92.618,-3.449,0.64, sec = self.basal[15])
        h.pt3dadd(-16.418,-96.508,0.131,0.64, sec = self.basal[15])
        h.pt3dadd(-15.178,-99.754,-0.075,0.64, sec = self.basal[15])
        h.pt3dadd(-13.399,-101.604,-0.737,0.64, sec = self.basal[15])
        h.pt3dadd(-12.171,-104.963,-1.239,0.64, sec = self.basal[15])
        h.pt3dadd(-10.571,-108.853,1.121,0.64, sec = self.basal[15])
        h.pt3dadd(-10.891,-113.393,3.021,0.64, sec = self.basal[15])
        h.pt3dadd(-11.519,-117.77,4.264,0.64, sec = self.basal[15])
        h.pt3dadd(-12.12,-122.248,4.078,0.64, sec = self.basal[15])
        h.pt3dadd(-13.423,-127.17,5.023,0.64, sec = self.basal[15])
        h.pt3dadd(-13.743,-132.36,7.783,0.64, sec = self.basal[15])
        h.pt3dadd(-16.133,-137.05,8.683,0.64, sec = self.basal[15])
        h.pt3dadd(-16.105,-139.642,7.714,0.64, sec = self.basal[15])
        h.pt3dadd(-15.71,-142.279,7.455,0.64, sec = self.basal[15])
        h.pt3dadd(-16.35,-146.809,8.095,0.64, sec = self.basal[15])
        h.pt3dadd(-19.23,-149.729,9.435,0.64, sec = self.basal[15])
        h.pt3dadd(-19.87,-153.609,10.595,0.64, sec = self.basal[15])
        h.pt3dadd(-21.79,-156.849,13.535,0.64, sec = self.basal[15])
        h.pt3dadd(-20.83,-160.419,13.535,0.64, sec = self.basal[15])
        h.pt3dadd(-21.47,-163.979,14.795,0.492, sec = self.basal[15])
        h.pt3dadd(-22.11,-169.169,16.355,0.404, sec = self.basal[15])
        h.pt3dadd(-21.79,-174.029,16.375,0.402, sec = self.basal[15])
        h.pt3dadd(-23.71,-178.559,14.595,0.404, sec = self.basal[15])
        h.pt3dadd(-24.99,-182.129,14.595,0.374, sec = self.basal[15])
        h.pt3dadd(-25.95,-186.009,14.595,0.32, sec = self.basal[15])
        h.pt3dadd(-27.23,-188.279,14.595,0.32, sec = self.basal[15])
        h.pt3dadd(-26.59,-191.519,17.275,0.32, sec = self.basal[15])
        h.pt3dadd(-29.61,-196.579,17.275,0.32, sec = self.basal[15])
        h.pt3dadd(-33.13,-200.469,19.755,0.32, sec = self.basal[15])

        self.basal[16].connect(self.soma[2])
        h.pt3dclear(sec = self.basal[16])
        h.pt3dadd(-54.06,-4.25,-5.96,2.5, sec = self.basal[16])
        h.pt3dadd(-57.1,-6.71,1.34,1.31, sec = self.basal[16])
        h.pt3dadd(-57.42,-14.48,1.54,1.226, sec = self.basal[16])
        h.pt3dadd(-59.66,-18.37,2.46,0.96, sec = self.basal[16])
        h.pt3dadd(-62.22,-20.96,4.94,0.96, sec = self.basal[16])
        h.pt3dadd(-63.18,-25.18,7.2,0.96, sec = self.basal[16])
        h.pt3dadd(-65.1,-29.06,10.1,0.96, sec = self.basal[16])

        self.basal[17].connect(self.soma[2])
        h.pt3dclear(sec = self.basal[17])
        h.pt3dadd(-54.06,-4.25,-5.96,2.5, sec = self.basal[17])
        h.pt3dadd(-58.33,-5.39,-5.2,1.914, sec = self.basal[17])
        h.pt3dadd(-60.57,-9.92,-19.84,1.6, sec = self.basal[17])

        self.basal[18].connect(self.basal[17])
        h.pt3dclear(sec = self.basal[18])
        h.pt3dadd(-60.57,-9.92,-19.84,1.6, sec = self.basal[18])
        h.pt3dadd(-65.52,-9.13,-22.5,1.088, sec = self.basal[18])
        h.pt3dadd(-69.68,-7.51,-24.56,0.96, sec = self.basal[18])
        h.pt3dadd(-74.16,-4.6,-25.9,0.96, sec = self.basal[18])
        h.pt3dadd(-77.99,-2.33,-26.92,0.96, sec = self.basal[18])

        self.basal[19].connect(self.basal[18])
        h.pt3dclear(sec = self.basal[19])
        h.pt3dadd(-77.99,-2.33,-26.92,0.96, sec = self.basal[19])
        h.pt3dadd(-79.73,-0.24,-30.98,0.96, sec = self.basal[19])
        h.pt3dadd(-83.098,2.124,-35.508,0.96, sec = self.basal[19])
        h.pt3dadd(-85.955,4.956,-40.509,0.96, sec = self.basal[19])
        h.pt3dadd(-87.875,8.836,-45.249,0.96, sec = self.basal[19])
        h.pt3dadd(-89.795,12.076,-47.129,0.96, sec = self.basal[19])
        h.pt3dadd(-90.435,15.646,-48.609,0.96, sec = self.basal[19])
        h.pt3dadd(-92.675,16.616,-53.969,0.96, sec = self.basal[19])
        h.pt3dadd(-94.275,19.526,-59.469,0.64, sec = self.basal[19])
        h.pt3dadd(-95.875,22.126,-60.809,0.64, sec = self.basal[19])
        h.pt3dadd(-98.755,24.386,-60.869,0.64, sec = self.basal[19])
        h.pt3dadd(-102.265,27.626,-63.749,0.64, sec = self.basal[19])
        h.pt3dadd(-104.825,31.196,-66.049,0.64, sec = self.basal[19])
        h.pt3dadd(-107.385,33.786,-70.129,0.64, sec = self.basal[19])

        self.basal[20].connect(self.basal[18])
        h.pt3dclear(sec = self.basal[20])
        h.pt3dadd(-77.99,-2.33,-26.92,0.96, sec = self.basal[20])
        h.pt3dadd(-82.79,-2.65,-28.06,0.74, sec = self.basal[20])
        h.pt3dadd(-87.59,-2.98,-26,0.738, sec = self.basal[20])
        h.pt3dadd(-90.763,-4.278,-25.829,0.804, sec = self.basal[20])
        h.pt3dadd(-95.4,-5.559,-25.739,0.778, sec = self.basal[20])
        h.pt3dadd(-99.767,-7.014,-25.498,0.9, sec = self.basal[20])
        h.pt3dadd(-102.79,-7.459,-25.391,0.73, sec = self.basal[20])
        h.pt3dadd(-106.31,-6.809,-24.611,0.64, sec = self.basal[20])
        h.pt3dadd(-108.55,-7.459,-24.031,0.64, sec = self.basal[20])
        h.pt3dadd(-111.11,-8.759,-23.331,0.64, sec = self.basal[20])
        h.pt3dadd(-114.048,-12.051,-23.429,0.604, sec = self.basal[20])
        h.pt3dadd(-116.649,-15.992,-23.457,0.648, sec = self.basal[20])
        h.pt3dadd(-118.676,-18.162,-23.352,0.61, sec = self.basal[20])
        h.pt3dadd(-122.506,-19.462,-22.932,0.614, sec = self.basal[20])
        h.pt3dadd(-124.93,-20.824,-23.543,0.602, sec = self.basal[20])
        h.pt3dadd(-128.255,-22.108,-24.483,0.512, sec = self.basal[20])
        h.pt3dadd(-131.712,-24.009,-25.028,0.486, sec = self.basal[20])
        h.pt3dadd(-133.632,-25.629,-27.428,0.468, sec = self.basal[20])
        h.pt3dadd(-136.832,-28.869,-27.748,0.404, sec = self.basal[20])
        h.pt3dadd(-140.672,-28.869,-28.448,0.4, sec = self.basal[20])
        h.pt3dadd(-145.782,-29.519,-28.508,0.488, sec = self.basal[20])
        h.pt3dadd(-149.622,-30.809,-28.948,0.492, sec = self.basal[20])
        h.pt3dadd(-155.382,-31.779,-27.388,0.428, sec = self.basal[20])
        h.pt3dadd(-159.852,-32.429,-26.628,0.448, sec = self.basal[20])
        h.pt3dadd(-164.652,-31.139,-24.128,0.41, sec = self.basal[20])
        h.pt3dadd(-168.492,-29.189,-22.088,0.396, sec = self.basal[20])
        h.pt3dadd(-177.122,-26.919,-22.688,0.5, sec = self.basal[20])
        h.pt3dadd(-182.102,-26.779,-22.988,0.426, sec = self.basal[20])
        h.pt3dadd(-186.262,-27.749,-24.568,0.414, sec = self.basal[20])
        h.pt3dadd(-191.702,-28.719,-26.068,0.4, sec = self.basal[20])
        h.pt3dadd(-199.052,-30.989,-26.648,0.378, sec = self.basal[20])
        h.pt3dadd(-210.562,-32.609,-27.068,0.39, sec = self.basal[20])

        self.basal[21].connect(self.basal[17])
        h.pt3dclear(sec = self.basal[21])
        h.pt3dadd(-60.57,-9.92,-19.84,1.6, sec = self.basal[21])
        h.pt3dadd(-60.57,-14.46,-21.62,1.28, sec = self.basal[21])
        h.pt3dadd(-59.297,-18.328,-22.197,1.28, sec = self.basal[21])
        h.pt3dadd(-58.861,-22.6,-22.725,1.28, sec = self.basal[21])
        h.pt3dadd(-59.203,-26.538,-23.53,1.28, sec = self.basal[21])
        h.pt3dadd(-59.843,-29.778,-25.81,1.28, sec = self.basal[21])

        self.basal[22].connect(self.basal[21])
        h.pt3dclear(sec = self.basal[22])
        h.pt3dadd(-59.843,-29.778,-25.81,1.28, sec = self.basal[22])
        h.pt3dadd(-63.233,-30.638,-25.59,0.96, sec = self.basal[22])
        h.pt3dadd(-66.433,-32.578,-26.67,0.774, sec = self.basal[22])
        h.pt3dadd(-68.033,-35.818,-27.07,0.822, sec = self.basal[22])
        h.pt3dadd(-71.35,-38.118,-27.057,0.818, sec = self.basal[22])
        h.pt3dadd(-75.262,-40.341,-27.546,0.816, sec = self.basal[22])
        h.pt3dadd(-79.098,-43.335,-27.25,0.808, sec = self.basal[22])
        h.pt3dadd(-82.288,-45.605,-27.25,0.782, sec = self.basal[22])
        h.pt3dadd(-86.128,-47.875,-28.73,0.806, sec = self.basal[22])
        h.pt3dadd(-90.405,-51.038,-28.876,0.724, sec = self.basal[22])
        h.pt3dadd(-95.435,-53.99,-29.034,0.64, sec = self.basal[22])
        h.pt3dadd(-101.195,-55.28,-31.314,0.64, sec = self.basal[22])
        h.pt3dadd(-104.352,-56.462,-32.367,0.64, sec = self.basal[22])
        h.pt3dadd(-106.847,-58.815,-33.579,0.584, sec = self.basal[22])
        h.pt3dadd(-108.592,-62.898,-34.595,0.632, sec = self.basal[22])
        h.pt3dadd(-109.728,-66.517,-36.074,0.704, sec = self.basal[22])
        h.pt3dadd(-112.928,-68.457,-38.554,0.728, sec = self.basal[22])
        h.pt3dadd(-116.128,-69.437,-38.554,0.682, sec = self.basal[22])
        h.pt3dadd(-119.638,-71.377,-41.954,0.67, sec = self.basal[22])
        h.pt3dadd(-123.848,-73.662,-41.956,0.604, sec = self.basal[22])
        h.pt3dadd(-127.498,-76.496,-41.933,0.606, sec = self.basal[22])
        h.pt3dadd(-131.338,-78.116,-41.453,0.546, sec = self.basal[22])
        h.pt3dadd(-134.858,-78.766,-41.453,0.478, sec = self.basal[22])
        h.pt3dadd(-138.698,-79.086,-41.453,0.48, sec = self.basal[22])
        h.pt3dadd(-141.248,-77.146,-39.793,0.552, sec = self.basal[22])
        h.pt3dadd(-145.728,-76.496,-39.793,0.478, sec = self.basal[22])
        h.pt3dadd(-150.528,-76.496,-39.793,0.5, sec = self.basal[22])
        h.pt3dadd(-153.408,-78.766,-40.533,0.552, sec = self.basal[22])
        h.pt3dadd(-154.998,-82.326,-44.853,0.478, sec = self.basal[22])
        h.pt3dadd(-157.878,-85.246,-44.853,0.52, sec = self.basal[22])
        h.pt3dadd(-162.038,-85.246,-48.813,0.486, sec = self.basal[22])
        h.pt3dadd(-165.878,-86.216,-48.813,0.506, sec = self.basal[22])
        h.pt3dadd(-170.028,-85.896,-50.953,0.506, sec = self.basal[22])
        h.pt3dadd(-174.628,-86.036,-52.873,0.434, sec = self.basal[22])
        h.pt3dadd(-177.508,-85.716,-55.873,0.382, sec = self.basal[22])
        h.pt3dadd(-183.268,-87.016,-58.953,0.426, sec = self.basal[22])
        h.pt3dadd(-189.018,-87.986,-58.953,0.342, sec = self.basal[22])
        h.pt3dadd(-194.778,-87.986,-58.953,0.408, sec = self.basal[22])
        h.pt3dadd(-199.898,-88.306,-56.093,0.352, sec = self.basal[22])

        self.basal[23].connect(self.basal[21])
        h.pt3dclear(sec = self.basal[23])
        h.pt3dadd(-59.843,-29.778,-25.81,1.28, sec = self.basal[23])
        h.pt3dadd(-59.523,-31.728,-24.95,1.28, sec = self.basal[23])

        self.basal[24].connect(self.basal[23])
        h.pt3dclear(sec = self.basal[24])
        h.pt3dadd(-59.523,-31.728,-24.95,1.28, sec = self.basal[24])
        h.pt3dadd(-60.033,-34.848,-27.77,1.014, sec = self.basal[24])
        h.pt3dadd(-61.194,-39.364,-27.36,0.928, sec = self.basal[24])
        h.pt3dadd(-61.369,-43.906,-26.715,0.842, sec = self.basal[24])
        h.pt3dadd(-60.729,-46.496,-24.115,0.904, sec = self.basal[24])
        h.pt3dadd(-60.089,-51.036,-21.235,0.912, sec = self.basal[24])
        h.pt3dadd(-59.139,-54.596,-20.835,0.908, sec = self.basal[24])
        h.pt3dadd(-58.898,-58.816,-20.302,0.89, sec = self.basal[24])
        h.pt3dadd(-61.025,-62.868,-19.689,0.872, sec = self.basal[24])
        h.pt3dadd(-61.938,-66.912,-18.401,0.834, sec = self.basal[24])
        h.pt3dadd(-61.618,-70.802,-16.441,0.694, sec = self.basal[24])
        h.pt3dadd(-61.618,-74.692,-16.441,0.748, sec = self.basal[24])
        h.pt3dadd(-63.563,-78.06,-15.268,0.736, sec = self.basal[24])
        h.pt3dadd(-66.626,-80.751,-14.195,0.726, sec = self.basal[24])
        h.pt3dadd(-68.546,-82.041,-13.355,0.722, sec = self.basal[24])
        h.pt3dadd(-69.186,-86.581,-13.355,0.724, sec = self.basal[24])
        h.pt3dadd(-71.746,-89.501,-13.035,0.782, sec = self.basal[24])
        h.pt3dadd(-72.386,-93.061,-12.835,0.812, sec = self.basal[24])
        h.pt3dadd(-73.986,-97.601,-12.995,0.66, sec = self.basal[24])
        h.pt3dadd(-76.546,-101.161,-12.995,0.612, sec = self.basal[24])
        h.pt3dadd(-77.186,-104.401,-12.995,0.668, sec = self.basal[24])
        h.pt3dadd(-78.466,-109.581,-15.175,0.666, sec = self.basal[24])
        h.pt3dadd(-77.826,-114.771,-15.175,0.39, sec = self.basal[24])

        self.basal[25].connect(self.basal[23])
        h.pt3dclear(sec = self.basal[25])
        h.pt3dadd(-59.523,-31.728,-24.95,1.28, sec = self.basal[25])
        h.pt3dadd(-58.243,-33.018,-27.75,0.964, sec = self.basal[25])
        h.pt3dadd(-57.851,-36.548,-27.926,0.814, sec = self.basal[25])
        h.pt3dadd(-57.978,-41.481,-28.52,0.814, sec = self.basal[25])
        h.pt3dadd(-58.529,-45.965,-29.761,0.812, sec = self.basal[25])
        h.pt3dadd(-58.344,-50.639,-30.78,0.812, sec = self.basal[25])
        h.pt3dadd(-57.064,-53.559,-31.08,0.724, sec = self.basal[25])
        h.pt3dadd(-57.569,-56.735,-32.163,0.716, sec = self.basal[25])
        h.pt3dadd(-57.314,-61.817,-33.036,0.706, sec = self.basal[25])
        h.pt3dadd(-57.471,-66.283,-34.835,0.688, sec = self.basal[25])
        h.pt3dadd(-56.991,-69.038,-35.295,0.738, sec = self.basal[25])
        h.pt3dadd(-56.881,-73.86,-35.515,0.764, sec = self.basal[25])
        h.pt3dadd(-57.276,-78.837,-35.24,0.788, sec = self.basal[25])
        h.pt3dadd(-57.596,-82.717,-35.24,0.762, sec = self.basal[25])
        h.pt3dadd(-58.556,-85.317,-36.2,0.778, sec = self.basal[25])
        h.pt3dadd(-58.236,-89.847,-36.22,0.744, sec = self.basal[25])
        h.pt3dadd(-57.916,-93.087,-37.12,0.788, sec = self.basal[25])
        h.pt3dadd(-57.156,-97.827,-37.42,0.782, sec = self.basal[25])
        h.pt3dadd(-56.836,-102.037,-38.7,0.686, sec = self.basal[25])
        h.pt3dadd(-55.556,-105.927,-40.46,0.726, sec = self.basal[25])
        h.pt3dadd(-52.676,-109.487,-40.46,0.784, sec = self.basal[25])
        h.pt3dadd(-50.436,-113.057,-42.02,0.61, sec = self.basal[25])
        h.pt3dadd(-48.196,-116.297,-43.04,0.544, sec = self.basal[25])
        h.pt3dadd(-45.316,-118.887,-44.18,0.44, sec = self.basal[25])
        h.pt3dadd(-42.766,-121.157,-40.48,0.506, sec = self.basal[25])
        h.pt3dadd(-40.846,-124.397,-40.48,0.46, sec = self.basal[25])
        h.pt3dadd(-38.286,-125.367,-40.48,0.478, sec = self.basal[25])
        h.pt3dadd(-36.686,-128.927,-37.24,0.5, sec = self.basal[25])
        h.pt3dadd(-33.806,-131.517,-37.24,0.41, sec = self.basal[25])
        h.pt3dadd(-33.166,-135.407,-37.24,0.476, sec = self.basal[25])
        h.pt3dadd(-30.286,-137.997,-36.24,0.32, sec = self.basal[25])
        h.pt3dadd(-29.656,-141.887,-36.24,0.32, sec = self.basal[25])

        self.basal[26].connect(self.soma[0])
        h.pt3dclear(sec = self.basal[26])
        h.pt3dadd(-53.42,3.52,-5.96,2.5, sec = self.basal[26])
        h.pt3dadd(-60.3,3.99,0.28,1.28, sec = self.basal[26])
        h.pt3dadd(-64.028,3.787,1.455,1.28, sec = self.basal[26])
        h.pt3dadd(-68.616,2.577,1.405,1.28, sec = self.basal[26])
        h.pt3dadd(-72.55,1.133,1.864,1.28, sec = self.basal[26])
        h.pt3dadd(-77.03,0.483,3.784,1.28, sec = self.basal[26])

        self.basal[27].connect(self.basal[26])
        h.pt3dclear(sec = self.basal[27])
        h.pt3dadd(-77.03,0.483,3.784,1.28, sec = self.basal[27])
        h.pt3dadd(-80.68,2.633,0.564,0.96, sec = self.basal[27])
        h.pt3dadd(-84.2,3.613,-0.576,0.96, sec = self.basal[27])
        h.pt3dadd(-88.771,4.452,-1.634,0.96, sec = self.basal[27])
        h.pt3dadd(-93.902,6.048,-2.616,0.96, sec = self.basal[27])
        h.pt3dadd(-96.462,6.688,-4.516,0.96, sec = self.basal[27])
        h.pt3dadd(-100.622,5.718,-5.996,0.96, sec = self.basal[27])
        h.pt3dadd(-102.852,5.718,-7.876,0.96, sec = self.basal[27])

        self.basal[28].connect(self.basal[27])
        h.pt3dclear(sec = self.basal[28])
        h.pt3dadd(-102.852,5.718,-7.876,0.96, sec = self.basal[28])
        h.pt3dadd(-102.852,3.128,-17.756,0.64, sec = self.basal[28])
        h.pt3dadd(-101.262,2.478,-21.296,0.64, sec = self.basal[28])
        h.pt3dadd(-100.622,-1.082,-24.456,0.64, sec = self.basal[28])
        h.pt3dadd(-101.892,-1.732,-27.696,0.64, sec = self.basal[28])
        h.pt3dadd(-103.172,-2.702,-35.536,0.64, sec = self.basal[28])
        h.pt3dadd(-105.092,-3.032,-41.596,0.64, sec = self.basal[28])
        h.pt3dadd(-105.412,-2.052,-46.196,0.64, sec = self.basal[28])
        h.pt3dadd(-107.012,-1.412,-47.816,0.64, sec = self.basal[28])
        h.pt3dadd(-108.932,-1.412,-50.276,0.64, sec = self.basal[28])
        h.pt3dadd(-110.212,0.538,-52.336,0.496, sec = self.basal[28])
        h.pt3dadd(-110.212,1.508,-56.156,0.476, sec = self.basal[28])

        self.basal[29].connect(self.basal[27])
        h.pt3dclear(sec = self.basal[29])
        h.pt3dadd(-102.852,5.718,-7.876,0.96, sec = self.basal[29])
        h.pt3dadd(-104.452,5.398,-7.876,0.96, sec = self.basal[29])
        h.pt3dadd(-108.932,5.718,-9.356,0.804, sec = self.basal[29])

        self.basal[30].connect(self.basal[29])
        h.pt3dclear(sec = self.basal[30])
        h.pt3dadd(-108.932,5.718,-9.356,0.804, sec = self.basal[30])
        h.pt3dadd(-113.092,4.428,-12.676,0.64, sec = self.basal[30])
        h.pt3dadd(-115.332,3.128,-12.676,0.782, sec = self.basal[30])
        h.pt3dadd(-118.842,3.128,-14.996,0.738, sec = self.basal[30])
        h.pt3dadd(-121.402,2.158,-17.416,0.73, sec = self.basal[30])
        h.pt3dadd(-124.282,1.188,-17.416,0.64, sec = self.basal[30])

        self.basal[31].connect(self.basal[30])
        h.pt3dclear(sec = self.basal[31])
        h.pt3dadd(-124.282,1.188,-17.416,0.64, sec = self.basal[31])
        h.pt3dadd(-127.162,0.858,-20.256,0.64, sec = self.basal[31])
        h.pt3dadd(-129.082,0.858,-20.256,0.64, sec = self.basal[31])
        h.pt3dadd(-131.632,-1.732,-22.016,0.64, sec = self.basal[31])
        h.pt3dadd(-134.192,-3.352,-24.736,0.64, sec = self.basal[31])
        h.pt3dadd(-138.352,-4.322,-29.736,0.64, sec = self.basal[31])
        h.pt3dadd(-140.592,-5.622,-32.256,0.64, sec = self.basal[31])
        h.pt3dadd(-143.472,-6.912,-32.256,0.64, sec = self.basal[31])
        h.pt3dadd(-146.342,-6.912,-35.356,0.64, sec = self.basal[31])
        h.pt3dadd(-149.222,-7.562,-37.116,0.64, sec = self.basal[31])
        h.pt3dadd(-152.102,-7.562,-37.936,0.64, sec = self.basal[31])
        h.pt3dadd(-154.022,-7.562,-37.916,0.64, sec = self.basal[31])
        h.pt3dadd(-157.222,-8.212,-39.196,0.64, sec = self.basal[31])
        h.pt3dadd(-159.782,-10.152,-39.636,0.64, sec = self.basal[31])
        h.pt3dadd(-162.332,-11.452,-43.116,0.64, sec = self.basal[31])
        h.pt3dadd(-165.852,-13.392,-44.816,0.516, sec = self.basal[31])
        h.pt3dadd(-168.092,-14.042,-47.096,0.486, sec = self.basal[31])

        self.basal[32].connect(self.basal[30])
        h.pt3dclear(sec = self.basal[32])
        h.pt3dadd(-124.282,1.188,-17.416,0.64, sec = self.basal[32])
        h.pt3dadd(-126.522,-2.052,-19.176,0.58, sec = self.basal[32])
        h.pt3dadd(-130.042,-4.972,-19.176,0.588, sec = self.basal[32])
        h.pt3dadd(-133.872,-5.942,-17.176,0.622, sec = self.basal[32])
        h.pt3dadd(-137.072,-8.212,-17.176,0.664, sec = self.basal[32])
        h.pt3dadd(-139.312,-9.832,-17.176,0.656, sec = self.basal[32])
        h.pt3dadd(-142.512,-12.422,-17.596,0.618, sec = self.basal[32])
        h.pt3dadd(-146.342,-12.752,-16.076,0.648, sec = self.basal[32])
        h.pt3dadd(-149.862,-13.072,-17.236,0.514, sec = self.basal[32])
        h.pt3dadd(-153.062,-12.752,-18.816,0.612, sec = self.basal[32])
        h.pt3dadd(-155.942,-12.422,-20.536,0.498, sec = self.basal[32])
        h.pt3dadd(-159.142,-11.772,-23.916,0.404, sec = self.basal[32])

        self.basal[33].connect(self.basal[29])
        h.pt3dclear(sec = self.basal[33])
        h.pt3dadd(-108.932,5.718,-9.356,0.804, sec = self.basal[33])
        h.pt3dadd(-114.692,7.338,-3.716,0.72, sec = self.basal[33])
        h.pt3dadd(-119.482,8.638,1.824,0.758, sec = self.basal[33])
        h.pt3dadd(-122.362,9.288,5.544,0.658, sec = self.basal[33])
        h.pt3dadd(-125.882,10.578,7.024,0.676, sec = self.basal[33])
        h.pt3dadd(-131.002,10.908,9.624,0.598, sec = self.basal[33])
        h.pt3dadd(-133.552,13.498,10.304,0.652, sec = self.basal[33])
        h.pt3dadd(-136.752,14.788,11.724,0.546, sec = self.basal[33])
        h.pt3dadd(-138.992,16.088,13.144,0.614, sec = self.basal[33])
        h.pt3dadd(-144.112,18.358,14.244,0.476, sec = self.basal[33])

        self.basal[34].connect(self.basal[26])
        h.pt3dclear(sec = self.basal[34])
        h.pt3dadd(-77.03,0.483,3.784,1.28, sec = self.basal[34])
        h.pt3dadd(-80.23,-0.487,1.264,0.788, sec = self.basal[34])
        h.pt3dadd(-82.47,-0.487,1.084,0.852, sec = self.basal[34])
        h.pt3dadd(-85.35,-2.107,0.664,0.75, sec = self.basal[34])
        h.pt3dadd(-88.084,-4.512,0.566,0.848, sec = self.basal[34])
        h.pt3dadd(-90.408,-7.229,0.826,0.952, sec = self.basal[34])
        h.pt3dadd(-93.59,-9.125,0.336,0.918, sec = self.basal[34])
        h.pt3dadd(-96.47,-9.445,-0.304,0.732, sec = self.basal[34])
        h.pt3dadd(-98.07,-11.395,-1.384,0.852, sec = self.basal[34])
        h.pt3dadd(-99.35,-13.985,-1.924,0.806, sec = self.basal[34])
        h.pt3dadd(-101.59,-16.895,-2.324,0.834, sec = self.basal[34])
        h.pt3dadd(-104.47,-20.135,-3.244,0.872, sec = self.basal[34])
        h.pt3dadd(-106.502,-23.151,-3.947,0.784, sec = self.basal[34])
        h.pt3dadd(-108.055,-26.209,-4.515,0.798, sec = self.basal[34])
        h.pt3dadd(-110.728,-29.518,-5.631,0.798, sec = self.basal[34])
        h.pt3dadd(-113.278,-32.758,-9.111,0.756, sec = self.basal[34])
        h.pt3dadd(-116.798,-35.348,-10.931,0.776, sec = self.basal[34])
        h.pt3dadd(-119.038,-37.288,-14.551,0.786, sec = self.basal[34])
        h.pt3dadd(-121.278,-39.558,-17.851,0.732, sec = self.basal[34])
        h.pt3dadd(-124.798,-42.148,-20.151,0.788, sec = self.basal[34])
        h.pt3dadd(-127.15,-46.524,-19.989,0.748, sec = self.basal[34])
        h.pt3dadd(-130.234,-50.645,-19.025,0.712, sec = self.basal[34])
        h.pt3dadd(-132.082,-54.729,-18.852,0.64, sec = self.basal[34])
        h.pt3dadd(-134.952,-57.639,-18.852,0.64, sec = self.basal[34])
        h.pt3dadd(-137.192,-60.229,-22.812,0.64, sec = self.basal[34])
        h.pt3dadd(-140.072,-62.499,-24.332,0.64, sec = self.basal[34])
        h.pt3dadd(-143.272,-64.449,-23.972,0.64, sec = self.basal[34])
        h.pt3dadd(-145.192,-66.709,-23.972,0.64, sec = self.basal[34])
        h.pt3dadd(-147.752,-69.309,-26.752,0.64, sec = self.basal[34])
        h.pt3dadd(-149.982,-72.219,-25.852,0.64, sec = self.basal[34])
        h.pt3dadd(-150.302,-77.079,-26.312,0.64, sec = self.basal[34])
        h.pt3dadd(-152.222,-79.999,-27.112,0.64, sec = self.basal[34])
        h.pt3dadd(-153.182,-83.889,-27.772,0.64, sec = self.basal[34])
        h.pt3dadd(-156.062,-87.119,-28.132,0.64, sec = self.basal[34])
        h.pt3dadd(-157.342,-91.009,-28.052,0.64, sec = self.basal[34])
        h.pt3dadd(-158.822,-95.029,-26.292,0.64, sec = self.basal[34])
        h.pt3dadd(-160.732,-99.569,-26.272,0.64, sec = self.basal[34])
        h.pt3dadd(-162.012,-102.479,-25.372,0.64, sec = self.basal[34])
        h.pt3dadd(-164.572,-106.049,-24.672,0.32, sec = self.basal[34])
        h.pt3dadd(-167.132,-110.579,-24.672,0.32, sec = self.basal[34])
        h.pt3dadd(-168.732,-116.409,-26.352,0.32, sec = self.basal[34])

        self.basal[35].connect(self.soma[0])
        h.pt3dclear(sec = self.basal[35])
        h.pt3dadd(-53.42,3.52,-5.96,2.5, sec = self.basal[35])
        h.pt3dadd(-60.27,4.33,-11.16,2.346, sec = self.basal[35])
        h.pt3dadd(-63.46,5.3,-18.84,1.606, sec = self.basal[35])
        h.pt3dadd(-65.7,6.92,-21.7,1.498, sec = self.basal[35])
        h.pt3dadd(-68.26,7.57,-25.3,1.642, sec = self.basal[35])
        h.pt3dadd(-69.86,9.19,-27.7,1.58, sec = self.basal[35])
        h.pt3dadd(-71.7,10.878,-31.447,1.452, sec = self.basal[35])
        h.pt3dadd(-73.919,12.85,-34.624,1.014, sec = self.basal[35])
        h.pt3dadd(-75.519,14.47,-35.724,1.004, sec = self.basal[35])
        h.pt3dadd(-76.799,14.79,-38.744,0.968, sec = self.basal[35])
        h.pt3dadd(-76.799,16.41,-41.704,0.832, sec = self.basal[35])
        h.pt3dadd(-77.759,18.68,-44.324,0.862, sec = self.basal[35])
        h.pt3dadd(-77.119,19.65,-46.684,0.832, sec = self.basal[35])
        h.pt3dadd(-78.079,23.21,-47.684,0.946, sec = self.basal[35])
        h.pt3dadd(-79.989,23.86,-49.304,0.854, sec = self.basal[35])
        h.pt3dadd(-80.629,25.16,-50.144,0.878, sec = self.basal[35])
        h.pt3dadd(-81.269,26.78,-52.924,0.776, sec = self.basal[35])
        h.pt3dadd(-82.229,27.75,-56.024,0.642, sec = self.basal[35])
        h.pt3dadd(-83.509,30.67,-57.384,0.738, sec = self.basal[35])
        h.pt3dadd(-86.389,31.96,-59.124,0.738, sec = self.basal[35])
        h.pt3dadd(-87.669,33.26,-63.364,0.638, sec = self.basal[35])
        h.pt3dadd(-88.309,35.53,-63.364,0.69, sec = self.basal[35])
        h.pt3dadd(-89.589,35.85,-67.304,0.686, sec = self.basal[35])
        h.pt3dadd(-90.229,36.82,-69.564,0.598, sec = self.basal[35])
        h.pt3dadd(-90.869,36.17,-72.364,0.766, sec = self.basal[35])
        h.pt3dadd(-90.549,35.53,-75.464,0.53, sec = self.basal[35])

        self.apical[0].connect(self.soma[3])
        h.pt3dclear(sec = self.apical[0])
        h.pt3dadd(-53.1,14.22,-5.96,5.76, sec = self.apical[0])
        h.pt3dadd(-53.42,16.81,-6.9,2.88, sec = self.apical[0])
        h.pt3dadd(-53.23,19.23,-8.22,2.88, sec = self.apical[0])
        h.pt3dadd(-52.27,27.01,-6.94,2.88, sec = self.apical[0])
        h.pt3dadd(-51.95,34.13,-7.32,2.88, sec = self.apical[0])
        h.pt3dadd(-49.71,42.56,-7.84,2.88, sec = self.apical[0])
        h.pt3dadd(-48.11,43.21,-8.96,2.56, sec = self.apical[0])

        self.apical[1].connect(self.apical[0])
        h.pt3dclear(sec = self.apical[1])
        h.pt3dadd(-48.11,43.21,-8.96,2.56, sec = self.apical[1])
        h.pt3dadd(-50.67,45.47,-6.74,1.802, sec = self.apical[1])
        h.pt3dadd(-50.99,48.39,-4.96,1.312, sec = self.apical[1])
        h.pt3dadd(-53.55,49.68,-3.46,1.248, sec = self.apical[1])
        h.pt3dadd(-54.83,51.3,-2.1,1.016, sec = self.apical[1])
        h.pt3dadd(-56.11,51.95,0.58,1.17, sec = self.apical[1])
        h.pt3dadd(-57.39,51.63,0.94,1.09, sec = self.apical[1])
        h.pt3dadd(-58.99,51.95,2.1,0.938, sec = self.apical[1])
        h.pt3dadd(-60.27,51.95,3.86,1.008, sec = self.apical[1])
        h.pt3dadd(-61.55,52.6,5.76,1, sec = self.apical[1])
        h.pt3dadd(-63.14,53.57,6.58,0.988, sec = self.apical[1])
        h.pt3dadd(-65.56,55.34,7.98,0.984, sec = self.apical[1])
        h.pt3dadd(-66.2,55.66,8.68,1.012, sec = self.apical[1])
        h.pt3dadd(-67.48,58.58,8.84,0.966, sec = self.apical[1])
        h.pt3dadd(-70.04,57.93,9.28,0.928, sec = self.apical[1])
        h.pt3dadd(-71,59.55,10.1,0.964, sec = self.apical[1])
        h.pt3dadd(-72.28,60.2,10.88,0.926, sec = self.apical[1])
        h.pt3dadd(-73.56,60.2,12.08,0.83, sec = self.apical[1])
        h.pt3dadd(-75.48,60.52,12.46,1.002, sec = self.apical[1])
        h.pt3dadd(-75.8,62.14,12.92,0.906, sec = self.apical[1])
        h.pt3dadd(-77.4,63.12,13.64,0.976, sec = self.apical[1])
        h.pt3dadd(-79,64.09,13.74,0.858, sec = self.apical[1])
        h.pt3dadd(-80.59,65.71,14.02,0.836, sec = self.apical[1])
        h.pt3dadd(-82.51,65.71,14.32,0.836, sec = self.apical[1])
        h.pt3dadd(-84.11,65.38,15.14,0.854, sec = self.apical[1])
        h.pt3dadd(-84.43,64.74,15.94,0.812, sec = self.apical[1])
        h.pt3dadd(-87.31,64.09,16.88,0.91, sec = self.apical[1])
        h.pt3dadd(-88.27,62.79,17.58,0.892, sec = self.apical[1])
        h.pt3dadd(-89.23,62.14,17.68,0.856, sec = self.apical[1])
        h.pt3dadd(-91.79,62.14,16.4,0.9, sec = self.apical[1])
        h.pt3dadd(-92.75,63.44,16.08,0.828, sec = self.apical[1])
        h.pt3dadd(-94.35,63.12,17.6,0.916, sec = self.apical[1])
        h.pt3dadd(-96.26,63.44,17.98,0.89, sec = self.apical[1])
        h.pt3dadd(-98.18,64.74,20.16,0.918, sec = self.apical[1])
        h.pt3dadd(-101.06,64.41,20.58,0.876, sec = self.apical[1])
        h.pt3dadd(-102.34,65.71,20.96,0.888, sec = self.apical[1])
        h.pt3dadd(-103.94,66.36,21.9,0.904, sec = self.apical[1])
        h.pt3dadd(-106.18,67,23,0.848, sec = self.apical[1])
        h.pt3dadd(-108.1,67,23.06,0.806, sec = self.apical[1])
        h.pt3dadd(-109.7,68.95,23.78,0.682, sec = self.apical[1])
        h.pt3dadd(-111.29,70.24,23.78,0.596, sec = self.apical[1])
        h.pt3dadd(-113.21,71.21,24.38,0.646, sec = self.apical[1])
        h.pt3dadd(-117.05,72.83,23.76,0.688, sec = self.apical[1])
        h.pt3dadd(-121.21,75.75,24.22,0.53, sec = self.apical[1])

        self.apical[2].connect(self.apical[0])
        h.pt3dclear(sec = self.apical[2])
        h.pt3dadd(-48.11,43.21,-8.96,2.56, sec = self.apical[2])
        h.pt3dadd(-47.66,48.21,-11.68,1.92, sec = self.apical[2])
        h.pt3dadd(-46.38,52.75,-13.22,1.92, sec = self.apical[2])
        h.pt3dadd(-45.1,56.96,-15.66,1.92, sec = self.apical[2])
        h.pt3dadd(-44.14,62.14,-17.12,1.92, sec = self.apical[2])
        h.pt3dadd(-42.54,67.33,-18.72,1.92, sec = self.apical[2])
        h.pt3dadd(-39.98,72.19,-17.06,1.92, sec = self.apical[2])
        h.pt3dadd(-38.38,76.72,-16.44,1.92, sec = self.apical[2])

        self.apical[3].connect(self.apical[2])
        h.pt3dclear(sec = self.apical[3])
        h.pt3dadd(-38.38,76.72,-16.44,1.92, sec = self.apical[3])
        h.pt3dadd(-36.63,85.29,-18.76,1.6, sec = self.apical[3])
        h.pt3dadd(-32.8,91.45,-21.02,1.6, sec = self.apical[3])
        h.pt3dadd(-30.24,98.25,-20.72,1.6, sec = self.apical[3])
        h.pt3dadd(-26.08,102.79,-20.76,1.6, sec = self.apical[3])
        h.pt3dadd(-24.16,108.94,-22.28,1.6, sec = self.apical[3])
        h.pt3dadd(-22.24,116.4,-25.64,1.6, sec = self.apical[3])
        h.pt3dadd(-20.81,122.8,-27.14,1.6, sec = self.apical[3])

        self.apical[4].connect(self.apical[3])
        h.pt3dclear(sec = self.apical[4])
        h.pt3dadd(-20.81,122.8,-27.14,1.6, sec = self.apical[4])
        h.pt3dadd(-20.32,125.47,-27.14,1.6, sec = self.apical[4])
        h.pt3dadd(-17.01,132.75,-29.88,1.6, sec = self.apical[4])
        h.pt3dadd(-16.83,133.99,-29.88,1.6, sec = self.apical[4])

        self.apical[5].connect(self.apical[4])
        h.pt3dclear(sec = self.apical[5])
        h.pt3dadd(-16.83,133.99,-29.88,1.6, sec = self.apical[5])
        h.pt3dadd(-16.01,135.76,-29.88,1.298, sec = self.apical[5])

        self.apical[6].connect(self.apical[5])
        h.pt3dclear(sec = self.apical[6])
        h.pt3dadd(-16.01,135.76,-29.88,1.298, sec = self.apical[6])
        h.pt3dadd(-13.81,139.88,-30.16,1.6, sec = self.apical[6])
        h.pt3dadd(-13.17,146.68,-30.3,1.6, sec = self.apical[6])
        h.pt3dadd(-9.65,152.83,-30.58,1.6, sec = self.apical[6])
        h.pt3dadd(-5.18,158.34,-32.16,1.6, sec = self.apical[6])
        h.pt3dadd(-2.94,164.5,-33.28,1.6, sec = self.apical[6])
        h.pt3dadd(1.22,169.36,-34.46,1.6, sec = self.apical[6])
        h.pt3dadd(3.46,172.27,-34.8,1.6, sec = self.apical[6])

        self.apical[7].connect(self.apical[6])
        h.pt3dclear(sec = self.apical[7])
        h.pt3dadd(3.46,172.27,-34.8,1.6, sec = self.apical[7])
        h.pt3dadd(7.81,176,-35.22,1.6, sec = self.apical[7])
        h.pt3dadd(11.33,182.16,-35.24,1.6, sec = self.apical[7])
        h.pt3dadd(14.2,186.05,-35.94,1.6, sec = self.apical[7])
        h.pt3dadd(17.87,190.39,-37.4,1.6, sec = self.apical[7])
        h.pt3dadd(19.79,191.69,-40,1.6, sec = self.apical[7])
        h.pt3dadd(21.39,193.31,-40.1,1.6, sec = self.apical[7])

        self.apical[8].connect(self.apical[7])
        h.pt3dclear(sec = self.apical[8])
        h.pt3dadd(21.39,193.31,-40.1,1.6, sec = self.apical[8])
        h.pt3dadd(22.02,198.53,-41.22,1.6, sec = self.apical[8])
        h.pt3dadd(23.62,204.03,-42.74,1.6, sec = self.apical[8])
        h.pt3dadd(25.54,211.49,-44.76,1.6, sec = self.apical[8])
        h.pt3dadd(29.06,218.29,-46.28,1.6, sec = self.apical[8])
        h.pt3dadd(32.9,223.8,-47.98,1.6, sec = self.apical[8])
        h.pt3dadd(34.81,233.84,-49.14,1.6, sec = self.apical[8])
        h.pt3dadd(37.37,241.29,-49.14,1.6, sec = self.apical[8])
        h.pt3dadd(42.81,249.39,-47.98,1.6, sec = self.apical[8])
        h.pt3dadd(45.69,258.14,-48.56,1.6, sec = self.apical[8])
        h.pt3dadd(47.29,265.91,-47.18,1.6, sec = self.apical[8])
        h.pt3dadd(47.93,270.45,-47.18,1.6, sec = self.apical[8])
        h.pt3dadd(52.08,276.28,-47.18,1.6, sec = self.apical[8])
        h.pt3dadd(51.44,280.49,-47.18,1.6, sec = self.apical[8])
        h.pt3dadd(53.36,288.27,-46.66,1.6, sec = self.apical[8])
        h.pt3dadd(56.24,294.75,-46.66,1.6, sec = self.apical[8])
        h.pt3dadd(57.67,300.75,-46.66,1.6, sec = self.apical[8])
        h.pt3dadd(60.55,304.32,-46.66,1.6, sec = self.apical[8])
        h.pt3dadd(60.55,309.5,-46.66,1.6, sec = self.apical[8])
        h.pt3dadd(61.19,315.65,-48.6,1.6, sec = self.apical[8])
        h.pt3dadd(62.47,320.84,-48.62,1.6, sec = self.apical[8])
        h.pt3dadd(65.03,327.64,-50.46,1.6, sec = self.apical[8])
        h.pt3dadd(66.31,333.47,-51.56,1.6, sec = self.apical[8])
        h.pt3dadd(66.31,339.31,-48.78,1.6, sec = self.apical[8])
        h.pt3dadd(68.55,344.16,-53.58,1.6, sec = self.apical[8])

        self.apical[9].connect(self.apical[8])
        h.pt3dclear(sec = self.apical[9])
        h.pt3dadd(68.55,344.16,-53.58,1.6, sec = self.apical[9])
        h.pt3dadd(71.25,348.21,-48.96,1.6, sec = self.apical[9])
        h.pt3dadd(73.49,352.42,-52.12,1.6, sec = self.apical[9])
        h.pt3dadd(77.65,356.63,-49.48,1.6, sec = self.apical[9])
        h.pt3dadd(78.93,363.43,-46.46,1.6, sec = self.apical[9])
        h.pt3dadd(82.12,370.89,-45.56,1.6, sec = self.apical[9])
        h.pt3dadd(85.64,377.04,-44.4,1.6, sec = self.apical[9])
        h.pt3dadd(88.52,383.85,-42.82,1.6, sec = self.apical[9])

        self.apical[10].connect(self.apical[9])
        h.pt3dclear(sec = self.apical[10])
        h.pt3dadd(88.52,383.85,-42.82,1.6, sec = self.apical[10])
        h.pt3dadd(91.89,385.64,-39.6,1.28, sec = self.apical[10])
        h.pt3dadd(94.45,388.56,-39.28,1.28, sec = self.apical[10])
        h.pt3dadd(98.29,391.47,-39.28,1.28, sec = self.apical[10])
        h.pt3dadd(101.49,393.74,-37.06,1.28, sec = self.apical[10])
        h.pt3dadd(104.68,397.3,-37.06,1.28, sec = self.apical[10])

        self.apical[11].connect(self.apical[10])
        h.pt3dclear(sec = self.apical[11])
        h.pt3dadd(104.68,397.3,-37.06,1.28, sec = self.apical[11])
        h.pt3dadd(107.35,400.34,-41.9,0.96, sec = self.apical[11])
        h.pt3dadd(109.91,404.22,-42.88,0.96, sec = self.apical[11])
        h.pt3dadd(112.47,406.49,-44.42,0.96, sec = self.apical[11])
        h.pt3dadd(114.39,410.06,-46.56,0.96, sec = self.apical[11])
        h.pt3dadd(115.67,413.29,-47.58,0.96, sec = self.apical[11])
        h.pt3dadd(120.46,415.24,-49.38,0.96, sec = self.apical[11])
        h.pt3dadd(122.7,417.51,-50.74,0.96, sec = self.apical[11])
        h.pt3dadd(126.54,417.83,-52.32,0.96, sec = self.apical[11])
        h.pt3dadd(130.06,419.77,-54.26,0.96, sec = self.apical[11])
        h.pt3dadd(131.98,422.37,-55.18,0.96, sec = self.apical[11])
        h.pt3dadd(135.17,423.34,-55.78,0.96, sec = self.apical[11])
        h.pt3dadd(139.01,423.34,-56.82,0.96, sec = self.apical[11])
        h.pt3dadd(143.49,423.66,-58.32,0.96, sec = self.apical[11])

        self.apical[12].connect(self.apical[11])
        h.pt3dclear(sec = self.apical[12])
        h.pt3dadd(143.49,423.66,-58.32,0.96, sec = self.apical[12])
        h.pt3dadd(148.96,422.65,-58.48,0.64, sec = self.apical[12])
        h.pt3dadd(150.24,421.68,-58.48,0.64, sec = self.apical[12])
        h.pt3dadd(152.8,422.97,-57.84,0.64, sec = self.apical[12])
        h.pt3dadd(155.04,419.41,-56.26,0.64, sec = self.apical[12])
        h.pt3dadd(158.24,419.41,-56.26,0.64, sec = self.apical[12])
        h.pt3dadd(160.15,420.38,-56.26,0.64, sec = self.apical[12])
        h.pt3dadd(163.03,420.38,-59.26,0.64, sec = self.apical[12])
        h.pt3dadd(168.47,422.33,-58.88,0.64, sec = self.apical[12])
        h.pt3dadd(173.59,423.3,-57.94,0.64, sec = self.apical[12])
        h.pt3dadd(175.5,425.24,-56.22,0.64, sec = self.apical[12])
        h.pt3dadd(176.78,428.48,-55.58,0.64, sec = self.apical[12])
        h.pt3dadd(178.7,428.16,-52.34,0.64, sec = self.apical[12])
        h.pt3dadd(180.94,428.48,-50.92,0.64, sec = self.apical[12])
        h.pt3dadd(182.86,429.78,-49.48,0.64, sec = self.apical[12])
        h.pt3dadd(184.78,428.81,-46.62,0.64, sec = self.apical[12])
        h.pt3dadd(186.38,428.48,-45.12,0.64, sec = self.apical[12])
        h.pt3dadd(189.25,428.16,-45.12,0.64, sec = self.apical[12])
        h.pt3dadd(191.81,428.81,-44.06,0.64, sec = self.apical[12])
        h.pt3dadd(193.73,428.16,-42.6,0.64, sec = self.apical[12])
        h.pt3dadd(195.97,430.1,-41.44,0.64, sec = self.apical[12])
        h.pt3dadd(197.25,432.37,-41.44,0.64, sec = self.apical[12])
        h.pt3dadd(202.37,433.02,-41.58,0.64, sec = self.apical[12])
        h.pt3dadd(205.24,432.04,-40.52,0.64, sec = self.apical[12])
        h.pt3dadd(207.48,434.31,-40.52,0.64, sec = self.apical[12])
        h.pt3dadd(210.04,434.96,-40.42,0.64, sec = self.apical[12])
        h.pt3dadd(212.92,435.28,-40.42,0.64, sec = self.apical[12])
        h.pt3dadd(214.84,434.64,-40.42,0.64, sec = self.apical[12])
        h.pt3dadd(218.67,436.26,-39.74,0.64, sec = self.apical[12])
        h.pt3dadd(221.23,437.88,-39.74,0.64, sec = self.apical[12])
        h.pt3dadd(224.75,437.88,-38.1,0.64, sec = self.apical[12])
        h.pt3dadd(226.35,439.82,-38.1,0.64, sec = self.apical[12])
        h.pt3dadd(229.87,439.82,-36.48,0.64, sec = self.apical[12])
        h.pt3dadd(232.75,440.79,-36.48,0.64, sec = self.apical[12])
        h.pt3dadd(234.98,444.68,-36.46,0.64, sec = self.apical[12])
        h.pt3dadd(237.86,446.3,-36.44,0.64, sec = self.apical[12])
        h.pt3dadd(240.42,447.27,-37.64,0.64, sec = self.apical[12])
        h.pt3dadd(244.9,447.27,-37.64,0.64, sec = self.apical[12])

        self.apical[13].connect(self.apical[12])
        h.pt3dclear(sec = self.apical[13])
        h.pt3dadd(244.9,447.27,-37.64,0.64, sec = self.apical[13])
        h.pt3dadd(246.5,449.86,-37.8,0.416, sec = self.apical[13])
        h.pt3dadd(247.78,449.54,-37.8,0.398, sec = self.apical[13])
        h.pt3dadd(250.01,452.78,-36.6,0.398, sec = self.apical[13])
        h.pt3dadd(251.93,453.43,-36.6,0.466, sec = self.apical[13])
        h.pt3dadd(254.49,453.75,-35.44,0.438, sec = self.apical[13])
        h.pt3dadd(256.09,455.37,-35.44,0.474, sec = self.apical[13])
        h.pt3dadd(257.69,457.32,-35.44,0.462, sec = self.apical[13])
        h.pt3dadd(260.57,459.58,-35.9,0.42, sec = self.apical[13])
        h.pt3dadd(263.76,460.88,-35.9,0.454, sec = self.apical[13])
        h.pt3dadd(267.6,462.82,-36.98,0.408, sec = self.apical[13])
        h.pt3dadd(270.16,464.12,-36.98,0.392, sec = self.apical[13])
        h.pt3dadd(272.08,466.06,-36.98,0.3, sec = self.apical[13])
        h.pt3dadd(275.28,469.3,-38.32,0.32, sec = self.apical[13])
        h.pt3dadd(279.43,468.65,-38.32,0.32, sec = self.apical[13])
        h.pt3dadd(280.87,471.41,-38.32,0.32, sec = self.apical[13])
        h.pt3dadd(284.07,473.68,-38.34,0.32, sec = self.apical[13])

        self.apical[14].connect(self.apical[12])
        h.pt3dclear(sec = self.apical[14])
        h.pt3dadd(244.9,447.27,-37.64,0.64, sec = self.apical[14])
        h.pt3dadd(245.22,445.65,-36.28,0.64, sec = self.apical[14])
        h.pt3dadd(247.46,443.06,-35.38,0.32, sec = self.apical[14])

        self.apical[15].connect(self.apical[11])
        h.pt3dclear(sec = self.apical[15])
        h.pt3dadd(143.49,423.66,-58.32,0.96, sec = self.apical[15])
        h.pt3dadd(147.01,424.31,-58.18,0.96, sec = self.apical[15])
        h.pt3dadd(148.92,425.28,-66.42,0.96, sec = self.apical[15])
        h.pt3dadd(152.12,426.9,-68.1,0.96, sec = self.apical[15])
        h.pt3dadd(156.6,427.55,-70.46,0.96, sec = self.apical[15])
        h.pt3dadd(159.48,427.23,-70.46,0.64, sec = self.apical[15])
        h.pt3dadd(162.99,429.17,-72.92,0.64, sec = self.apical[15])
        h.pt3dadd(165.75,430.29,-74.74,0.64, sec = self.apical[15])
        h.pt3dadd(170.23,430.94,-76.1,0.64, sec = self.apical[15])
        h.pt3dadd(171.51,433.86,-76.78,0.64, sec = self.apical[15])
        h.pt3dadd(174.07,433.53,-79.04,0.64, sec = self.apical[15])
        h.pt3dadd(177.58,433.21,-79.38,0.64, sec = self.apical[15])
        h.pt3dadd(179.5,435.48,-80.7,0.64, sec = self.apical[15])
        h.pt3dadd(183.02,434.83,-77.78,0.64, sec = self.apical[15])
        h.pt3dadd(186.86,436.12,-79.18,0.64, sec = self.apical[15])
        h.pt3dadd(191.01,435.48,-80.6,0.64, sec = self.apical[15])
        h.pt3dadd(192.29,437.1,-81.22,0.64, sec = self.apical[15])
        h.pt3dadd(199.97,439.36,-81.22,0.64, sec = self.apical[15])
        h.pt3dadd(203.17,439.04,-81.22,0.64, sec = self.apical[15])
        h.pt3dadd(205.09,442.28,-81.22,0.64, sec = self.apical[15])
        h.pt3dadd(209.88,442.93,-83.32,0.64, sec = self.apical[15])
        h.pt3dadd(212.44,445.84,-86.08,0.64, sec = self.apical[15])
        h.pt3dadd(215.64,447.14,-86.08,0.64, sec = self.apical[15])
        h.pt3dadd(220.44,447.79,-86.82,0.64, sec = self.apical[15])
        h.pt3dadd(223.47,449.86,-87.22,0.64, sec = self.apical[15])
        h.pt3dadd(227.31,451.81,-88.58,0.64, sec = self.apical[15])
        h.pt3dadd(233.07,452.13,-92.02,0.64, sec = self.apical[15])
        h.pt3dadd(236.26,454.4,-96.56,0.64, sec = self.apical[15])
        h.pt3dadd(241.7,456.67,-97.96,0.64, sec = self.apical[15])
        h.pt3dadd(244.58,453.75,-99.44,0.64, sec = self.apical[15])
        h.pt3dadd(248.1,454.4,-101.44,0.64, sec = self.apical[15])
        h.pt3dadd(250.65,454.08,-101.72,0.64, sec = self.apical[15])
        h.pt3dadd(253.21,456.02,-102.74,0.64, sec = self.apical[15])
        h.pt3dadd(256.73,457.64,-104.56,0.64, sec = self.apical[15])
        h.pt3dadd(260.25,457.96,-106.3,0.64, sec = self.apical[15])

        self.apical[16].connect(self.apical[15])
        h.pt3dclear(sec = self.apical[16])
        h.pt3dadd(260.25,457.96,-106.3,0.64, sec = self.apical[16])
        h.pt3dadd(263.44,457.96,-105.78,0.32, sec = self.apical[16])
        h.pt3dadd(265.36,456.34,-105.78,0.32, sec = self.apical[16])
        h.pt3dadd(268.88,456.34,-107.48,0.32, sec = self.apical[16])
        h.pt3dadd(270.48,457.96,-107.48,0.32, sec = self.apical[16])

        self.apical[17].connect(self.apical[15])
        h.pt3dclear(sec = self.apical[17])
        h.pt3dadd(260.25,457.96,-106.3,0.64, sec = self.apical[17])
        h.pt3dadd(262.81,460.23,-106.98,0.32, sec = self.apical[17])
        h.pt3dadd(263.76,463.79,-107.16,0.32, sec = self.apical[17])

        self.apical[18].connect(self.apical[10])
        h.pt3dclear(sec = self.apical[18])
        h.pt3dadd(104.68,397.3,-37.06,1.28, sec = self.apical[18])
        h.pt3dadd(105.32,400.22,-38.4,0.64, sec = self.apical[18])
        h.pt3dadd(107.56,401.84,-35.9,0.64, sec = self.apical[18])
        h.pt3dadd(109.16,402.16,-36.12,0.64, sec = self.apical[18])
        h.pt3dadd(110.76,401.19,-34.58,0.64, sec = self.apical[18])
        h.pt3dadd(111.08,402.16,-25.2,0.64, sec = self.apical[18])
        h.pt3dadd(111.72,401.84,-22.76,0.64, sec = self.apical[18])
        h.pt3dadd(111.08,399.25,-19.64,0.64, sec = self.apical[18])
        h.pt3dadd(112.36,398.28,-19.64,0.64, sec = self.apical[18])
        h.pt3dadd(113.64,398.28,-16.34,0.64, sec = self.apical[18])
        h.pt3dadd(115.56,398.28,-13.06,0.64, sec = self.apical[18])
        h.pt3dadd(117.79,397.63,-13.06,0.64, sec = self.apical[18])
        h.pt3dadd(119.39,398.28,-13.06,0.64, sec = self.apical[18])
        h.pt3dadd(123.23,397.95,-11.84,0.64, sec = self.apical[18])
        h.pt3dadd(128.03,398.92,-10.86,0.64, sec = self.apical[18])
        h.pt3dadd(130.91,397.95,-9.38,0.64, sec = self.apical[18])
        h.pt3dadd(133.14,397.3,-8.26,0.64, sec = self.apical[18])
        h.pt3dadd(137.3,396.98,-8.26,0.64, sec = self.apical[18])
        h.pt3dadd(140.82,397.63,-8.9,0.64, sec = self.apical[18])
        h.pt3dadd(144.02,399.57,-8.92,0.64, sec = self.apical[18])
        h.pt3dadd(149.95,402.64,-7.54,0.64, sec = self.apical[18])
        h.pt3dadd(153.15,406.2,-5.06,0.64, sec = self.apical[18])
        h.pt3dadd(158.26,408.47,-3.24,0.64, sec = self.apical[18])
        h.pt3dadd(161.14,410.74,-1.44,0.64, sec = self.apical[18])
        h.pt3dadd(164.34,412.68,0,0.64, sec = self.apical[18])
        h.pt3dadd(166.26,413,0,0.64, sec = self.apical[18])
        h.pt3dadd(170.42,414.62,-2.72,0.64, sec = self.apical[18])
        h.pt3dadd(173.61,416.57,-4.68,0.64, sec = self.apical[18])
        h.pt3dadd(177.45,418.83,-5.66,0.684, sec = self.apical[18])
        h.pt3dadd(180.97,420.78,-6.1,0.68, sec = self.apical[18])
        h.pt3dadd(183.53,423.69,-6.68,0.562, sec = self.apical[18])
        h.pt3dadd(186.73,426.93,-8.42,0.622, sec = self.apical[18])
        h.pt3dadd(188.32,432.12,-10.04,0.61, sec = self.apical[18])
        h.pt3dadd(191.52,434.71,-11.16,0.56, sec = self.apical[18])
        h.pt3dadd(193.44,437.3,-12.04,0.51, sec = self.apical[18])
        h.pt3dadd(195.04,438.92,-13.06,0.494, sec = self.apical[18])
        h.pt3dadd(196.96,441.84,-14.02,0.496, sec = self.apical[18])
        h.pt3dadd(199.84,442.81,-15.36,0.508, sec = self.apical[18])
        h.pt3dadd(201.91,443.99,-15.36,0.504, sec = self.apical[18])
        h.pt3dadd(204.15,448.2,-15.94,0.512, sec = self.apical[18])
        h.pt3dadd(205.75,449.82,-16.46,0.474, sec = self.apical[18])
        h.pt3dadd(208.63,451.12,-16.82,0.444, sec = self.apical[18])

        self.apical[19].connect(self.apical[9])
        h.pt3dclear(sec = self.apical[19])
        h.pt3dadd(88.52,383.85,-42.82,1.6, sec = self.apical[19])
        h.pt3dadd(88.52,390,-42.74,1.28, sec = self.apical[19])
        h.pt3dadd(89.48,395.51,-40.16,1.28, sec = self.apical[19])
        h.pt3dadd(89.16,401.34,-39.28,1.28, sec = self.apical[19])
        h.pt3dadd(87.06,405.41,-37.12,0.96, sec = self.apical[19])
        h.pt3dadd(83.86,409.94,-36.58,0.96, sec = self.apical[19])
        h.pt3dadd(82.9,412.54,-36.58,0.96, sec = self.apical[19])
        h.pt3dadd(81.3,415.78,-35.34,0.96, sec = self.apical[19])
        h.pt3dadd(80.66,419.01,-35.34,0.96, sec = self.apical[19])
        h.pt3dadd(79.06,420.31,-35.34,0.96, sec = self.apical[19])
        h.pt3dadd(77.78,423.23,-35.14,0.96, sec = self.apical[19])
        h.pt3dadd(74.9,424.2,-35.14,0.96, sec = self.apical[19])
        h.pt3dadd(72.34,425.49,-34.46,0.96, sec = self.apical[19])
        h.pt3dadd(69.15,427.44,-33.3,0.96, sec = self.apical[19])
        h.pt3dadd(67.87,429.71,-32.8,0.96, sec = self.apical[19])
        h.pt3dadd(66.27,432.3,-32.8,0.64, sec = self.apical[19])
        h.pt3dadd(65.95,436.83,-33.96,0.64, sec = self.apical[19])
        h.pt3dadd(64.35,441.69,-33.96,0.628, sec = self.apical[19])
        h.pt3dadd(62.75,444.93,-34.88,0.544, sec = self.apical[19])
        h.pt3dadd(61.79,449.47,-34.9,0.62, sec = self.apical[19])
        h.pt3dadd(60.51,453.36,-34.92,0.56, sec = self.apical[19])
        h.pt3dadd(59.55,456.6,-36.32,0.598, sec = self.apical[19])
        h.pt3dadd(57.77,460.61,-36.32,0.566, sec = self.apical[19])
        h.pt3dadd(57.77,464.5,-37.16,0.576, sec = self.apical[19])
        h.pt3dadd(57.14,468.06,-37.16,0.67, sec = self.apical[19])
        h.pt3dadd(59.05,470.98,-37.16,0.594, sec = self.apical[19])
        h.pt3dadd(58.09,474.21,-36.2,0.586, sec = self.apical[19])
        h.pt3dadd(58.41,478.75,-36.2,0.49, sec = self.apical[19])

        self.apical[20].connect(self.apical[8])
        h.pt3dclear(sec = self.apical[20])
        h.pt3dadd(68.55,344.16,-53.58,1.6, sec = self.apical[20])
        h.pt3dadd(72.38,346.43,-56.46,1.28, sec = self.apical[20])
        h.pt3dadd(74.62,351.29,-57.9,1.28, sec = self.apical[20])
        h.pt3dadd(78.63,353.36,-57.9,1.28, sec = self.apical[20])
        h.pt3dadd(81.83,358.87,-60.8,1.28, sec = self.apical[20])
        h.pt3dadd(83.43,363.08,-63,1.28, sec = self.apical[20])

        self.apical[21].connect(self.apical[20])
        h.pt3dclear(sec = self.apical[21])
        h.pt3dadd(83.43,363.08,-63,1.28, sec = self.apical[21])
        h.pt3dadd(83.59,367.11,-59.64,1.28, sec = self.apical[21])

        self.apical[22].connect(self.apical[21])
        h.pt3dclear(sec = self.apical[22])
        h.pt3dadd(83.59,367.11,-59.64,1.28, sec = self.apical[22])
        h.pt3dadd(81.24,370.14,-65.34,0.96, sec = self.apical[22])
        h.pt3dadd(81.24,374.02,-65.34,0.96, sec = self.apical[22])
        h.pt3dadd(79.96,376.62,-65.34,0.96, sec = self.apical[22])
        h.pt3dadd(80.6,380.5,-65.34,0.96, sec = self.apical[22])
        h.pt3dadd(78.68,381.8,-65.34,0.96, sec = self.apical[22])
        h.pt3dadd(78.68,386.66,-63.98,0.96, sec = self.apical[22])
        h.pt3dadd(77.72,389.9,-63.76,0.96, sec = self.apical[22])
        h.pt3dadd(76.44,391.52,-63.62,0.96, sec = self.apical[22])
        h.pt3dadd(77.08,393.46,-63.42,0.96, sec = self.apical[22])
        h.pt3dadd(75.48,397.03,-63.2,0.96, sec = self.apical[22])
        h.pt3dadd(76.76,400.27,-64.32,0.96, sec = self.apical[22])
        h.pt3dadd(75.16,402.86,-67.32,0.96, sec = self.apical[22])
        h.pt3dadd(73.56,407.07,-69.66,0.96, sec = self.apical[22])
        h.pt3dadd(72.28,409.66,-69.68,0.96, sec = self.apical[22])
        h.pt3dadd(72.92,414.2,-73.54,0.96, sec = self.apical[22])
        h.pt3dadd(72.13,417.26,-72.22,0.64, sec = self.apical[22])
        h.pt3dadd(71.17,419.85,-73.74,0.64, sec = self.apical[22])
        h.pt3dadd(72.13,424.06,-74.58,0.64, sec = self.apical[22])
        h.pt3dadd(70.85,426.98,-75.7,0.64, sec = self.apical[22])
        h.pt3dadd(70.21,431.52,-75.86,0.64, sec = self.apical[22])
        h.pt3dadd(71.17,435.4,-77.02,0.64, sec = self.apical[22])
        h.pt3dadd(71.81,437.35,-77.02,0.64, sec = self.apical[22])
        h.pt3dadd(71.49,440.59,-76.18,0.64, sec = self.apical[22])
        h.pt3dadd(70.21,442.21,-76.18,0.64, sec = self.apical[22])
        h.pt3dadd(70.85,446.42,-76.18,0.64, sec = self.apical[22])
        h.pt3dadd(69.26,449.01,-76.18,0.64, sec = self.apical[22])
        h.pt3dadd(69.57,450.95,-76.18,0.64, sec = self.apical[22])
        h.pt3dadd(68.94,452.9,-76.18,0.64, sec = self.apical[22])
        h.pt3dadd(68.94,456.46,-77.78,0.64, sec = self.apical[22])
        h.pt3dadd(71.17,459.7,-75.78,0.64, sec = self.apical[22])
        h.pt3dadd(69.89,461,-75.78,0.64, sec = self.apical[22])
        h.pt3dadd(70.53,464.56,-75.94,0.64, sec = self.apical[22])
        h.pt3dadd(68.94,469.1,-77.6,0.64, sec = self.apical[22])
        h.pt3dadd(69.57,471.36,-76.64,0.64, sec = self.apical[22])
        h.pt3dadd(67.02,475.58,-76.64,0.64, sec = self.apical[22])
        h.pt3dadd(66.7,479.79,-79.16,0.64, sec = self.apical[22])

        self.apical[23].connect(self.apical[21])
        h.pt3dclear(sec = self.apical[23])
        h.pt3dadd(83.59,367.11,-59.64,1.28, sec = self.apical[23])
        h.pt3dadd(86.47,368.08,-61.36,1.28, sec = self.apical[23])
        h.pt3dadd(86.79,371.32,-68.28,0.96, sec = self.apical[23])
        h.pt3dadd(89.35,374.56,-70.64,0.96, sec = self.apical[23])
        h.pt3dadd(90.63,377.8,-72.32,0.96, sec = self.apical[23])
        h.pt3dadd(91.59,380.71,-72.32,0.96, sec = self.apical[23])
        h.pt3dadd(94.15,379.74,-75.24,0.96, sec = self.apical[23])
        h.pt3dadd(95.11,382.98,-77.2,0.96, sec = self.apical[23])
        h.pt3dadd(95.43,384.93,-79.46,0.96, sec = self.apical[23])
        h.pt3dadd(97.66,387.19,-80.8,0.96, sec = self.apical[23])
        h.pt3dadd(97.98,389.79,-80.82,0.96, sec = self.apical[23])
        h.pt3dadd(96.7,391.73,-82.6,0.96, sec = self.apical[23])
        h.pt3dadd(97.02,394.65,-83.8,0.96, sec = self.apical[23])
        h.pt3dadd(98.62,396.91,-85.56,0.96, sec = self.apical[23])
        h.pt3dadd(100.54,398.86,-86.38,0.96, sec = self.apical[23])
        h.pt3dadd(100.22,402.42,-88.56,0.96, sec = self.apical[23])
        h.pt3dadd(101.82,405.66,-90.3,0.96, sec = self.apical[23])
        h.pt3dadd(105.02,407.61,-92,0.96, sec = self.apical[23])
        h.pt3dadd(105.66,410.85,-93.42,0.96, sec = self.apical[23])
        h.pt3dadd(105.34,415.06,-95.12,0.96, sec = self.apical[23])
        h.pt3dadd(106.3,417.32,-98.04,0.96, sec = self.apical[23])
        h.pt3dadd(109.18,420.56,-100.26,0.96, sec = self.apical[23])
        h.pt3dadd(111.21,424.28,-101.6,0.96, sec = self.apical[23])
        h.pt3dadd(112.49,425.58,-107.86,0.96, sec = self.apical[23])
        h.pt3dadd(115.05,426.55,-108.1,0.96, sec = self.apical[23])
        h.pt3dadd(118.89,428.17,-109.04,0.96, sec = self.apical[23])
        h.pt3dadd(122.72,430.12,-109.9,0.96, sec = self.apical[23])
        h.pt3dadd(123.36,431.74,-112.58,0.96, sec = self.apical[23])
        h.pt3dadd(123.36,433.36,-112.58,0.96, sec = self.apical[23])

        self.apical[24].connect(self.apical[23])
        h.pt3dclear(sec = self.apical[24])
        h.pt3dadd(123.36,433.36,-112.58,0.96, sec = self.apical[24])
        h.pt3dadd(123.49,436.76,-112.54,0.96, sec = self.apical[24])
        h.pt3dadd(124.45,441.3,-114.12,0.96, sec = self.apical[24])
        h.pt3dadd(125.41,445.18,-114.12,0.96, sec = self.apical[24])
        h.pt3dadd(124.77,450.37,-116.14,0.96, sec = self.apical[24])

        self.apical[25].connect(self.apical[24])
        h.pt3dclear(sec = self.apical[25])
        h.pt3dadd(124.77,450.37,-116.14,0.96, sec = self.apical[25])
        h.pt3dadd(124.13,453.61,-120.42,0.64, sec = self.apical[25])
        h.pt3dadd(123.17,456.2,-126.76,0.64, sec = self.apical[25])
        h.pt3dadd(120.3,459.76,-126.76,0.64, sec = self.apical[25])
        h.pt3dadd(120.62,464.3,-130.66,0.64, sec = self.apical[25])
        h.pt3dadd(119.98,468.19,-130.66,0.64, sec = self.apical[25])
        h.pt3dadd(119.98,472.07,-132.56,0.64, sec = self.apical[25])

        self.apical[26].connect(self.apical[24])
        h.pt3dclear(sec = self.apical[26])
        h.pt3dadd(124.77,450.37,-116.14,0.96, sec = self.apical[26])
        h.pt3dadd(127.01,452.96,-116.8,0.59, sec = self.apical[26])
        h.pt3dadd(129.57,453.93,-116.8,0.566, sec = self.apical[26])
        h.pt3dadd(129.89,457.49,-115.7,0.556, sec = self.apical[26])
        h.pt3dadd(132.13,461.71,-113.84,0.512, sec = self.apical[26])
        h.pt3dadd(133.73,463.33,-113.84,0.556, sec = self.apical[26])
        h.pt3dadd(135.01,466.89,-112.42,0.532, sec = self.apical[26])
        h.pt3dadd(136.6,469.16,-112.42,0.488, sec = self.apical[26])
        h.pt3dadd(141.08,470.45,-113.32,0.484, sec = self.apical[26])
        h.pt3dadd(142.04,473.69,-114.36,0.556, sec = self.apical[26])
        h.pt3dadd(142.68,478.23,-113.42,0.578, sec = self.apical[26])
        h.pt3dadd(142.36,480.82,-113.42,0.556, sec = self.apical[26])

        self.apical[27].connect(self.apical[23])
        h.pt3dclear(sec = self.apical[27])
        h.pt3dadd(123.36,433.36,-112.58,0.96, sec = self.apical[27])
        h.pt3dadd(126.24,432.71,-114.12,0.96, sec = self.apical[27])
        h.pt3dadd(128.8,431.41,-119.44,0.924, sec = self.apical[27])
        h.pt3dadd(131.36,431.41,-122.22,0.836, sec = self.apical[27])
        h.pt3dadd(133.92,430.44,-122.22,0.888, sec = self.apical[27])
        h.pt3dadd(136.8,432.38,-122.22,0.896, sec = self.apical[27])
        h.pt3dadd(139.03,434,-124.58,0.912, sec = self.apical[27])
        h.pt3dadd(141.59,433.68,-125.36,0.874, sec = self.apical[27])
        h.pt3dadd(144.79,436.92,-127.06,0.942, sec = self.apical[27])
        h.pt3dadd(147.03,438.86,-128.48,0.988, sec = self.apical[27])
        h.pt3dadd(149.91,437.57,-129.5,0.952, sec = self.apical[27])
        h.pt3dadd(152.46,437.57,-131.1,0.86, sec = self.apical[27])
        h.pt3dadd(155.02,438.54,-132.7,0.904, sec = self.apical[27])
        h.pt3dadd(157.9,439.19,-135.54,1.024, sec = self.apical[27])
        h.pt3dadd(160.78,438.86,-137.22,0.904, sec = self.apical[27])

        self.apical[28].connect(self.apical[27])
        h.pt3dclear(sec = self.apical[28])
        h.pt3dadd(160.78,438.86,-137.22,0.904, sec = self.apical[28])
        h.pt3dadd(163.93,440.2,-132.86,0.882, sec = self.apical[28])
        h.pt3dadd(168.73,441.17,-133.2,0.7, sec = self.apical[28])
        h.pt3dadd(172.57,442.79,-133.96,0.602, sec = self.apical[28])
        h.pt3dadd(176.72,445.38,-135.34,0.574, sec = self.apical[28])
        h.pt3dadd(178.96,450.24,-136.86,0.572, sec = self.apical[28])
        h.pt3dadd(182.48,451.22,-138.06,0.538, sec = self.apical[28])
        h.pt3dadd(184.08,453.48,-138.9,0.486, sec = self.apical[28])
        h.pt3dadd(186.96,455.75,-141.74,0.506, sec = self.apical[28])
        h.pt3dadd(187.92,458.02,-142.56,0.422, sec = self.apical[28])
        h.pt3dadd(190.8,459.64,-145.68,0.494, sec = self.apical[28])
        h.pt3dadd(192.71,465.15,-145.7,0.446, sec = self.apical[28])
        h.pt3dadd(195.59,469.36,-144.22,0.524, sec = self.apical[28])
        h.pt3dadd(198.47,473.25,-145.4,0.554, sec = self.apical[28])
        h.pt3dadd(201.67,473.25,-146.88,0.526, sec = self.apical[28])
        h.pt3dadd(204.55,476.81,-146.66,0.456, sec = self.apical[28])
        h.pt3dadd(209.02,480.37,-146.66,0.554, sec = self.apical[28])

        self.apical[29].connect(self.apical[27])
        h.pt3dclear(sec = self.apical[29])
        h.pt3dadd(160.78,438.86,-137.22,0.904, sec = self.apical[29])
        h.pt3dadd(161.74,436.92,-143.52,1.008, sec = self.apical[29])
        h.pt3dadd(163.66,437.89,-144.8,0.844, sec = self.apical[29])
        h.pt3dadd(165.26,438.54,-146.64,0.74, sec = self.apical[29])
        h.pt3dadd(167.31,438.4,-149.76,0.668, sec = self.apical[29])
        h.pt3dadd(168.91,439.37,-149.76,0.678, sec = self.apical[29])
        h.pt3dadd(170.51,437.75,-151.02,0.67, sec = self.apical[29])
        h.pt3dadd(173.71,437.75,-154.66,0.702, sec = self.apical[29])
        h.pt3dadd(177.23,440.99,-157.46,0.748, sec = self.apical[29])
        h.pt3dadd(179.14,442.28,-158.62,0.756, sec = self.apical[29])
        h.pt3dadd(183.3,443.9,-159.3,0.782, sec = self.apical[29])
        h.pt3dadd(187.14,445.52,-160.8,0.638, sec = self.apical[29])
        h.pt3dadd(190.02,446.5,-156.26,0.684, sec = self.apical[29])
        h.pt3dadd(193.85,448.12,-160.22,0.678, sec = self.apical[29])
        h.pt3dadd(198.65,448.12,-163.18,0.732, sec = self.apical[29])
        h.pt3dadd(203.13,448.44,-162.66,0.552, sec = self.apical[29])
        h.pt3dadd(206.65,449.74,-166.04,0.592, sec = self.apical[29])
        h.pt3dadd(210.16,451.03,-171.54,0.632, sec = self.apical[29])
        h.pt3dadd(213.36,451.36,-168.86,0.662, sec = self.apical[29])
        h.pt3dadd(219.12,451.68,-173.52,0.586, sec = self.apical[29])
        h.pt3dadd(222.96,449.74,-176.2,0.566, sec = self.apical[29])
        h.pt3dadd(225.01,448.3,-180.86,0.564, sec = self.apical[29])
        h.pt3dadd(226.61,450.24,-181.74,0.602, sec = self.apical[29])
        h.pt3dadd(230.77,448.95,-185.26,0.438, sec = self.apical[29])
        h.pt3dadd(234.61,447.98,-189.36,0.374, sec = self.apical[29])

        self.apical[30].connect(self.apical[20])
        h.pt3dclear(sec = self.apical[30])
        h.pt3dadd(83.43,363.08,-63,1.28, sec = self.apical[30])
        h.pt3dadd(88.22,364.7,-61,0.904, sec = self.apical[30])
        h.pt3dadd(92.06,366.97,-61.54,0.94, sec = self.apical[30])
        h.pt3dadd(93.66,369.24,-62.22,0.958, sec = self.apical[30])
        h.pt3dadd(96.22,371.83,-63.18,0.878, sec = self.apical[30])
        h.pt3dadd(100.06,372.15,-67.12,0.84, sec = self.apical[30])
        h.pt3dadd(104.53,374.75,-70.74,0.902, sec = self.apical[30])
        h.pt3dadd(108.05,376.04,-73.28,0.812, sec = self.apical[30])
        h.pt3dadd(110.61,378.96,-73.28,0.952, sec = self.apical[30])
        h.pt3dadd(116.05,381.87,-73.28,0.872, sec = self.apical[30])
        h.pt3dadd(119.88,384.14,-74.08,0.886, sec = self.apical[30])
        h.pt3dadd(125.32,386.09,-75.64,0.834, sec = self.apical[30])
        h.pt3dadd(130.12,389.33,-78.5,0.704, sec = self.apical[30])
        h.pt3dadd(134.13,391.79,-78.58,0.724, sec = self.apical[30])
        h.pt3dadd(139.89,393.41,-82.18,0.782, sec = self.apical[30])
        h.pt3dadd(146.6,396.32,-89.9,0.848, sec = self.apical[30])
        h.pt3dadd(151.4,398.27,-92.56,0.858, sec = self.apical[30])
        h.pt3dadd(156.2,400.21,-99.54,0.826, sec = self.apical[30])
        h.pt3dadd(161.31,401.51,-104,0.88, sec = self.apical[30])
        h.pt3dadd(165.47,399.89,-106.56,0.858, sec = self.apical[30])
        h.pt3dadd(168.67,403.13,-107.62,0.89, sec = self.apical[30])
        h.pt3dadd(173.46,401.51,-110.54,0.882, sec = self.apical[30])
        h.pt3dadd(178.26,405.72,-114.12,0.824, sec = self.apical[30])
        h.pt3dadd(181.78,407.66,-118.46,0.924, sec = self.apical[30])
        h.pt3dadd(185.3,411.23,-120.88,0.912, sec = self.apical[30])
        h.pt3dadd(187.86,414.79,-124.58,0.954, sec = self.apical[30])
        h.pt3dadd(193.11,417.84,-125.28,0.832, sec = self.apical[30])
        h.pt3dadd(196.63,418.48,-125.28,0.858, sec = self.apical[30])
        h.pt3dadd(198.87,420.75,-126.66,0.88, sec = self.apical[30])

        self.apical[31].connect(self.apical[30])
        h.pt3dclear(sec = self.apical[31])
        h.pt3dadd(198.87,420.75,-126.66,0.88, sec = self.apical[31])
        h.pt3dadd(198.03,423.17,-124.34,0.926, sec = self.apical[31])
        h.pt3dadd(199.62,426.74,-124.34,0.81, sec = self.apical[31])
        h.pt3dadd(202.82,429.65,-127.7,0.884, sec = self.apical[31])
        h.pt3dadd(204.42,432.24,-128.8,0.968, sec = self.apical[31])
        h.pt3dadd(205.06,435.48,-128.8,0.946, sec = self.apical[31])
        h.pt3dadd(207.94,436.13,-129.96,0.864, sec = self.apical[31])
        h.pt3dadd(207.94,439.37,-129.96,0.888, sec = self.apical[31])
        h.pt3dadd(212.74,440.67,-132.14,0.91, sec = self.apical[31])
        h.pt3dadd(214.01,444.23,-133.72,0.838, sec = self.apical[31])
        h.pt3dadd(214.33,448.44,-130.06,0.938, sec = self.apical[31])
        h.pt3dadd(215.29,452.33,-128.84,0.85, sec = self.apical[31])
        h.pt3dadd(219.13,453.95,-127.3,0.87, sec = self.apical[31])
        h.pt3dadd(219.77,458.16,-128.14,0.808, sec = self.apical[31])
        h.pt3dadd(223.61,459.78,-128.5,0.84, sec = self.apical[31])
        h.pt3dadd(226.17,461.73,-129.82,0.85, sec = self.apical[31])
        h.pt3dadd(229.36,463.67,-128,0.804, sec = self.apical[31])
        h.pt3dadd(229.68,467.88,-128,0.66, sec = self.apical[31])
        h.pt3dadd(233.2,470.47,-128.24,0.726, sec = self.apical[31])
        h.pt3dadd(237.04,475.33,-130.38,0.472, sec = self.apical[31])

        self.apical[32].connect(self.apical[30])
        h.pt3dclear(sec = self.apical[32])
        h.pt3dadd(198.87,420.75,-126.66,0.88, sec = self.apical[32])
        h.pt3dadd(204.62,423.02,-129.44,0.64, sec = self.apical[32])
        h.pt3dadd(210.7,425.61,-130.44,0.64, sec = self.apical[32])
        h.pt3dadd(215.5,425.29,-131.18,0.64, sec = self.apical[32])
        h.pt3dadd(220.93,427.23,-132.26,0.64, sec = self.apical[32])
        h.pt3dadd(225.73,427.56,-134.02,0.64, sec = self.apical[32])
        h.pt3dadd(229.89,425.29,-135.76,0.64, sec = self.apical[32])
        h.pt3dadd(233.72,426.58,-137.1,0.64, sec = self.apical[32])
        h.pt3dadd(237.24,429.18,-134.88,0.64, sec = self.apical[32])
        h.pt3dadd(242.04,430.15,-135.94,0.64, sec = self.apical[32])
        h.pt3dadd(245.87,431.77,-137.24,0.64, sec = self.apical[32])
        h.pt3dadd(250.47,435.48,-138.86,0.64, sec = self.apical[32])
        h.pt3dadd(255.59,435.48,-139.74,0.64, sec = self.apical[32])
        h.pt3dadd(259.1,437.43,-140.58,0.64, sec = self.apical[32])
        h.pt3dadd(262.94,438.72,-141.14,0.64, sec = self.apical[32])
        h.pt3dadd(268.06,440.02,-141.14,0.64, sec = self.apical[32])
        h.pt3dadd(271.58,440.99,-144.06,0.64, sec = self.apical[32])
        h.pt3dadd(276.37,440.34,-145.48,0.64, sec = self.apical[32])

        self.apical[33].connect(self.apical[7])
        h.pt3dclear(sec = self.apical[33])
        h.pt3dadd(21.39,193.31,-40.1,1.6, sec = self.apical[33])
        h.pt3dadd(23.31,191.04,-43.66,1.08, sec = self.apical[33])
        h.pt3dadd(25.87,190.39,-44.46,0.986, sec = self.apical[33])
        h.pt3dadd(29.07,189.74,-44.46,1.102, sec = self.apical[33])
        h.pt3dadd(32.58,188.45,-44.88,0.924, sec = self.apical[33])
        h.pt3dadd(36.42,189.42,-45.34,0.954, sec = self.apical[33])
        h.pt3dadd(39.94,190.39,-45.34,0.982, sec = self.apical[33])

        self.apical[34].connect(self.apical[33])
        h.pt3dclear(sec = self.apical[34])
        h.pt3dadd(39.94,190.39,-45.34,0.982, sec = self.apical[34])
        h.pt3dadd(41.1,193.81,-41.68,0.96, sec = self.apical[34])
        h.pt3dadd(41.73,197.69,-40.1,0.96, sec = self.apical[34])
        h.pt3dadd(44.61,201.91,-39.84,0.96, sec = self.apical[34])
        h.pt3dadd(45.57,207.41,-37.08,0.96, sec = self.apical[34])
        h.pt3dadd(46.53,213.57,-36.72,0.96, sec = self.apical[34])
        h.pt3dadd(48.13,218.11,-36.72,0.96, sec = self.apical[34])
        h.pt3dadd(52.29,222.64,-37.6,0.96, sec = self.apical[34])
        h.pt3dadd(53.89,227.18,-36.74,0.96, sec = self.apical[34])
        h.pt3dadd(57.72,230.09,-36.38,0.96, sec = self.apical[34])
        h.pt3dadd(60.6,231.06,-36.28,0.96, sec = self.apical[34])
        h.pt3dadd(62.52,235.92,-36.22,0.928, sec = self.apical[34])
        h.pt3dadd(65.08,240.14,-35.02,0.896, sec = self.apical[34])
        h.pt3dadd(67.11,244.86,-38.28,1.016, sec = self.apical[34])
        h.pt3dadd(70.31,249.72,-37.26,0.822, sec = self.apical[34])
        h.pt3dadd(73.51,254.9,-37.26,0.772, sec = self.apical[34])
        h.pt3dadd(76.07,259.43,-36.78,0.668, sec = self.apical[34])
        h.pt3dadd(77.99,263.97,-34.26,0.736, sec = self.apical[34])
        h.pt3dadd(81.5,264.94,-33.34,0.618, sec = self.apical[34])
        h.pt3dadd(85.66,265.91,-31.44,0.64, sec = self.apical[34])
        h.pt3dadd(90.14,266.89,-29.46,0.552, sec = self.apical[34])

        self.apical[35].connect(self.apical[33])
        h.pt3dclear(sec = self.apical[35])
        h.pt3dadd(39.94,190.39,-45.34,0.982, sec = self.apical[35])
        h.pt3dadd(42.82,188.77,-44.24,0.912, sec = self.apical[35])
        h.pt3dadd(46.97,187.48,-46.44,0.97, sec = self.apical[35])
        h.pt3dadd(49.21,184.88,-46.72,0.844, sec = self.apical[35])
        h.pt3dadd(52.41,184.56,-47.7,0.906, sec = self.apical[35])
        h.pt3dadd(55.61,182.94,-48.66,0.806, sec = self.apical[35])
        h.pt3dadd(59.13,184.56,-49.94,0.73, sec = self.apical[35])
        h.pt3dadd(61.36,182.94,-51.14,0.83, sec = self.apical[35])
        h.pt3dadd(65.2,181.64,-52.16,0.784, sec = self.apical[35])
        h.pt3dadd(70,180.67,-53.64,0.902, sec = self.apical[35])
        h.pt3dadd(73.2,181.64,-54.8,0.77, sec = self.apical[35])
        h.pt3dadd(75.95,181.17,-55.82,0.856, sec = self.apical[35])
        h.pt3dadd(79.47,179.55,-60.08,0.836, sec = self.apical[35])
        h.pt3dadd(81.39,177.28,-60.6,0.716, sec = self.apical[35])
        h.pt3dadd(82.67,174.37,-61.62,0.71, sec = self.apical[35])
        h.pt3dadd(86.5,174.04,-63.66,0.544, sec = self.apical[35])
        h.pt3dadd(88.74,173.07,-64.94,0.466, sec = self.apical[35])

        self.apical[36].connect(self.apical[6])
        h.pt3dclear(sec = self.apical[36])
        h.pt3dadd(3.46,172.27,-34.8,1.6, sec = self.apical[36])
        h.pt3dadd(1.86,175.84,-37.06,0.96, sec = self.apical[36])
        h.pt3dadd(-0.7,178.75,-37.52,0.96, sec = self.apical[36])

        self.apical[37].connect(self.apical[36])
        h.pt3dclear(sec = self.apical[37])
        h.pt3dadd(-0.7,178.75,-37.52,0.96, sec = self.apical[37])
        h.pt3dadd(0.13,181.84,-36.74,0.96, sec = self.apical[37])
        h.pt3dadd(-1.47,184.43,-36.66,0.64, sec = self.apical[37])
        h.pt3dadd(-3.38,185.4,-36.08,0.64, sec = self.apical[37])
        h.pt3dadd(-3.38,188.32,-36.7,0.64, sec = self.apical[37])
        h.pt3dadd(-4.34,190.26,-37.52,0.64, sec = self.apical[37])
        h.pt3dadd(-5.94,190.91,-38.62,0.64, sec = self.apical[37])
        h.pt3dadd(-6.58,193.82,-38.72,0.64, sec = self.apical[37])
        h.pt3dadd(-8.5,196.09,-38.72,0.64, sec = self.apical[37])
        h.pt3dadd(-9.46,199.01,-39.3,0.64, sec = self.apical[37])
        h.pt3dadd(-10.1,202.89,-40,0.64, sec = self.apical[37])
        h.pt3dadd(-10.74,204.84,-40.5,0.64, sec = self.apical[37])
        h.pt3dadd(-11.7,208.08,-41.04,0.64, sec = self.apical[37])
        h.pt3dadd(-12.66,210.67,-41.4,0.64, sec = self.apical[37])
        h.pt3dadd(-13.62,212.29,-42.26,0.64, sec = self.apical[37])
        h.pt3dadd(-14.58,213.91,-43.42,0.64, sec = self.apical[37])
        h.pt3dadd(-17.14,215.21,-44.86,0.64, sec = self.apical[37])
        h.pt3dadd(-18.09,218.12,-46.2,0.64, sec = self.apical[37])
        h.pt3dadd(-18.09,219.42,-48.84,0.64, sec = self.apical[37])
        h.pt3dadd(-20.33,220.39,-48.84,0.64, sec = self.apical[37])
        h.pt3dadd(-20.33,222.98,-52.5,0.64, sec = self.apical[37])
        h.pt3dadd(-22.89,224.28,-52.5,0.64, sec = self.apical[37])

        self.apical[38].connect(self.apical[36])
        h.pt3dclear(sec = self.apical[38])
        h.pt3dadd(-0.7,178.75,-37.52,0.96, sec = self.apical[38])
        h.pt3dadd(-4.22,180.37,-38.1,0.64, sec = self.apical[38])
        h.pt3dadd(-6.66,181.17,-38.1,0.64, sec = self.apical[38])
        h.pt3dadd(-7.62,183.11,-37.4,0.64, sec = self.apical[38])
        h.pt3dadd(-10.82,183.76,-37.1,0.64, sec = self.apical[38])
        h.pt3dadd(-13.06,183.76,-36.14,0.64, sec = self.apical[38])
        h.pt3dadd(-15.62,187.32,-34.4,0.64, sec = self.apical[38])
        h.pt3dadd(-17.54,191.21,-34.06,0.64, sec = self.apical[38])
        h.pt3dadd(-19.46,195.42,-33.4,0.64, sec = self.apical[38])
        h.pt3dadd(-20.74,198.34,-31.68,0.64, sec = self.apical[38])
        h.pt3dadd(-19.46,200.61,-31.68,0.64, sec = self.apical[38])
        h.pt3dadd(-21.37,202.23,-29.92,0.64, sec = self.apical[38])
        h.pt3dadd(-22.33,203.85,-26.44,0.64, sec = self.apical[38])
        h.pt3dadd(-24.25,205.79,-23.34,0.64, sec = self.apical[38])
        h.pt3dadd(-24.25,207.73,-23.34,0.64, sec = self.apical[38])
        h.pt3dadd(-25.53,212.59,-21.62,0.64, sec = self.apical[38])
        h.pt3dadd(-23.61,214.86,-20.24,0.64, sec = self.apical[38])
        h.pt3dadd(-24.25,217.45,-19.2,0.64, sec = self.apical[38])
        h.pt3dadd(-24.25,220.05,-19.2,0.64, sec = self.apical[38])
        h.pt3dadd(-25.53,221.67,-18.44,0.64, sec = self.apical[38])
        h.pt3dadd(-24.89,225.55,-17.36,0.64, sec = self.apical[38])
        h.pt3dadd(-26.81,228.15,-16.08,0.64, sec = self.apical[38])
        h.pt3dadd(-27.77,230.74,-14.2,0.64, sec = self.apical[38])
        h.pt3dadd(-29.05,232.03,-12.02,0.64, sec = self.apical[38])
        h.pt3dadd(-30.01,231.38,-12.02,0.64, sec = self.apical[38])
        h.pt3dadd(-31.61,230.74,-10.68,0.64, sec = self.apical[38])
        h.pt3dadd(-32.57,232.03,-7.84,0.64, sec = self.apical[38])
        h.pt3dadd(-32.89,234.95,-6.18,0.64, sec = self.apical[38])
        h.pt3dadd(-34.63,236.42,-4.42,0.64, sec = self.apical[38])
        h.pt3dadd(-34.63,238.04,-1.7,0.64, sec = self.apical[38])
        h.pt3dadd(-36.22,239.98,-0.28,0.64, sec = self.apical[38])
        h.pt3dadd(-37.18,242.25,0.36,0.64, sec = self.apical[38])
        h.pt3dadd(-38.46,244.19,2.24,0.64, sec = self.apical[38])
        h.pt3dadd(-38.14,246.78,2.26,0.64, sec = self.apical[38])
        h.pt3dadd(-41.02,247.11,3.84,0.64, sec = self.apical[38])
        h.pt3dadd(-42.3,247.11,7.54,0.64, sec = self.apical[38])
        h.pt3dadd(-43.26,250.35,7.54,0.64, sec = self.apical[38])
        h.pt3dadd(-46.46,250.67,9.92,0.64, sec = self.apical[38])
        h.pt3dadd(-46.78,252.61,12.6,0.64, sec = self.apical[38])

        self.apical[39].connect(self.apical[5])
        h.pt3dclear(sec = self.apical[39])
        h.pt3dadd(-16.01,135.76,-29.88,1.298, sec = self.apical[39])
        h.pt3dadd(-12.81,134.47,-39.18,1.118, sec = self.apical[39])
        h.pt3dadd(-9.3,134.14,-40.2,1.092, sec = self.apical[39])
        h.pt3dadd(-6.74,131.88,-40.84,1.208, sec = self.apical[39])
        h.pt3dadd(-5.14,129.93,-42.48,1.27, sec = self.apical[39])
        h.pt3dadd(-2.9,129.28,-46.68,1.262, sec = self.apical[39])
        h.pt3dadd(-1.3,127.02,-48.52,1.08, sec = self.apical[39])
        h.pt3dadd(-1.62,124.42,-50.62,1.256, sec = self.apical[39])
        h.pt3dadd(0.62,123.13,-54.38,0.96, sec = self.apical[39])
        h.pt3dadd(1.9,124.42,-56.68,0.96, sec = self.apical[39])
        h.pt3dadd(2.86,123.45,-59.26,0.96, sec = self.apical[39])
        h.pt3dadd(4.91,122.32,-60.98,0.96, sec = self.apical[39])
        h.pt3dadd(6.51,120.7,-62.88,1.006, sec = self.apical[39])
        h.pt3dadd(9.07,119.41,-66.06,0.898, sec = self.apical[39])
        h.pt3dadd(11.31,119.41,-70.6,0.672, sec = self.apical[39])
        h.pt3dadd(12.91,115.84,-74.86,0.752, sec = self.apical[39])
        h.pt3dadd(14.19,114.22,-76.82,0.744, sec = self.apical[39])
        h.pt3dadd(17.7,113.58,-76.82,0.614, sec = self.apical[39])
        h.pt3dadd(20.9,116.82,-80.66,0.63, sec = self.apical[39])
        h.pt3dadd(21.22,120.06,-76.5,0.644, sec = self.apical[39])
        h.pt3dadd(25.38,121.03,-75.08,0.67, sec = self.apical[39])

        self.apical[40].connect(self.apical[4])
        h.pt3dclear(sec = self.apical[40])
        h.pt3dadd(-16.83,133.99,-29.88,1.6, sec = self.apical[40])
        h.pt3dadd(-18.11,132.04,-39,1.17, sec = self.apical[40])
        h.pt3dadd(-20.35,130.75,-39.92,1.012, sec = self.apical[40])
        h.pt3dadd(-20.99,129.13,-41.26,0.926, sec = self.apical[40])
        h.pt3dadd(-22.27,127.51,-42.44,0.934, sec = self.apical[40])
        h.pt3dadd(-22.59,125.89,-43.22,0.934, sec = self.apical[40])
        h.pt3dadd(-23.87,123.62,-44.58,0.872, sec = self.apical[40])
        h.pt3dadd(-25.79,123.3,-47.88,0.918, sec = self.apical[40])
        h.pt3dadd(-28.03,122.65,-50.14,0.828, sec = self.apical[40])
        h.pt3dadd(-28.99,121.03,-52.7,0.786, sec = self.apical[40])
        h.pt3dadd(-29.62,118.76,-55.28,0.842, sec = self.apical[40])
        h.pt3dadd(-32.18,118.44,-57.7,0.856, sec = self.apical[40])
        h.pt3dadd(-32.5,113.9,-59.66,0.888, sec = self.apical[40])
        h.pt3dadd(-33.46,110.01,-59.7,0.912, sec = self.apical[40])
        h.pt3dadd(-35.06,109.36,-59.92,0.838, sec = self.apical[40])
        h.pt3dadd(-35.7,110.34,-64.7,0.748, sec = self.apical[40])
        h.pt3dadd(-36.66,108.39,-68,0.888, sec = self.apical[40])
        h.pt3dadd(-37.3,106.12,-68,0.824, sec = self.apical[40])
        h.pt3dadd(-38.26,103.21,-74.76,0.64, sec = self.apical[40])

        self.apical[41].connect(self.apical[3])
        h.pt3dclear(sec = self.apical[41])
        h.pt3dadd(-20.81,122.8,-27.14,1.6, sec = self.apical[41])
        h.pt3dadd(-18.25,122.48,-21.48,0.966, sec = self.apical[41])
        h.pt3dadd(-18.25,125.4,-21.48,0.992, sec = self.apical[41])
        h.pt3dadd(-20.49,127.34,-20.3,0.874, sec = self.apical[41])
        h.pt3dadd(-21.45,128.96,-19.02,0.802, sec = self.apical[41])
        h.pt3dadd(-24.01,130.26,-17.52,0.77, sec = self.apical[41])
        h.pt3dadd(-24.97,131.88,-14.94,0.756, sec = self.apical[41])
        h.pt3dadd(-26.24,135.44,-13.34,0.78, sec = self.apical[41])
        h.pt3dadd(-27.52,137.38,-11.78,0.72, sec = self.apical[41])
        h.pt3dadd(-29.76,139.65,-9.32,0.75, sec = self.apical[41])
        h.pt3dadd(-31.04,140.3,-8.54,0.766, sec = self.apical[41])
        h.pt3dadd(-31.36,143.86,-7.54,0.64, sec = self.apical[41])
        h.pt3dadd(-33.92,145.81,-6.68,0.594, sec = self.apical[41])
        h.pt3dadd(-36.16,146.78,-7.2,0.574, sec = self.apical[41])
        h.pt3dadd(-38.08,151.31,-5.16,0.628, sec = self.apical[41])
        h.pt3dadd(-40,152.29,-4.78,0.566, sec = self.apical[41])
        h.pt3dadd(-40.63,155.53,-4.26,0.572, sec = self.apical[41])
        h.pt3dadd(-43.19,157.15,-3.92,0.522, sec = self.apical[41])
        h.pt3dadd(-45.43,158.44,-1.06,0.484, sec = self.apical[41])
        h.pt3dadd(-47.67,160.06,0.7,0.448, sec = self.apical[41])

        self.apical[42].connect(self.apical[2])
        h.pt3dclear(sec = self.apical[42])
        h.pt3dadd(-38.38,76.72,-16.44,1.92, sec = self.apical[42])
        h.pt3dadd(-41.58,78.99,-19,0.96, sec = self.apical[42])
        h.pt3dadd(-44.46,81.26,-20.62,0.96, sec = self.apical[42])
        h.pt3dadd(-46.38,81.91,-20,0.96, sec = self.apical[42])
        h.pt3dadd(-48.62,85.47,-19.94,0.96, sec = self.apical[42])
        h.pt3dadd(-51.49,87.41,-19.58,0.96, sec = self.apical[42])
        h.pt3dadd(-53.73,88.06,-20.7,0.96, sec = self.apical[42])

        self.apical[43].connect(self.apical[42])
        h.pt3dclear(sec = self.apical[43])
        h.pt3dadd(-53.73,88.06,-20.7,0.96, sec = self.apical[43])
        h.pt3dadd(-56.14,88.86,-21.42,0.64, sec = self.apical[43])
        h.pt3dadd(-58.38,89.18,-21.36,0.64, sec = self.apical[43])
        h.pt3dadd(-60.62,88.86,-23.58,0.64, sec = self.apical[43])
        h.pt3dadd(-63.81,88.86,-24,0.64, sec = self.apical[43])
        h.pt3dadd(-66.05,87.56,-26.24,0.64, sec = self.apical[43])
        h.pt3dadd(-66.69,86.91,-30.9,0.64, sec = self.apical[43])
        h.pt3dadd(-68.61,86.59,-33.2,0.616, sec = self.apical[43])
        h.pt3dadd(-70.85,85.62,-34.32,0.62, sec = self.apical[43])
        h.pt3dadd(-72.45,85.94,-38.1,0.55, sec = self.apical[43])
        h.pt3dadd(-72.45,87.56,-40.12,0.484, sec = self.apical[43])
        h.pt3dadd(-74.69,87.56,-41.78,0.48, sec = self.apical[43])
        h.pt3dadd(-76.29,86.91,-43.12,0.45, sec = self.apical[43])
        h.pt3dadd(-78.53,84.97,-44.54,0.498, sec = self.apical[43])
        h.pt3dadd(-80.44,83.35,-47.78,0.434, sec = self.apical[43])

        self.apical[44].connect(self.apical[42])
        h.pt3dclear(sec = self.apical[44])
        h.pt3dadd(-53.73,88.06,-20.7,0.96, sec = self.apical[44])
        h.pt3dadd(-55.33,91.3,-16.86,0.96, sec = self.apical[44])
        h.pt3dadd(-57.25,92.27,-13.84,0.864, sec = self.apical[44])
        h.pt3dadd(-60.45,93.57,-13.82,0.64, sec = self.apical[44])
        h.pt3dadd(-63.33,95.51,-14.32,0.644, sec = self.apical[44])
        h.pt3dadd(-65.24,97.46,-14.42,0.7, sec = self.apical[44])
        h.pt3dadd(-69.08,98.75,-14.42,0.66, sec = self.apical[44])
        h.pt3dadd(-70.68,101.02,-15.68,0.6, sec = self.apical[44])
        h.pt3dadd(-71.32,102.96,-16.42,0.59, sec = self.apical[44])
        h.pt3dadd(-72.92,104.58,-16.76,0.484, sec = self.apical[44])
        h.pt3dadd(-75.48,105.56,-16.76,0.522, sec = self.apical[44])
        h.pt3dadd(-76.76,108.47,-16.78,0.422, sec = self.apical[44])


        # Set up the geom_nseg
