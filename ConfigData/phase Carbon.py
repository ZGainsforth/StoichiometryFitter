
__author__ = 'Zack Gainsforth'
__copyright__ = 'Copyright 2017, Zack Gainsforth'
__email__ = 'zsg@gainsforth.com'

from numpy import *
if __name__ != '__main__':
    import PhysicsBasics as pb


def AnalyzePhase(AtPct=None, WtPct=None, OxWtPct=None, OByStoich=None):
    """ Carbon analysis
    """

    #Normalize our AtPct vector.
    AtPct = AtPct/sum(AtPct)*100

    # We output an output string which contains the analysis.
    OutStr = '--- Carbon Analysis ---\n\n'

    # This analysis only knows about these elements:
    KnownElements = ['O', 'C', 'S', 'N', 'Si']

    # If anything else accounts for more than 2 At % then this analysis is garbage
    OtherCations = 0
    for Zsub, ElAtPct in enumerate(AtPct):
        # If this is an unknown cation, and it has any abundance, add it to our cumulative abundance of unknowns.
        if ElAtPct > 0 and pb.ElementalSymbols[Zsub+1] not in KnownElements:
            OtherCations += ElAtPct

    if OtherCations > 20:
        OutStr += 'More than 10% of the atomic abundance is comprised by atoms other than: ' + ' '.join(KnownElements) + '.'
        OutStr += '\nCannot analyze.'
        return OutStr

    # Report elemental ratios.
    OutStr += 'C/O = %0.3f\n' % (AtPct[pb.C-1]/AtPct[pb.O-1])
    OutStr += 'C/N = %0.3f\n' % (AtPct[pb.C-1]/AtPct[pb.N-1])
    OutStr += 'O/S = %0.3f\n' % (AtPct[pb.O-1]/AtPct[pb.S-1])
    OutStr += 'O/Si = %0.3f\n' % (AtPct[pb.O-1]/AtPct[pb.Si-1])

    return OutStr

if __name__ == '__main__':

    import imp
    pb = imp.load_source('PhysicsBasics', '../PhysicsBasics.py')
