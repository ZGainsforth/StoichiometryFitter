from __future__ import division
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
    OutStr = '--- Apatite Analysis ---\n\n'

    # This analysis only knows about these elements:
    KnownElements = ['H', 'O', 'P', 'Ca', 'F', 'Cl', 'Na', 'Mn']

    # If anything else accounts for more than 2 At % then this analysis is garbage
    OtherCations = 0
    for Zsub, ElAtPct in enumerate(AtPct):
        # If this is an unknown cation, and it has any abundance, add it to our cumulative abundance of unknowns.
        if ElAtPct > 0 and pb.ElementalSymbols[Zsub+1] not in KnownElements:
            OtherCations += ElAtPct

    if OtherCations > 2:
        OutStr += 'More than 2% of the atomic abundance is comprised by atoms other than: ' + ' '.join(KnownElements) + '.'
        OutStr += '\nAnalysis will likely be in error.\n\n'
        # return OutStr

    # If the cation/O ratio is off by more than 2%, then we can't analyze it.
    # The range of valid O values is between 57 and 59 At %
    ErrMargin = 5.0
    if (AtPct[pb.O-1] < (57.0-ErrMargin)) or (AtPct[pb.O-1] > (59.0+ErrMargin)):
        OutStr += 'Oxygen is {:1.3f} which is not within {:g}% of the range 57-59 At%.'.format(AtPct[pb.O-1], ErrMargin)
        OutStr += '\nAnalysis will likely be in error.\n\n'
        # return OutStr

    # If the Ca/P ratio is off by more than 2%, then we can't analyze it.
    CaPRatio = AtPct[pb.Ca-1]/AtPct[pb.P-1]
    if (abs(CaPRatio - 10.0/6.0)*100 > 2):
        OutStr += 'Ca/P ratio is {:1.3f} which is not within 2% of 10/6 = 1.666.'.format(CaPRatio)
        OutStr += '\nAnalysis will likely be in error.\n\n'
        # return OutStr

    E = dict()

    # Because O varies in apatite, we won't normalize against it.  The most accurate element is probably Ca.
    # So, everything is ratioed to 10 Ca.
    for Element in KnownElements:
        E[Element] = eval('AtPct[pb.%s-1]/AtPct[pb.Ca-1]*10'%Element)

    # Calculate the OH/F/Cl site.
    # There are 2 OH/F/Cl sites for 10 Ca.
    # We can't measure H so we must infer it from F and Cl.
    E['H'] = 0.0
    E['H'] = 2 - (E['F'] + E['Cl'])
    # Handle the situation that the input quant is doesn't add up to a valid solid solution.
    if E['H'] < -0.1:
        print('Warning: Computed H is negative by more than 1/10 site.  Quants may be in error.\n')
    if E['H'] > 2.1:
        print('Warning: Hydrogen is more abundant than allowed by > 1/10 site.  Quants may be in error.  Assuming 2 H.\n')
        E['H'] = 2
    # And ignore rounding errors.
    if E['H'] < 1e-9:
        E['H'] = 0
    Ap = E['H'] / (E['H'] + E['F'] + E['Cl']) * 100
    Fl = E['F'] / (E['H'] + E['F'] + E['Cl']) * 100
    Chl = E['Cl'] / (E['H'] + E['F'] + E['Cl']) * 100
    # Report the solid solution.
    OutStr += 'X site solid solution: \n'.format('Element', '#')
    OutStr += '{:>11s}:    {:<1.0f}\n'.format('Ap', Ap)
    OutStr += '{:>11s}:    {:<1.0f}\n'.format('Fl', Fl)
    OutStr += '{:>11s}:    {:<1.0f}\n'.format('Chl', Chl)

    # OriginalE is the unnormalized vector of elements so we can do cation sums.
    OriginalE = E.copy()

    OutStr += '\n'
    OutStr += 'Element per 10 Ca:\n'
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
    OutStr += '{:>11s}:    {:<1.3f}\n'.format('Total Atoms', CationSum)


    return OutStr, None
    
if __name__ == '__main__':

    import imp
    pb = imp.load_source('PhysicsBasics', '../PhysicsBasics.py')

    AtPct = zeros(pb.MAXELEMENT)
    AtPct[pb.H-1] = 2/44*100
    AtPct[pb.O-1] = 26/44*100
    AtPct[pb.P-1] = 6/44*100
    AtPct[pb.Ca-1] = 10/44*100
    print('Hydroxypatite: Ca10 (PO4)6 (OH)2:\n')
    print(AnalyzePhase(AtPct))

    AtPct = zeros(pb.MAXELEMENT)
    AtPct[pb.F-1] = 2/42*100
    AtPct[pb.O-1] = 24/42*100
    AtPct[pb.P-1] = 6/42*100
    AtPct[pb.Ca-1] = 10/42*100
    print('Fluorapatite: Ca10 (PO4)6 F2:\n')
    print(AnalyzePhase(AtPct))

    AtPct = zeros(pb.MAXELEMENT)
    AtPct[pb.Cl-1] = 2/42*100
    AtPct[pb.O-1] = 24/42*100
    AtPct[pb.P-1] = 6/42*100
    AtPct[pb.Ca-1] = 10/42*100
    print('Chlorapatite: Ca10 (PO4)6 Cl2:\n')
    print(AnalyzePhase(AtPct))

    AtPct = zeros(pb.MAXELEMENT)
    AtPct[pb.F-1] = 1/43*100
    AtPct[pb.O-1] = 25/43*100
    AtPct[pb.P-1] = 6/43*100
    AtPct[pb.Ca-1] = 10/43*100
    print('Fluorapatite-apatite: Ca10 (PO4)6 F(OH):\n')
    print(AnalyzePhase(AtPct))

    AtPct = zeros(pb.MAXELEMENT)
    AtPct[pb.F-1] = 1/42*100
    AtPct[pb.Cl-1] = 1/42*100
    AtPct[pb.O-1] = 24/42*100
    AtPct[pb.P-1] = 6/42*100
    AtPct[pb.Ca-1] = 10/42*100
    print('Chlorofluorapatite: Ca10 (PO4)6 FCl:\n')
    print(AnalyzePhase(AtPct))

    AtPct = zeros(pb.MAXELEMENT)
    AtPct[pb.Cl-1] = 3/42*100
    AtPct[pb.O-1] = 24/42*100
    AtPct[pb.P-1] = 6/42*100
    AtPct[pb.Ca-1] = 10/42*100
    print('Chlorapatite: Ca10 (PO4)6 Cl3 (invalid):\n')
    print(AnalyzePhase(AtPct))

