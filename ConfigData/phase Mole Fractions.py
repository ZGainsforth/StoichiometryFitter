
__author__ = 'Zack Gainsforth'
__copyright__ = 'Copyright 2017, Zack Gainsforth'
__email__ = 'zsg@gainsforth.com'

from numpy import *
if __name__ != '__main__':
    import PhysicsBasics as pb
    from fractions import Fraction
    import CountsToQuant

def CatsPerNOxygens(AtPct, KnownElements, NOxygens):
    OutStr = ''
    E = dict()

    # We already did stoichiometry so cations/8 oxy can be ratioed against the O exactly.
    for Element in KnownElements:
        E[Element] = eval('AtPct[pb.%s-1]/AtPct[pb.O-1]*%d'%(Element, NOxygens))

    # Compute how many cations in the M sites.
    M = sum(array([e for e in list(E.values())])) - E['O']

    OutStr += '\n'
    OutStr += 'Cations per %d oxygens:\n'%NOxygens
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

    return OutStr

def GetOxideWeights(OByStoichiometry):

    # Get element masses (a vector for all elements, and the mass of O specifically.)
    M_el = array(pb.ElementalWeights[1:])
    M_O = pb.ElementalWeights[pb.O]

    # We only make oxides with positively charged cations.  The negs are transferred directly.
    PosCharges = OByStoichiometry.clip(min=0)
    # 1 means that we can multiply by this vector to extract the elements that are not stoichometrically tied to O.
    NegMask = (OByStoichiometry <= 0).astype(float)

    # Using the stoichiometries entered in, the number of cations and oxygens are determined by the ratio of the cation charge to oxygen's charge of 2.
    NumCats = array([Fraction(float(Charge)/2.).limit_denominator(10).denominator for Charge in PosCharges])
    NumOx = array([Fraction(float(Charge)/2.).limit_denominator(10).numerator for Charge in PosCharges])
    # Now compute the molecular weight of the oxide as the weight of the appropriate number of cations and oxygens.
    MolWt = M_el*NumCats + M_O*NumOx

    return MolWt, NumCats, NumOx

def AnalyzePhase(AtPct=None, WtPct=None, OxWtPct=None, OByStoich=None):
    """ Olivine analysis
    """

    OutStr = ''

    #Normalize our AtPct vector.
    AtPct = AtPct/sum(AtPct)*100

    # This analysis only knows about these elements:
    KnownElements = ['O', 'Na', 'Mg', 'Al', 'Si', 'P', 'S', 'K', 'Ca', 'Ti', 'V', 'Cr', 'Mn', 'Fe', 'Ni']

    # Report oxide mole fractions
    if OByStoich is not None:
        OutStr += '\n--- Mole fractions of oxides Analysis ---\n'

        OxWt, NumCats, NumOx = GetOxideWeights(OByStoich)

        E = dict()

        # Compute the mol fractions: just the oxide weight % / oxide weights.
        for Element in KnownElements:
            E[Element] = eval('OxWtPct[pb.%s-1]/OxWt[pb.%s-1]'%(Element, Element))
        print(E)

        # Renormalize
        MolFracNorm = sum(array([e for e in list(E.values())])) - E['O']

        # Sidecheck.
        SumMolFrac = 0

        OutStr += '\n{:>11s}:    {:<10s}\n'.format('Element', '#')
        for ElName in KnownElements:
            if ElName != 'O' and E[ElName] != 0:
                # Make a string for how many cations in the oxide formula
                NCats = eval('NumCats[pb.%s-1]'%ElName)
                if NCats == 1:
                    NCats = ''
                else:
                    NCats =  '%d'%NCats
                # And oxygen
                NOx = eval('NumOx[pb.%s-1]'%ElName)
                if NOx == 1:
                    NOx = ''
                else:
                    NOx =  '%d'%NOx
                # Finally, the oxide name
                OxideName = '%s%sO%s'%(ElName, NCats, NOx)
                OutStr += '{:>11s}:    {:<1.3f}\n'.format(OxideName, E[ElName]/MolFracNorm)
                SumMolFrac += E[ElName]/MolFracNorm
        OutStr += '{:>11s}:    {:<1.3f}\n'.format('Sum:', SumMolFrac)

    # Report number of cations per various numbers of oxygens.
    OutStr += '\n--- Cations per N oxygens Analysis ---\n'

    OutStr += CatsPerNOxygens(AtPct, KnownElements, 4)
    OutStr += CatsPerNOxygens(AtPct, KnownElements, 6)
    OutStr += CatsPerNOxygens(AtPct, KnownElements, 8)
    OutStr += CatsPerNOxygens(AtPct, KnownElements, 10)
    OutStr += CatsPerNOxygens(AtPct, KnownElements, 18)

    return OutStr

if __name__ == '__main__':

    import imp
    pb = imp.load_source('PhysicsBasics', '../PhysicsBasics.py')

    AtPct = zeros(pb.MAXELEMENT)
    AtPct[pb.O-1] = 60.999
    AtPct[pb.Na-1] = 0.313
    AtPct[pb.Mg-1] = 15.163
    AtPct[pb.Al-1] = 0.814
    AtPct[pb.Si-1] = 20.453
    AtPct[pb.Ca-1] = 0.578
    AtPct[pb.Ti-1] = 0.0083
    AtPct[pb.Fe-1] = 4.244
    print('\n\n-----------------------\n\n')
    print('Pyroxene En75Fs20Wo3\n')
    print(AnalyzePhase(AtPct))

