from __future__ import division
__author__ = 'Zack Gainsforth'
__copyright__ = 'Copyright 2015, Zack Gainsforth'
__email__ = 'zsg@gainsforth.com'

import matplotlib
import matplotlib.pyplot as plt
from numpy import *
import os
if __name__ != '__main__':
    import PhysicsBasics as pb

# Set the bold level.
boldlevel=3
FontSizeBasis = (boldlevel+2)*4    # Fonts get bigger as boldlevel increases
TickMajorBasis = boldlevel*4    # As fonts get bigger, they need a larger padding from the axis.
# Increase the size of the tick label fonts.
matplotlib.rc('xtick', labelsize=FontSizeBasis)
matplotlib.rc('ytick', labelsize=FontSizeBasis)
# Increase their padding.
matplotlib.rc('xtick.major', pad=TickMajorBasis)
matplotlib.rc('ytick.major', pad=TickMajorBasis)

def AnalyzePhase(AtPct=None, WtPct=None, OxWtPct=None):

    #Normalize our AtPct vector.
    AtPct = AtPct/sum(AtPct)*100

    # A dictionary of the AtPct values would be useful so we can look up by element name.
    E = dict(zip(pb.ElementalSymbols, AtPct))

    # We output an output string which contains the analysis.
    OutStr = '--- Simple At% ratios ---\n\n'

    OutStr += "Abundances ratioed to:\n"
    OutStr += "Element to   Mg       Si       Fe\n"
    OutStr += '-'*41 + '\n'
    for Zminus, E in enumerate(AtPct):
        if E != 0:
            EtoMg = E / AtPct[pb.Mg-1]
            EtoSi = E / AtPct[pb.Si-1]
            EtoFe = E / AtPct[pb.Fe-1]
            OutStr += '%-13s%-9.3f%-9.3f%-9.3f\n' % (tuple([pb.ElementalSymbols[Zminus+1]]) + tuple([EtoMg, EtoSi, EtoFe]))


    # We output an output string which contains the analysis.
    OutStr += '--- Chondritic Analysis ---\n\n'

    # Load the prosolar abundances.  This is recorded from the Lodders ref with logarithmic values.
    ProtosolarAbundancesFileName = 'ProtosolarAbundances.csv'
    if not os._exists(ProtosolarAbundancesFileName):
        ProtosolarAbundancesFileName = os.path.join('ConfigData', ProtosolarAbundancesFileName)
    Protosolar = genfromtxt(ProtosolarAbundancesFileName, delimiter=',', skip_header=1, dtype=None)
    ProtosolarDict = dict(Protosolar)   # This dictionary could be handy...
    Protosolar = array(zip(*Protosolar)[1]) # But we really need just a numpy array with the numbers.

    # Convert to vectors which are normalized to Mg, Si, and Fe.
    ProtosolarToMg = power(10, Protosolar)  # Get out of log space into linear space.  Now the numbers relate to AtPct.
    ProtosolarToMg /= ProtosolarToMg[pb.Mg-1]
    ProtosolarToSi = power(10, Protosolar)
    ProtosolarToSi /= ProtosolarToSi[pb.Si-1]
    ProtosolarToFe = power(10, Protosolar)
    ProtosolarToFe /= ProtosolarToFe[pb.Fe-1]

    # Print out the abundances normalized to protosolar.
    Ratios = list() # Keep track of the ratios, so at the end we can compute standard deviations.
    OutStr += "Abundances ratioed to protosolar and normalized to:\n"
    OutStr += "Element to   Mg       Si       Fe\n"
    OutStr += '-'*41 + '\n'
    for Zminus, E in enumerate(AtPct):
        if E != 0:
            EtoMg = E / AtPct[pb.Mg-1]
            EtoSi = E / AtPct[pb.Si-1]
            EtoFe = E / AtPct[pb.Fe-1]
            Ratios.append([EtoMg/ProtosolarToMg[Zminus], EtoSi/ProtosolarToSi[Zminus], EtoFe/ProtosolarToFe[Zminus]])
            OutStr += '%-13s%-9.3f%-9.3f%-9.3f\n' % (tuple([pb.ElementalSymbols[Zminus+1]]) + tuple(Ratios[-1]))
    Ratios = array(Ratios)
    Means = mean(Ratios, axis=0)
    Stdevs = std(Ratios, axis=0)
    OutStr += '-'*41 + '\n'
    OutStr += '%-13s%-9.3f%-9.3f%-9.3f\n' % (tuple(['Mean']) + tuple(Means))
    OutStr += '%-13s%-9.3f%-9.3f%-9.3f\n' % (tuple(['Standard dev']) + tuple(Stdevs))
    OutStr += '-'*41 + '\n'

    OutStr += '\nRef:Lodders, K. (2003). Solar System Abundances and Condensation Temperatures of the Elements. The Astrophysical Journal, 591(2), 1220-1247. http://doi.org/10.1086/375492\n'

    # Now draw a plot comparing this spectrum to CI and GEMS.  Only if Si is measured.
    if AtPct[pb.Si-1] != 0:
        # Literature numbers for GEMS from Bradley, J., & Ireland, T. (1996). The search for interstellar components in interplanetary dust particles. In B. A. S. Gustafson & M. S. Hanner (Eds.), Physics, Chemistry, and Dynamics of Interplanetary Dust (Vol. 104, pp. 275-282). IAU Colloq 150: Physics.
        # GEMSNums = dict()
        # GEMSNums['O'] = array([3.76, 3.7, 3.96, 3.51, 4.99])
        # GEMSNums['Mg'] = array([0.38, 0.24, 1.11, 0.65, 0.82])
        # GEMSNums['Al'] = array([0.12, 0.11, 0.08, 0.11, 0.12])
        # GEMSNums['S'] = array([0.14, 0.08, 0.10, 0.05, 0.12])
        # GEMSNums['Ca'] = array([0.01, 0.02, 0.08, 0.03, 0.04])
        # GEMSNums['Cr'] = array([0.02, 0.04, 0.03, 0.02, 0.01])
        # GEMSNums['Fe'] = array([0.42, 0.38, 0.70, 0.12, 0.43])
        # GEMSNums['Ni'] = array([0.03, 0.03, 0.05, 0.006, 0.03])

        GEMSElements = ['O', 'Mg', 'Al', 'S', 'Ca', 'Cr', 'Fe', 'Ni']
        GEMSElementsZ = [pb.O, pb.Mg, pb.Al, pb.S, pb.Ca, pb.Cr, pb.Fe, pb.Ni]
        GEMSElementsInds = range(len(GEMSElements))
        GEMSNums = array([[3.76, 0.38, 0.12, 0.14, 0.01, 0.02, 0.42, 0.03],
         [3.7,  0.24, 0.11, 0.08, 0.02, 0.04, 0.38, 0.03],
         [3.96, 1.11, 0.08, 0.10, 0.08, 0.03, 0.70, 0.05],
         [3.51, 0.65, 0.11, 0.05, 0.03, 0.02, 0.12, 0.006],
         [4.99, 0.82, 0.12, 0.12, 0.04, 0.01, 0.43, 0.03],
         ])

        #Average composition of Chondritic meteorites from Bradley (2007).
        # ChondriticNums = array([4.34, 1.075, 0.85, 0.515, 0.061, 0.013, 0.9, 0.049])
        # Chondritic from Lodders (2003)
        ChondriticNums = array([v for (k,v) in ProtosolarDict.items() if k in GEMSElements])
        ChondriticNums = power(10, ChondriticNums)
        ChondriticNums /= power(10, ProtosolarDict['Si'])

        SampleNums = zeros(8)
        for i, El in enumerate(GEMSElementsZ):
            if AtPct[El-1] != 0:
                SampleNums[i] = AtPct[El-1] / AtPct[pb.Si-1]

        # We will be plotting so clear the plot that may already be plotted.
        plt.clf()

        plt.scatter(GEMSElementsInds*5, GEMSNums, marker='v', color='blue', s=200,alpha=0.5)
        plt.scatter(GEMSElementsInds, SampleNums, marker='o', color='red', s=200,alpha=0.5)
        plt.scatter(GEMSElementsInds, ChondriticNums, marker='s', color='green', s=200,alpha=0.5)

        plt.xticks(GEMSElementsInds, GEMSElements, rotation='vertical')
        plt.gca().set_yscale('log')
        plt.legend(['Literature GEMS', 'This Spectrum', 'Chondritic'])
        plt.ylabel('Element/Si, At%', fontsize=FontSizeBasis)
        plt.gca().set_ylim([1e-3, 30])
        plt.tight_layout()
        plt.show()

    return OutStr
    
if __name__ == '__main__':

    import imp
    pb = imp.load_source('PhysicsBasics', '../PhysicsBasics.py')

    AtPct = zeros(pb.MAXELEMENT)
    AtPct[pb.O-1] = 61.9
    AtPct[pb.Mg-1] = 2.9
    AtPct[pb.Al-1] = 0.8
    AtPct[pb.Si-1] = 16.9
    AtPct[pb.S-1] = 6.1
    AtPct[pb.Cr-1] = 0.3
    AtPct[pb.Fe-1] = 11.1
    print 'Planetary Materials Page 2-54 (Rietmeijer: Interplanetary Dust Particles): Table 23, Line 1\n'
    print AnalyzePhase(AtPct)

    # Bradley, J. P. (2007). 1.26 - Interplanetary Dust Particles. In A. M. Davis (Ed.), Treatise on Geochemistry, Vol. 1, Meteorites, Comets, and Planets (pp. 689-711). Oxford: Pergamon. http://doi.org/10.1016/B0-08-043751-6/01152-X
    AtPct = zeros(pb.MAXELEMENT)
    AtPct[pb.C-1] = 1.75
    AtPct[pb.O-1] = 4.173
    AtPct[pb.Na-1] = 0.052
    AtPct[pb.Mg-1] = 0.980
    AtPct[pb.Al-1] = 0.075
    AtPct[pb.Si-1] = 1
    AtPct[pb.S-1] = 0.356
    AtPct[pb.Ca-1] = 0.052
    AtPct[pb.Cr-1] = 0.015
    AtPct[pb.Fe-1] = 0.697
    AtPct[pb.Ni-1] = 0.027
    print 'Chondritic IDPs bulk\n'
    print AnalyzePhase(AtPct)
