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
    KnownElements = ['O', 'Mg', 'Al', 'Si', 'Ca', 'Ti', 'V', 'Cr', 'Mn', 'Fe', 'Ni', 'Zn']

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

    # # Cations per 7 atoms.
    # for Element in KnownElements:
    #     E[Element] = eval('AtPct[pb.%s-1]/100*7'%Element)

    # TODO test spinel cations per four oxygens.
    # Cations per four oxygens.
    for Element in KnownElements:
        E[Element] = eval('AtPct[pb.%s-1]/AtPct[pb.O-1]*4'%Element)

    OriginalTotalCations = E['Si'] + E['Ti'] + E['Al'] + E['Mn'] + E['Mg'] + E['Ca'] + E['Ni'] + E['Zn'] + E['Cr'] + E['V'] + E['Fe']
    OriginalE = E.copy()
    # For the stoichiometry calculation to work, we have to have EXACTLY 3 cations.  So make it so, but we will keep the original number for reporting.
    for i in ['Si','Ti','Al','Mn','Mg','Ca','Ni','Zn','Cr','V','Fe']:
        E[i] *= 3/OriginalTotalCations


    # A is the octahedral site, usually 2+. (But also takes Ti4+)
    # B is the tetrahedral site, usually 3+.

    # Mg, Mn, Ni, Zn always go in A.
    A = E['Mg'] + E['Mn']+ E['Ni']+ E['Zn']
    ACharge = A*2

    # Al, Cr, and V, always go in B
    B = E['Al'] + E['Cr'] + E['V']
    BCharge = B*3

    # Ti goes in octahedral, and leaves a charge surplus.
    A += E['Ti']
    ACharge += E['Ti']*4

    # Fe splits the difference, filling up 3+ in B and 2+ in A.
    # So first we fill up A:

    Fe = E['Fe']
    FeA = (1 - A) # How many atoms to fill up A.
    FeB = Fe-FeA # The rest of the atoms are going into B.
    if FeA<=Fe:
        A += FeA
        ACharge += FeA*2
        Fe-=FeA

    # The remaining Fe goes in B as whatever oxidation state balances the total charge.
    ChargeDeficit = 8-(ACharge+BCharge)
    #AtomDeficit = 3-(A+B)

    # If there is not enough iron to make up the difference, it all goes 3+
    if ChargeDeficit > 3*FeB:
        Fe2 = 0
        Fe3 = FeB
        B += FeB
        BCharge += 3*FeB
    # Or if there is too much iron for the charge deficit, it all goes 2+
    elif ChargeDeficit <= 2*FeB:
        Fe2 = FeB
        Fe3 = 0
        B += FeB
        BCharge += 2*FeB
    else:
        # In between:
        # x is Fe2+ in B.  y is Fe3+ in B.  FeB is the total number of Fe atoms in B.
        # ChargeDeficit is the total charge supplied by the Fe.
        # 2x+3y = ChargeDeficit
        # x+y = FeB
        # Solve for x (Fe2+) and y (Fe3+)
        Fe2 = (3*FeB-ChargeDeficit)
        Fe3 = (ChargeDeficit-2*FeB)
        B += Fe2+Fe3
        BCharge += 2*Fe2 + 3*Fe3

    OutStr += 'Site A (octahedral):\n'
    OutStr += '{:>11s}:    {:<10s}\n'.format('Element', 'Occupancy')
    OutStr += '{:>11s}:    {:<1.3f}\n'.format('Mg2+', E['Mg'])
    OutStr += '{:>11s}:    {:<1.3f}\n'.format('Mn2+', E['Mn'])
    OutStr += '{:>11s}:    {:<1.3f}\n'.format('Ni2+', E['Ni'])
    OutStr += '{:>11s}:    {:<1.3f}\n'.format('Zn2+', E['Zn'])
    OutStr += '{:>11s}:    {:<1.3f}\n'.format('Fe2+', FeA)
    OutStr += '{:>11s}:    {:<1.3f}\n'.format('Ti4+', E['Ti'])
    OutStr += '{:>11s}:    {:<1.3f}\n'.format('Total occ', A)
    OutStr += '{:>11s}:    {:<1.3f}\n'.format('Charge', ACharge)
    OutStr += '\n'
    OutStr += 'Site B (Tetrahedral):\n'
    OutStr += '{:>11s}:    {:<10s}\n'.format('Element', 'Occupancy')
    OutStr += '{:>11s}:    {:<1.3f}\n'.format('Al3+', E['Al'])
    OutStr += '{:>11s}:    {:<1.3f}\n'.format('Cr3+', E['Cr'])
    OutStr += '{:>11s}:    {:<1.3f}\n'.format('V3+', E['V'])
    OutStr += '{:>11s}:    {:<1.3f}\n'.format('Fe2+', Fe2)
    OutStr += '{:>11s}:    {:<1.3f}\n'.format('Fe3+', Fe3)
    OutStr += '{:>11s}:    {:<1.3f}\n'.format('Total occ', B)
    OutStr += '{:>11s}:    {:<1.3f}\n'.format('Charge', BCharge)
    OutStr += '\n'
    OutStr += 'Cations per 4 oxygens:\n'
    OutStr += '{:>11s}:    {:<10s}\n'.format('Element', '#')
    for ElName in KnownElements:
        if ElName != 'O' and OriginalE[ElName] != 0:
            OutStr += '{:>11s}:    {:<1.3f}\n'.format(ElName, OriginalE[ElName])
    OutStr += '\n'
    OutStr += '{:>11s}:    {:<1.3f}\n'.format('Sum Cations', OriginalTotalCations)
    OutStr += 'Fe3+/sum(Fe) =  {:.3f}\n'.format(Fe3/(FeA+Fe2+Fe3))
    OutStr += 'Note, the cations have been set to 3 so the occupancy should be perfect.  Sum cations is the original sum for evaluating the quality of the fit.\n'
    OutStr += '\n'



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

