from __future__ import division
__author__ = 'Zack Gainsforth'
__copyright__ = 'Copyright 2015, Zack Gainsforth'
__email__ = 'zsg@gainsforth.com'

from numpy import *
import os
if __name__ != '__main__':
    import PhysicsBasics as pb

def AnalyzePhase(AtPct=None, WtPct=None, OxWtPct=None):

    #Normalize our AtPct vector.
    AtPct = AtPct/sum(AtPct)*100

    # A dictionary of the AtPct values would be useful so we can look up by element name.
    E = dict(zip(pb.ElementalSymbols, AtPct))

    # We output an output string which contains the analysis.
    OutStr = '--- Common ratios ---\n\n'

    # Report the atom ratios.
    if E['Fe'] > 0 and E['Ni'] > 0:
        OutStr += 'Fe/Ni = %0.3f, %0.3f X chondritic\n' % (E['Fe']/E['Ni'], (E['Fe']/E['Ni'])*float('5.751E-2'))
    # if E['Se'] > 0:
    #     OutStr += 'S/Se = %0.3f, %0.3f X chondritic\n' % (E['S']/E['Se'], (E['S']/E['Se'])/float('6.344E+3'))
    # if E['Cr'] > 0:
    #     OutStr += 'Cr/Fe = %0.3f, %0.3f X chondritic\n' % (E['Cr']/E['Fe'], (E['Cr']/E['Fe'])/float('1.564E-2'))
    # if E['Mn'] > 0:
    #     OutStr += 'Mn/Fe = %0.3f, %0.3f X chondritic\n' % (E['Mn']/E['Fe'], (E['Mn']/E['Fe'])/float('1.084E-2'))
    # if E['Cu'] > 0:
    #     OutStr += 'Cu/Fe = %0.3f, %0.3f X chondritic\n' % (E['Cu']/E['Fe'], (E['Cu']/E['Fe'])/float('6.036E-4'))
    # if E['Zn'] > 0:
    #     OutStr += 'Zn/Fe = %0.3f, %0.3f X chondritic\n' % (E['Zn']/E['Fe'], (E['Zn']/E['Fe'])/float('1.478E-3'))


    # We output an output string which contains the analysis.
    OutStr =+ '--- Chondritic Analysis ---\n\n'

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

    # # Report the atom ratios.
    # OutStr += '(Fe+Ni)/S = %0.3f\n' % ((E['Fe']+E['Ni'])/E['S'])
    # if E['Ni'] > 0:
    #     OutStr += 'Ni/Fe = %0.3f, %0.3f X chondritic\n' % (E['Ni']/E['Fe'], (E['Ni']/E['Fe'])/float('5.751E-2'))
    # if E['Se'] > 0:
    #     OutStr += 'S/Se = %0.3f, %0.3f X chondritic\n' % (E['S']/E['Se'], (E['S']/E['Se'])/float('6.344E+3'))
    # if E['Cr'] > 0:
    #     OutStr += 'Cr/Fe = %0.3f, %0.3f X chondritic\n' % (E['Cr']/E['Fe'], (E['Cr']/E['Fe'])/float('1.564E-2'))
    # if E['Mn'] > 0:
    #     OutStr += 'Mn/Fe = %0.3f, %0.3f X chondritic\n' % (E['Mn']/E['Fe'], (E['Mn']/E['Fe'])/float('1.084E-2'))
    # if E['Cu'] > 0:
    #     OutStr += 'Cu/Fe = %0.3f, %0.3f X chondritic\n' % (E['Cu']/E['Fe'], (E['Cu']/E['Fe'])/float('6.036E-4'))
    # if E['Zn'] > 0:
    #     OutStr += 'Zn/Fe = %0.3f, %0.3f X chondritic\n' % (E['Zn']/E['Fe'], (E['Zn']/E['Fe'])/float('1.478E-3'))
    # OutStr += '(Fe+Ni+Cr+Mn+Cu+Zn+Co)/(S+Se) = %0.3f\n' % (Cations/Anions)
    # OutStr += 'Probable superlattice at room temperature: %s\n' % (NakazawaPhase)
    # OutStr += 'Ref: Nakazawa, H., & Morimoto, N. (1971). Phase relations and superstructures of pyrrhotite, Fe1-xS. Materials Research Bulletin, 6(5), 345-357.\n'

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
