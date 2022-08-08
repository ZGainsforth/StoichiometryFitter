
__author__ = 'Zack Gainsforth'
__copyright__ = 'Copyright 2014, Zack Gainsforth'
__email__ = 'zsg@gainsforth.com'

from numpy import *
if __name__ != '__main__':
    import PhysicsBasics as pb


def AnalyzePhase(AtPct=None, WtPct=None, OxWtPct=None, OByStoich=None):
    """ Olivine analysis
    """

    #Normalize our AtPct vector.
    AtPct = AtPct/sum(AtPct)*100

    # We output an output string which contains the analysis.
    OutStr = '--- Olivine Analysis ---\n\n'

    # This analysis only knows about these elements:
    KnownElements = ['O', 'Na', 'Mg', 'Al', 'Si', 'Ca', 'Ti', 'Cr', 'Mn', 'Fe', 'Ni']

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

    # This is supposed to be cations/4oxy.  But this is actually cation/7atoms.
    # for Element in KnownElements:
    #     E[Element] = eval('AtPct[pb.%s-1]/100*7'%Element)

    # We already did stoichiometry so cations/4 oxy can be ratioed against the O exactly.
    for Element in KnownElements:
        E[Element] = eval('AtPct[pb.%s-1]/AtPct[pb.O-1]*4'%Element)

    # OriginalE is the unnormalized vector of elements so we can do cation sums.
    OriginalE = E.copy()

    # Compute how many cations in the M2 + M2 sites.
    M1M2 = sum(array([e for e in list(E.values())])) - E['O'] - E['Si']

    # Report the Fo type stuff.
    OutStr += 'Mg/(Mg+Fe) = %0.3f\n' % (E['Mg']/(E['Mg']+E['Fe']))
    for e in KnownElements:
        if e in ['O', 'Si']:
            continue
        if E[e] != 0:
            OutStr += e + '/(M1+M2) = %0.3f\n' % (E[e]/M1M2)

    OutStr += '\n'
    OutStr += 'Cations per 4 oxygens:\n'
    OutStr += '{:>11s}:    {:<10s}\n'.format('Element', '#')
    CationSum = 0
    for ElName in KnownElements:
        if ElName != 'O' and OriginalE[ElName] != 0:
            CationSum += OriginalE[ElName]
            if OriginalE[ElName] < 0.01:
                # Handle ppm levels gracefully.
                OutStr += '{:>11s}:    {:<1.3f}'.format(ElName, OriginalE[ElName])
                OutStr += ', {:>11s}:    {:<4.0f} * 10^-6\n'.format(ElName, OriginalE[ElName]*1e6)
            else:
                OutStr += '{:>11s}:    {:<1.3f}\n'.format(ElName, OriginalE[ElName])
    OutStr += '{:>11s}:    {:<1.3f}\n'.format('Total Cats', CationSum)


    return OutStr
    
if __name__ == '__main__':

    import imp
    pb = imp.load_source('PhysicsBasics', '../PhysicsBasics.py')

    AtPct = zeros(pb.MAXELEMENT)
    AtPct[pb.O-1] = 4/7*100
    AtPct[pb.Mg-1] = 2/7*100
    AtPct[pb.Si-1] = 1/7*100
    print('Forsterite: Mg2 Si O4:\n')
    print(AnalyzePhase(AtPct))

    AtPct = zeros(pb.MAXELEMENT)
    AtPct[pb.O-1] = 4/7*100
    AtPct[pb.Fe-1] = 2/7*100
    AtPct[pb.Si-1] = 1/7*100
    print('Fayalite: Fe2 Si O4:\n')
    print(AnalyzePhase(AtPct))

    AtPct = zeros(pb.MAXELEMENT)
    AtPct[pb.O-1] =  57.135
    AtPct[pb.Si-1] = 14.273
    AtPct[pb.Mg-1] = 24.825
    AtPct[pb.Fe-1] = 3.544
    AtPct[pb.Mn-1] = 0.057
    AtPct[pb.Ca-1] = 0.091
    AtPct[pb.Ni-1] = 0.074
    print('UC Fo87:\n')
    print(AnalyzePhase(AtPct))

