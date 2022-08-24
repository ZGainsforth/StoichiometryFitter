
__author__ = 'Zack Gainsforth'
__copyright__ = 'Copyright 2014, Zack Gainsforth'
__email__ = 'zsg@gainsforth.com'

from numpy import *
if __name__ != '__main__':
    import PhysicsBasics as pb


def AnalyzePhase(AtPct=None, WtPct=None, OxWtPct=None, OByStoich=None):
    """ Serpentine analysis
    """

    # H is invisible so infer how much H based on 5 oxy and 4 OH.
    AtPct = array(AtPct)
    AtPct[pb.H-1] = AtPct[pb.O-1]*4/9

    #Normalize our AtPct vector.
    AtPct = AtPct/sum(AtPct)*100

    # We output an output string which contains the analysis.
    OutStr = '--- Serpentine Analysis ---\n\n'

    # This analysis only knows about these elements:
    KnownElements = ['H', 'O', 'Na', 'Mg', 'Al', 'Si', 'Ca', 'Ti', 'Cr', 'Mn', 'Fe', 'Ni']

    # Define which atoms are supposed to go in octahedral and tetrahedral sites.
    OctahedralAtoms = ['Na', 'Mg', 'Ca', 'Ti', 'Cr', 'Mn', 'Fe', 'Ni']
    TetrahedralAtoms = ['Al', 'Si']

    # # If anything else accounts for more than 5 At % then this analysis is garbage
    # OtherCations = 0
    # for Zsub, ElAtPct in enumerate(AtPct):
    #     # If this is an unknown cation, and it has any abundance, add it to our cumulative abundance of unknowns.
    #     if ElAtPct > 0 and pb.ElementalSymbols[Zsub+1] not in KnownElements:
    #         OtherCations += ElAtPct

    # if OtherCations > 2:
    #     OutStr += 'More than 2% of the atomic abundance is comprised by atoms other than: ' + ' '.join(KnownElements) + '.'
    #     OutStr += '\nCannot analyze.'
    #     return OutStr

    # # If the cation/O ratio is off by more than 2%, then we can't analyze it.
    # if (abs(AtPct[pb.O-1] - 4/7*100) > 2) or (abs((sum(AtPct)-AtPct[pb.O-1]) - 3/7*100) > 2):
    #     OutStr += 'Cation/Anion ratio is not within 2% of 3/4.'
    #     OutStr += '\nCannot analyze.'
    #     return OutStr

    E = dict()

    # This is supposed to be cations/4oxy.  But this is actually cation/7atoms.
    # for Element in KnownElements:
    #     E[Element] = eval('AtPct[pb.%s-1]/100*7'%Element)

    # We already did stoichiometry so cations/9 oxy can be ratioed against the O exactly.
    for Element in KnownElements:
        E[Element] = eval('AtPct[pb.%s-1]/AtPct[pb.O-1]*9'%Element)

    # OriginalE is the unnormalized vector of elements so we can do cation sums.
    OriginalE = E.copy()

    # Compute how many cations in the Oct sites.
    Oct = sum(array([e for e in list(E.values())])) - E['O'] - E['H'] - E['Si'] - E['Al']

    # Tet should be Si and Al.
    Tet = E['Si'] - E['Al']

    # Report the Fo type stuff.
    OutStr += 'Mg/(Mg+Fe) = %0.3f\n' % (E['Mg']/(E['Mg']+E['Fe']))
    OutStr += 'Al/(Al+Si) = %0.3f\n' % (E['Al']/(E['Al']+E['Si']))
    for e in KnownElements:
        if e in ['H', 'O', 'Si', 'Al']:
            continue
        if E[e] != 0:
            OutStr += e + '/(Octahedral) = %0.3f\n' % (E[e]/Oct)

    OutStr += '\n'
    OutStr += 'Octahedral atoms per 18 atoms:\n'
    OutStr += '{:>11s}:    {:<10s}\n'.format('Element', '#')
    CationSum = 0
    for ElName in KnownElements:
        if (ElName in OctahedralAtoms) and (OriginalE[ElName] != 0):
            CationSum += OriginalE[ElName]
            if OriginalE[ElName] < 0.01:
                # Handle ppm levels gracefully.
                OutStr += '{:>11s}:    {:<1.3f}'.format(ElName, OriginalE[ElName])
                OutStr += ', {:>11s}:    {:<4.0f} * 10^-6\n'.format(ElName, OriginalE[ElName]*1e6)
            else:
                OutStr += '{:>11s}:    {:<1.3f}\n'.format(ElName, OriginalE[ElName])
    OutStr += '{:>11s}:    {:<1.3f}\n'.format('Total Cats', CationSum)
    OutStr += 'Serpentine formula should have 3 octahedral atoms.\n'

    OutStr += '\n'
    OutStr += 'Tetrahedral atoms per 18 atoms:\n'
    OutStr += '{:>11s}:    {:<10s}\n'.format('Element', '#')
    CationSum = 0
    for ElName in KnownElements:
        if (ElName in TetrahedralAtoms) and (OriginalE[ElName] != 0):
            CationSum += OriginalE[ElName]
            if OriginalE[ElName] < 0.01:
                # Handle ppm levels gracefully.
                OutStr += '{:>11s}:    {:<1.3f}'.format(ElName, OriginalE[ElName])
                OutStr += ', {:>11s}:    {:<4.0f} * 10^-6\n'.format(ElName, OriginalE[ElName]*1e6)
            else:
                OutStr += '{:>11s}:    {:<1.3f}\n'.format(ElName, OriginalE[ElName])
    OutStr += '{:>11s}:    {:<1.3f}\n'.format('Total Cats', CationSum)
    OutStr += 'Serpentine formula should have 2 tetrahedral atoms.\n'

    OutStr += '\n'
    OutStr += 'Atoms per 18 atoms:\n'
    OutStr += '{:>11s}:    {:<10s}\n'.format('Element', '#')
    CationSum = 0
    for ElName in KnownElements:
        if OriginalE[ElName] != 0:
            CationSum += OriginalE[ElName]
            if OriginalE[ElName] < 0.01:
                # Handle ppm levels gracefully.
                OutStr += '{:>11s}:    {:<1.3f}'.format(ElName, OriginalE[ElName])
                OutStr += ', {:>11s}:    {:<4.0f} * 10^-6\n'.format(ElName, OriginalE[ElName]*1e6)
            else:
                OutStr += '{:>11s}:    {:<1.3f}\n'.format(ElName, OriginalE[ElName])
    OutStr += '{:>11s}:    {:<1.3f}\n'.format('Total Cats', CationSum)
    OutStr += 'Serpentine formula is Oct3 Tet2 O9 H4\n'
    OutStr += 'Serpentine formula is Oct3 Tet2 O5 OH4\n'
    OutStr += 'Tet is Al or Si, occasionally Fe can be included (not considered here)\n'
    OutStr += 'All other cations go in the octahedral sites.\n'

    return OutStr
    
if __name__ == '__main__':

    import imp
    pb = imp.load_source('PhysicsBasics', '../PhysicsBasics.py')

    AtPct = zeros(pb.MAXELEMENT)
    AtPct[pb.H-1] = 4
    AtPct[pb.O-1] = 9
    AtPct[pb.Mg-1] = 3
    AtPct[pb.Si-1] = 2
    print('Serpentine: Mg3 Si2 O5 (OH)4:\n')
    print(AnalyzePhase(AtPct))

