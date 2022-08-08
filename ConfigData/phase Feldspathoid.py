
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
    AtPct = AtPct/sum(AtPct)*100.

    # We output an output string which contains the analysis.
    OutStr = '--- Nepheline Analysis ---\n\n'

    # This analysis only knows about these elements:
    KnownElements = ['O', 'Na', 'Al', 'Si', 'K', 'Ca', 'Mg', 'Mn', 'Fe']

    # If anything else accounts for more than 2 At % then this analysis is garbage
    OtherCations = 0
    for Zsub, ElAtPct in enumerate(AtPct):
        # If this is an unknown cation, and it has any abundance, add it to our cumulative abundance of unknowns.
        if ElAtPct > 0 and pb.ElementalSymbols[Zsub+1] not in KnownElements:
            OtherCations += ElAtPct

    if OtherCations > 2.:
        OutStr += 'More than 2% of the atomic abundance is comprised by atoms other than: ' + ' '.join(KnownElements) + '.'
        OutStr += '\nRemaining analysis is dubious.\n'
        #return OutStr

    # If the cation/O ratio is off by more than 2% outside of the window 11/32 to 12/32, then we can't analyze it.
    # Oxygen should be between 16/28 and 16/27 because Barth nepheline can have vacancies.
    if (AtPct[pb.O-1] < (16./28*100. - 2)) or (AtPct[pb.O-1] > (16./27*100. + 2)):
        OutStr += 'Cation/Anion ratio is not within 2% of Nepheline-Kalsilite.'
        OutStr += '\nRemaining analysis is dubious.\n'
        #return OutStr

    E = dict()

    # We already did stoichiometry so cations/32 oxy can be ratioed against the O exactly.
    for Element in KnownElements:
        E[Element] = eval('AtPct[pb.%s-1]/AtPct[pb.O-1]*32.'%Element)

    # import pdb; pdb.set_trace()

    # Stoichiometry calculation based on Nepheline solid solution compositions:  stoichiometry revisited, reviewed, clarified and rationalized (2020). C. Michael B. Henderson, Mineralogical Magazine, 84, 813-838, doi:10.1180/mgm.2020.78

    # Compute Excess silicon (Equation 1 from ref.)
    ExcessSi = E['Si'] - E['Na'] - E['K'] - 2*E['Ca']

    Qz = (24 - 3*E['Na'] - 3*E['K'] - 6*E['Ca']) * 100/24 # Vacancy-quartz component.
    Ne = 3*E['Na'] * 100/24 # Nepheline component.
    Ks = 3*E['K'] * 100/24 # Kalsilite component.
    CaNe = 6*E['Ca'] * 100/24 # Vacancy-Anorthite component.
    KsM = 6*(E['Mg']+E['Mn']+E['Fe']) * 100/24 # Kalsilite-impurity component.

    # Report the component numbers.
    OutStr += '\nM sites:\n'
    OutStr += 'Na2 Al2 Si2 O8 = %0.3f (Ne#)\n' % (Ne)
    OutStr += 'K2 Al2 Si2 O8 = %0.3f (Ks#)\n' % (Ks)
    OutStr += 'Vac Ca Al2 Si2 O8 = %0.3f (CaNe#)\n' % (CaNe)
    OutStr += 'Vac2 Si4 O8 = %0.3f (Qz#)\n' % (Qz)
    OutStr += 'K2 M1 Si3 O8 = %0.3f (KsM# M = 2+ cation: Mg, Fe2+, Mn)\n' % (KsM)
    OutStr += 'Filled M Sites (based on 32 O) = %0.3f (should be 8 without vacancies).\n' % (E['Na'] + E['K'])
    OutStr += '\nT sites:\n'
    OutStr += 'Al/(Al+Si+Mg+Mn+Fe) = %0.3f\n' % (E['Al'] / (E['Al'] + E['Si'] + E['Mg'] + E['Mn'] + E['Fe']))
    OutStr += 'Si/(Al+Si+Mg+Mn+Fe) = %0.3f\n' % (E['Si'] / (E['Al'] + E['Si'] + E['Mg'] + E['Mn'] + E['Fe']))
    OutStr += 'Si/Al = %0.3f\n' % (E['Si'] / E['Al'])
    OutStr += 'Filled T Sites (based on 32 O) = %0.3f (should be 16).\n' % (E['Al'] + E['Si'] + E['Mg'] + E['Mn'] + E['Fe'])

    OutStr += '\n'
    OutStr += 'Cations per 32 oxygens:\n'
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
    OutStr += 'Ideal number of cats is 24 (without vacancies).\n\n'
    OutStr += 'Ref: Stoichiometry calculation based on Nepheline solid solution compositions:  stoichiometry revisited, reviewed, clarified and rationalized (2020). C. Michael B. Henderson, Mineralogical Magazine, 84, 813-838, doi:10.1180/mgm.2020.78'


    return OutStr

if __name__ == '__main__':

    import imp
    pb = imp.load_source('PhysicsBasics', '../PhysicsBasics.py')
    # import pdb; pdb.set_trace()

    AtPct = zeros(pb.MAXELEMENT)
    AtPct[pb.K-1] = 1/28*100
    AtPct[pb.Na-1] = 3/28*100
    AtPct[pb.Al-1] = 4/28*100
    AtPct[pb.Si-1] = 4/28*100
    AtPct[pb.O-1] = 16/28*100
    print('\n\n-----------------------\n\n')
    print('Nepheline: K Na3 Al4 Si4 O16:\n')
    print(AnalyzePhase(AtPct))

    AtPct = zeros(pb.MAXELEMENT)
    AtPct[pb.K-1] = 4/28*100
    AtPct[pb.Al-1] = 4/28*100
    AtPct[pb.Si-1] = 4/28*100
    AtPct[pb.O-1] = 16/28*100
    print('\n\n-----------------------\n\n')
    print('Kalsilite: K4 Al4 Si4 O16:\n')
    print(AnalyzePhase(AtPct))

    AtPct = zeros(pb.MAXELEMENT)
    AtPct[pb.K-1] = 0/28*100
    AtPct[pb.Na-1] = 3/28*100
    AtPct[pb.Al-1] = 3/28*100
    AtPct[pb.Si-1] = 5/28*100
    AtPct[pb.O-1] = 16/28*100
    print('\n\n-----------------------\n\n')
    print('Barth Nepheline: Na3 Al3 Si5 O16:\n')
    print(AnalyzePhase(AtPct))

    AtPct = zeros(pb.MAXELEMENT)
    AtPct[pb.Ca-1] = 1.447
    AtPct[pb.Na-1] = 11.581
    AtPct[pb.Al-1] = 14.482 
    AtPct[pb.Si-1] = 14.510
    AtPct[pb.O-1] = 57.980
    print('\n\n-----------------------\n\n')
    print('80Ne20An (from Henderson ref):\n')
    print(AnalyzePhase(AtPct))

    AtPct = zeros(pb.MAXELEMENT)
    AtPct[pb.Ca-1] = 1.516
    AtPct[pb.Na-1] = 7.578
    AtPct[pb.Al-1] = 10.604 
    AtPct[pb.Si-1] = 19.696
    AtPct[pb.O-1] = 60.605
    print('\n\n-----------------------\n\n')
    print('50Ne20An30Q (from Henderson ref):\n')
    print(AnalyzePhase(AtPct))

    AtPct = zeros(pb.MAXELEMENT)
    AtPct[pb.K-1] = 1.519
    AtPct[pb.Na-1] = 8.571
    AtPct[pb.Mg-1] = 0.177
    AtPct[pb.Al-1] = 13.415
    AtPct[pb.Si-1] = 16.992
    AtPct[pb.O-1] = 59.327
    print('\n\n-----------------------\n\n')
    print('Track 220 TP5 Nepheline:\n')
    print(AnalyzePhase(AtPct))
