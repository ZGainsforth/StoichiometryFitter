
__author__ = 'Zack Gainsforth'
__copyright__ = 'Copyright 2014, Zack Gainsforth'
__email__ = 'zsg@gainsforth.com'

from numpy import *
if __name__ != '__main__':
    import PhysicsBasics as pb
from PhaseFit import FitPhases
from collections import OrderedDict

def ComputeCp(T, PhaseName):
    # The values are from Ghiorso & Sack 1991 Thermochemistry of the Oxide Minerals in the book Oxide Minerals: Petrologic and Magnetic Significance.  Table 10.
    # Delta Hf, S, k0, k1, k2, k3, Tlambda, l1 and l2
    PhaseConstants = array([('Chromite', -1445.490, 142.676, 236.874, -16.796, 0, -16.765, 0, 0, 0, 0),
                            ('Hercynite', -1947.681, 115.362, 235.190, -14.370, -46.913, 64.564, 0, 0, 0, 0),
                            ('Magnesioferrite', -1406.465, 122.765, 196.66, 0.0, -74.922, 81.007, 665, 15.236, -53.571, 931),
                            ('Magnesiotitanate', -2161.998, 120.170, 226.11, -13.801, -17.011, 4.128, 0, 0, 0, 0),
                            ('Magnetite', -1117.403, 146.114, 207.93, 0.0, -72.433, 66.436, 848, -19.502, 61.037, 1565),
                            ('Picochromite', -1783.640, 106.020, 201.981, -5.519, -57.844, -57.729, 0, 0, 0, 0),
                            ('Magnesiospinel', -2300.313, 84.535, 235.90, -17.666, -17.104, 4.062, 0, 0, 0, 0),
                            ('Ulvospinel', -1488.500, 185.447, 249.63, -18.174, 0.000, -5.453, 0, 0, 0, 0),
                            ], dtype = [('Mineral', 'S20'), ('DeltaHf0', 'f4'), ('S', 'f4'), ('k0', 'f4'), ('k1', 'f4'), ('k2', 'f4'), ('k3', 'f4'), ('Tlambda', 'f4'), ('l1', 'f4'), ('l2', 'f4'), ('DeltagH', 'f4')])

    # Scale DeltaH units to joules
    PhaseConstants['DeltaHf0'] *= 1000
    # Add exponenents on the constants.
    PhaseConstants['k1'] *= 10**-2
    PhaseConstants['k2'] *= 10**-5
    PhaseConstants['k3'] *= 10**-7
    PhaseConstants['l1'] *= 10**2
    PhaseConstants['l2'] *= 10**5

    # Get the thermodynamic constants for the phase we want to compute.
    V = PhaseConstants[PhaseConstants['Mineral'] == PhaseName]
    if len(V) != 1:
        print('Phase %s not one of the thermodynamic endmembers in the Ghiorso & Sack implementation.' % PhaseName)
        return

    print(V)
# TODO Implement Cp and Gf equations.
    return

def GetThermodynamicPropertiesForSpinel(AtPct):
    # First we have to fit it against the end-member spinel species from Sack and Ghiorso.

    # Make a quant array for PhaseFit.
    Quant = OrderedDict(list(zip(pb.ElementalSymbols[1:], list(zip(AtPct, AtPct)))))

    # We are using a bunch of them.  S&G use just five in MELTS, but we use them all.  Hopefully,
    # we can sort out site degeneracies!  Well, let's find out.
    PhaseArray = [['Chromite', 'Fe1 Cr2 O4'],
                  ['Hercynite', 'Fe1 Al2 O4'],
                  ['Magnesioferrite', 'Mg1 Fe2 O4'],
                  ['Magnesiotitanate', 'Ti1 Mg2 O4'],
                  ['Magnetite', 'Fe3 O4'],
                  ['Picochromite', 'Mg1 Cr2 O4'],
                  ['Magnesiospinel', 'Mg1 Al2 O4'],
                  ['Ulvospinel', 'Fe2 Ti1 O4']]

    (FitResult, Residual, FitComposition) = FitPhases(Quant, PhaseArray)
    #print(FitResult)

    # Make a temperatures vector
    T = linspace(298, 2000, 2000-298)
    ComputeCp(T, 'Hercynite')

    return


def AnalyzePhase(AtPct=None, WtPct=None, OxWtPct=None, OByStoich=None):
    """ Assume an "ideal" spinel...
    """

    #Normalize our AtPct vector.
    AtPct = AtPct/sum(AtPct)*100

    # This isn't fully implemented yet.  Intention is to compute free energies for spinel at some point based on Sack & Ghiorso.
    GetThermodynamicPropertiesForSpinel(AtPct)

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

    # Fe splits the difference if it is present, filling up 3+ in B and 2+ in A.
    # So first we fill up A:

    
    if E['Fe'] > 0:
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

        # Finally compute the Fe3/Sum(Fe) ratio.
        Fe3OverSumFe = Fe3/(FeA+Fe2+Fe3)

    else:
        FeA = FeB = Fe2 = Fe3 = Fe3OverSumFe = 0

    OutStr += 'Site A (tetrahedral):\n'
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
    OutStr += 'Site B (octahedral):\n'
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
    OutStr += 'Fe3+/sum(Fe) =  {:.3f}\n'.format(Fe3OverSumFe)
    OutStr += 'Note, the cations should ideally be 3 for spinel.\n'
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
    print('Magnesiospinel: Mg Al2 O4:\n')
    print(AnalyzePhase(AtPct))

    # Ideal chromite
    AtPct = zeros(pb.MAXELEMENT)
    AtPct[pb.O-1] = 4/7*100
    AtPct[pb.Fe-1] = 1/7*100
    AtPct[pb.Cr-1] = 2/7*100
    print('Chromite: Fe Cr2 O4:\n')
    print(AnalyzePhase(AtPct))

    # Ideal Ulvospinel
    AtPct = zeros(pb.MAXELEMENT)
    AtPct[pb.O-1] = 4/7*100
    AtPct[pb.Ti-1] = 1/7*100
    AtPct[pb.Fe-1] = 2/7*100
    print('Ulvospinel: Ti Fe2 O4:\n')
    print(AnalyzePhase(AtPct))

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
    print('UC Chromite:\n')
    print(AnalyzePhase(AtPct))

