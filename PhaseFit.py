""" PhaseFit.py: Uses the quantified composition from the EDS spectrum to determine what mineral(s) are the best fit.
    For example, in the case of MgFeSiO4, it would determine that this is a good fit for olivine and that it would be Fo50."""

__author__ = 'Zack Gainsforth'
__copyright__ = 'Copyright 2014, Zack Gainsforth'
__email__ = 'zsg@gainsforth.com'

from numpy import *
import MyPython as mp
import PhysicsBasics as pb
import re
from collections import *
from scipy import optimize

def FitPhases(Quant, Phases):
    """FitPhases(Quant, Phases): Using a list of quantitative element abundances, determine which set of phases/solid
    solution end members best produce that elemental abundance.

    :param Quant: An ordered dict like so: ('H', (0.0, 0.0, 0.0, 1.0)),  where 'H' is the name of the element (string), the numbers are at %
    and wt%, oxide wt% and kfactors respectively.
    :param Phases: as list of lists: [['Name', 'Formula'], ...] for each phase to fit against.

    :return: returns OrderedDict with the molar abundance added. {'Name':  ('Formula', Abundance),...]
    """

    # We're going to do the fit using least squares.  ElAbund = PhaseMatrix * PhaseAbund.
    # PhaseAbund is a vector of molar abundances for the phases (to be computed)
    # ElAbund is a vector of elemental abundances in the set of phases (ElAbund[0] is H, [1] is He, all At %)
    # PhaseMatrix is a matrix with one column for each phase and one row for each element.  For example, SiO2 has the
    #  8th row (oxygen) = 66.67 and the 14th row (silicon) = 33.33.  Zero based indexing means [8-1] = 66.67.

    """ BUILD ElAbund and PhaseMatrix """

    # Pull ElAbund out fo the Quant list of tuples.  It's the first entry of the value tuple that is the element Z.
    ElAbund = array(list(zip(*list(Quant.values())))[0])

    # Initialize the PhaseMatrix
    PhaseMatrix = zeros((pb.MAXELEMENT, len(Phases)))

    # Add each phase (row) one by one to the matrix.
    for ColNum, Phase in enumerate(Phases):

        # Parse the mineral formula.  The format is 'Mg1.5 Fe0.5 Si1 O4'.  We require each element to be an element
        # name followed by a float.  Spaces are common for readability, but we don't require them.

        # First remove all spaces.
        Elems = ''.join(Phase[1].split())

        # Now use regex to separate all the (element, abundance) pairs. '[a-zA-Z]+' gets some characters. '[.0-9]+'
        # gets a number, with an optional decimal.
        Pairs = re.findall('[a-zA-Z]+[.0-9]+', Elems)

        for Pair in Pairs:
            # Split the name from the fractional abundance.  Added | so it splits the element and abundance apart.
            ElName, ElFrac = re.findall('[a-zA-Z]+|[.0-9]+', Pair)
            # Put this is row (whatever this phase is) and column (Z of the element)
            PhaseMatrix[pb.ElementDict[ElName][0]-1, ColNum] = ElFrac

    # Do a linear least squares fit.
    #PhaseAbund, Residual, _, _ = linalg.lstsq(PhaseMatrix, ElAbund)
    PhaseAbund, Residual = optimize.nnls(PhaseMatrix, ElAbund)

    # The PhaseAbund should be normalized so these reflect molar %.
    PhaseAbund = PhaseAbund/sum(PhaseAbund)*100

    FitComposition = sum((PhaseMatrix*PhaseAbund), axis=1)
    FitComposition = FitComposition/sum(FitComposition)*100

    # Package up the fit result.
    Names = [PhaseNames[0] for PhaseNames in Phases]
    Formulas = [PhaseNames[1] for PhaseNames in Phases]
    FitResult = OrderedDict(list(zip(Names, list(zip(Formulas, PhaseAbund)))))

    # Send it back up
    return (FitResult, Residual, FitComposition)

# Le Beautifuleaux text harness
if __name__ == '__main__':
    import pickle
    # # Let's use a mineral like Fo50
    # AtPct = zeros(pb.MAXELEMENT)
    # AtPct[pb.O-1] = 4
    # AtPct[pb.Mg-1] = 1
    # AtPct[pb.Fe-1] = 1
    # AtPct[pb.Si-1] = 1
    #
    # # Normalize it for atom %
    # AtPct = nan_to_num(AtPct/sum(Counts)*100)
    #
    # # Also convert to weight %
    # M_el = array(pb.ElementalWeights[1:])
    # WtPct = nan_to_num(AtPct * M_el)
    # WtPct = nan_to_num(WtPct / sum(WtPct) *100)
    #
    # Quant = OrderedDict(zip(pb.ElementalSymbols[1:], zip(AtPct, WtPct)))

    # Load the list of phases.  It's two column.  First is the human name for the phase.  Second is the formula in the format 'Si1 O2' for SiO2.
    # The converter removes whitespace from the formula column so we can have variable column widths.
    Phases = genfromtxt('ConfigData/Phases.csv', dtype=None, comments='#', delimiter=',',
                            converters={1: lambda s: str(s).lstrip()})

    SelectedPhases = pickle.load(open('Temp/SelectedPhases.pickle', 'rb'))
    Quant = pickle.load(open('Temp/DebugQuant.pickle', 'rb'))

    # Trim the phases down to just the ones the user selected to fit.
    PhasesToFit = [PhasesToFit for PhasesToFit in Phases if PhasesToFit[0] in SelectedPhases]

    FitResult, Residual = FitPhases(Quant, PhasesToFit)

    print('{:30s} {:5s}'.format('Phase', 'Molar %'))
    for Phase, Result in FitResult.items():
        print('{:30s} {:5.3f}%'.format(Phase, Result[1]))

    print('{:30s} {:g}'.format('Fit residual', Residual))
