from __future__ import division
__author__ = 'Zack Gainsforth'
__copyright__ = 'Copyright 2014, Zack Gainsforth'
__email__ = 'zsg@gainsforth.com'

from numpy import *
if __name__ != '__main__':
    import PhysicsBasics as pb


def AnalyzePhase(AtPct=None, WtPct=None, OxWtPct=None):
    """ Assume an "ideal" spinel...
    """

    #Normalize our AtPct vector.
    AtPct = AtPct/sum(AtPct)*100

    # We output an output string which contains the analysis.
    OutStr = '--- Spinel Analysis ---\n\n'

    # This analysis only knows about these elements:
    KnownElements = ['Si', 'Ca', 'O', 'Mg', 'Al', 'Ti', 'V', 'Cr', 'Mn', 'Fe', 'Ni', 'Zn']

    # If anything else accounts for more than 2 At % then this analysis is garbage
    OtherCations = 0
    for Zsub, ElAtPct in enumerate(AtPct):
        # If this is an unknown cation, and it has any abundance, add it to our cumulative abundance of unknowns.
        if ElAtPct > 0 and pb.ElementalSymbols[Zsub+1] not in KnownElements:
            OtherCations += ElAtPct

    if OtherCations > 2:
        OutStr += 'More than 2% of the atomic abundance is comprised by atoms other than: ' + ' '.join(KnownElements) + '.'
        OutStr += '\nCannot analyze.'
        return OutStr

    # If the cation/O ratio is off by more than 2%, then we can't analyze it.
    if (abs(AtPct[pb.O-1] - 4/7*100) > 2) or (abs((sum(AtPct)-AtPct[pb.O-1]) - 3/7*100) > 2):
        OutStr += 'Cation/Anion ratio is not within 2% of 3/4.'
        OutStr += '\nCannot analyze.'
        return OutStr

    E = dict()

    for Element in KnownElements:
        E[Element] = eval('AtPct[pb.%s-1]/100*7'%Element)

    OriginalTotalCations = E['Si'] + E['Ti'] + E['Al'] + E['Mn'] + E['Mg'] + E['Ca'] + E['Ni'] + E['Zn'] + E['Cr'] + E['V'] + E['Fe']
    # For the stoichiometry calculation to work, we have to have EXACTLY 3 cations.  So make it so, but we will keep the original number for reporting.
    for i in ['Si','Ti','Al','Mn','Mg','Ca','Ni','Zn','Cr','V','Fe']:
        E[i] *= 3/OriginalTotalCations

    # Calculate Fe3+/sum(Fe) by stoichiometry.  Assume nominal oxidation states for all the other elements, and only allow the oxidation state of Fe to change.
    Charge = E['Si']*4 + E['Ti']*4 + E['Al']*3 + E['Mn']*2 + E['Mg']*2 + E['Ca']*2 + E['Ni']*2 + E['Zn']*2 + E['Cr']*3 + E['V']*3

    # We should have 3 cations.  In this case, we expect a total charge of 8 (2*3+ + 2+)  Figure how much charge we need from the Fe.
    ChargeDeficit = 8-Charge
    # x is the Fe2+ fraction.  Gotten by solving ChargeDeficit = x*Fe*2 + (1-x)*Fe+3
    x = 3 - ChargeDeficit/E['Fe']

    TotalCations = E['Si'] + E['Ti'] + E['Al'] + E['Mn'] + E['Mg'] + E['Ca'] + E['Ni'] + E['Zn'] + E['Cr'] + E['V'] + E['Fe']
    TotalCharge = Charge + x*E['Fe']*2 + (1-x)*E['Fe']*3

    OutStr += '{:>11s}:    {:<1.3f}\n'.format('Sum Cations', OriginalTotalCations)
    #OutStr += '{:>11s}:    {:<1.3f}\n'.format('Total Charge', TotalCharge) # This one's not so useful.  It will always produce 8...
    OutStr += 'Fe3+/sum(Fe) =  {:.3f}\n'.format(1-x)

    return OutStr
    
if __name__ == '__main__':

    import imp
    pb = imp.load_source('PhysicsBasics', '../PhysicsBasics.py')

    # Ideal magnesiospinel
    AtPct = zeros(pb.MAXELEMENT)
    AtPct[pb.O-1] = 4/7*100
    AtPct[pb.Mg-1] = 1/7*100
    AtPct[pb.Al-1] = 2/7*100
    print 'Magnesiospinel: Mg Al2 O4:\n'
    print AnalyzePhase(AtPct)

    # Ideal chromite
    AtPct = zeros(pb.MAXELEMENT)
    AtPct[pb.O-1] = 4/7*100
    AtPct[pb.Fe-1] = 1/7*100
    AtPct[pb.Cr-1] = 2/7*100
    print 'Chromite: Fe Cr2 O4:\n'
    print AnalyzePhase(AtPct)

    # Ideal Ulvospinel
    AtPct = zeros(pb.MAXELEMENT)
    AtPct[pb.O-1] = 4/7*100
    AtPct[pb.Ti-1] = 1/7*100
    AtPct[pb.Fe-1] = 2/7*100
    print 'Ulvospinel: Ti Fe2 O4:\n'
    print AnalyzePhase(AtPct)

    # UC chromite
    AtPct = zeros(pb.MAXELEMENT)
    AtPct[pb.O-1] =  57.270
    AtPct[pb.Cr-1] = 17.016
    AtPct[pb.Ti-1] = 0.174
    AtPct[pb.Al-1] = 7.904
    AtPct[pb.Fe-1] = 10.275
    AtPct[pb.Mn-1] = 0.114
    AtPct[pb.Mg-1] = 7.177
    AtPct[pb.V-1] =  0.066
    AtPct[pb.Si-1] = 0.005
    print 'UC Chromite:\n'
    print AnalyzePhase(AtPct)

