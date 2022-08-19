
__author__ = 'Zack Gainsforth'
__copyright__ = 'Copyright 2017, Zack Gainsforth'
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
    OutStr = '--- Feldspar Analysis ---\n\n'

    # This analysis only knows about these elements:
    KnownElements = ['O', 'Na', 'Al', 'Si', 'K', 'Ca', 'Mg', 'Fe', 'P', 'S', 'Mn']

    # If anything else accounts for more than 2 At % then this analysis is garbage
    OtherCations = 0
    for Zsub, ElAtPct in enumerate(AtPct):
        # If this is an unknown cation, and it has any abundance, add it to our cumulative abundance of unknowns.
        if ElAtPct > 0 and pb.ElementalSymbols[Zsub+1] not in KnownElements:
            OtherCations += ElAtPct

    if OtherCations > 2:
        OutStr += 'More than 2% of the atomic abundance is comprised by atoms other than: ' + ' '.join(KnownElements) + '.'
        OutStr += '\nRemaining analysis is dubious.\n\n'
        #return OutStr

    # If the cation/O ratio is off by more than 2%, then we can't analyze it.
    if (abs(AtPct[pb.O-1] - 8/13*100) > 2) or (abs((sum(AtPct)-AtPct[pb.O-1]) - 5/13*100) > 2):
        OutStr += 'Cation/Anion ratio is not within 2% of feldspar.'
        OutStr += '\nRemaining analysis is dubious.\n\n'
        #return OutStr

    E = dict()

    # We already did stoichiometry so cations/8 oxy can be ratioed against the O exactly.
    for Element in KnownElements:
        E[Element] = eval('AtPct[pb.%s-1]/AtPct[pb.O-1]*8'%Element)

    # Compute how many cations in the M sites.
    M = sum(array([e for e in list(E.values())])) - E['O'] - E['Si'] - E['Al']

    # Report the AnAbOr numbers.
    OutStr += 'Ca/(Ca+Na+K) = %0.3f (An#)\n' % (E['Ca']/(E['Ca']+E['Na']+E['K']))
    OutStr += 'Na/(Ca+Na+K) = %0.3f (Ab#)\n' % (E['Na']/(E['Ca']+E['Na']+E['K']))
    OutStr += 'K/(Ca+Na+K) = %0.3f (Or#)\n' % (E['K']/(E['Ca']+E['Na']+E['K']))
    OutStr += '\nT sites:\n'
    OutStr += 'Al/(Al+Si) = %0.3f\n' % (E['Al'] / (E['Al'] + E['Si']))
    OutStr += 'Si/(Al+Si) = %0.3f\n' % (E['Si'] / (E['Al'] + E['Si']))
    OutStr += '\nT/M = %0.3f (should be 4)\n' % ((E['Al'] + E['Si']) / (E['Ca'] + E['Na'] + E['K']))

    OutStr += '\n'
    OutStr += 'Cations per 8 oxygens:\n'
    OutStr += '{:>11s}:    {:<10s}\n'.format('Element', '#')
    CationSum = 0
    for ElName in KnownElements:
        if ElName != 'O' and E[ElName] != 0:
            CationSum += E[ElName]
            if E[ElName] < 0.01:
                # Handle ppm levels gracefully.
                OutStr += '{:>11s}:    {:<1.3f}'.format(ElName, E[ElName])
                OutStr += ', {:>11s}:    {:<4.0f} * 10^-6\n'.format(ElName, E[ElName]*1e6)
            else:
                OutStr += '{:>11s}:    {:<1.3f}\n'.format(ElName, E[ElName])
    OutStr += '{:>11s}:    {:<1.3f}\n'.format('Total Cats', CationSum)
    OutStr += 'Ideal number of cats is 5.'


    return OutStr

if __name__ == '__main__':

    import imp
    pb = imp.load_source('PhysicsBasics', '../PhysicsBasics.py')

    AtPct = zeros(pb.MAXELEMENT)
    AtPct[pb.O-1] = 8/13*100
    AtPct[pb.Ca-1] = 1/13*100
    AtPct[pb.Al-1] = 2/13*100
    AtPct[pb.Si-1] = 2/13*100
    print('\n\n-----------------------\n\n')
    print('Anorthite: Ca Al2 Si2 O8:\n')
    print(AnalyzePhase(AtPct))

    AtPct = zeros(pb.MAXELEMENT)
    AtPct[pb.O-1] = 8/13*100
    AtPct[pb.Na-1] = 1/13*100
    AtPct[pb.Al-1] = 1/13*100
    AtPct[pb.Si-1] = 3/13*100
    print('\n\n-----------------------\n\n')
    print('Albite: Ca Al Si3 O8:\n')
    print(AnalyzePhase(AtPct))

    AtPct = zeros(pb.MAXELEMENT)
    AtPct[pb.O-1] = 8/13*100
    AtPct[pb.K-1] = 1/13*100
    AtPct[pb.Al-1] = 1/13*100
    AtPct[pb.Si-1] = 3/13*100
    print('\n\n-----------------------\n\n')
    print('Orthoclase: K Al Si3 O8:\n')
    print(AnalyzePhase(AtPct))

    AtPct = zeros(pb.MAXELEMENT)
    AtPct[pb.O-1] = 61.34
    AtPct[pb.K - 1] = 6.78
    AtPct[pb.Na - 1] = 0.64
    AtPct[pb.Al-1] = 7.92
    AtPct[pb.Si-1] = 22.88
    print('\n\n-----------------------\n\n')
    print('Lunar Sanidine: K Al Si3 O8:\n')
    print(AnalyzePhase(AtPct))
