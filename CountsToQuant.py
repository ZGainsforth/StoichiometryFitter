"""CountsToQuant.py: Used to convert EDS counts to a quantitative number by applying k-factors, PRZ, and then doing At% Wt% conversions."""

__author__ = 'Zack Gainsforth'
__copyright__ = 'Copyright 2014, Zack Gainsforth'
__email__ = 'zsg@gainsforth.com'

from numpy import *
from collections import OrderedDict
import linecache

import MyPython as mp
import PhysicsBasics as pb
import CharacteristicEmission as ce
import AbsorptionCorrection as abs


def ComputeOxygenStoichiometry(Counts, AtomCharges, ByMass=True):
    # If computing oxygen by stoichiometry, then figure the O counts now.
    # The formula is:
    # C_O = oxygen counts.
    # C_el = element counts (for a given element).
    # M_O = mass of oxygen (16)
    # M_el = mass of element
    # Q_el = Charge of element (e.g. Na=1 and Si=4)
    # Q_O = Charge of oxygen (2)
    # C_O = sum(C_el * M_O/M_el * Q_el/Q_O)
    # Where sum is over all elements except oxygen.

    # That's when counts are proportional to wt % (as when using wt % k-factors) or when wt % is the input.
    # When atom % is the input, the equation is a little simpler:
    # C_O = sum(C_el * Q_el/Q_O)

    if AtomCharges is not None:
        # First zero out the existing O.
        Counts[pb.O - 1] = 0

        # Also zero out any negatively charged atoms, since they aren't going to pair with oxygen.
        AtomCharges[AtomCharges<0] = 0

        # Element weights vector.
        M_el = array(pb.ElementalWeights[1:])
        M_O = array(pb.ElementalWeights[pb.O])
        Q_O = 2
        Q_el = AtomCharges

        if ByMass == True:
            C_O = sum(nan_to_num(Counts * M_O / M_el * Q_el / Q_O))
        else:
            C_O = sum(nan_to_num(Counts * Q_el / Q_O))

        # Here counts is zero based so the oxygen index is one down.
        Counts[pb.O - 1] = C_O

    return Counts

# Used for ensuring columns read from the csv files are floats (or 0 if not).
floatme = lambda s: float(s or 0)

def DoArbitraryAbsorptionCorrection(ArbitraryAbsorptionCorrection, Counts):

    try:
        ArbAbsFileName = 'ConfigData/Absorption ' + ArbitraryAbsorptionCorrection + '.csv'
        ArbAbsWtPct = genfromtxt(ArbAbsFileName, dtype=None, comments='#', skip_header=3, delimiter=',',
                                 converters={1: floatme})
        # And we want just column 1.
        ArbAbsWtPct = [Wt for (Name, Wt) in ArbAbsWtPct]
        # First line is tau.
        (s, ArbAbsTau) = linecache.getline(ArbAbsFileName, 1).strip().split('=')
        assert (s == '#tau')
        ArbAbsTau = float(ArbAbsTau)
        # Second line is rho.
        (s, ArbAbsRho) = linecache.getline(ArbAbsFileName, 2).strip().split('=')
        assert (s == '#rho')
        ArbAbsRho = float(ArbAbsRho)
    except:
        mp.ReportError('Could not read Arbitrary Absorption Correction file.')

    # Get the energy of each line (actually a weighted average of the lines of that series).
    LineEnergies = zeros(pb.MAXELEMENT)
    for Z in range(3, 50):  # We start at 3 because H and He don't have fluor emission per se.
        # For now, we only use K-shell.
        LineEnergies[Z - 1] = ce.GetFluorescenceLineEnergy(pb.ElementalSymbols[Z], 'K')

    # For the really heavy elements (Uuo, etc.) we get nans because those lines aren't measured.  Also,
    # we don't care about
    LineEnergies = nan_to_num(LineEnergies)
    # Update counts with the new corrected (after absorption) values.
    Counts = abs.DoAbsorption(LineEnergies, Counts, ArbAbsWtPct, ArbAbsRho, ArbAbsTau)
    return Counts


def GetAbundancesFromCounts(Counts, kfacsfile=None, InputType='Counts',
                            ArbitraryAbsorptionCorrection=None, AbsorptionCorrection=0,
                            OByStoichiometry=None):
    """Counts (ndarray) is the input vector giving all the counts for each element in order. It is MAXELEMENTS long.
    kfacsfile=None (str) gives the k-factors for each element, or None means not to apply k-factors.
        'Titan 80 keV' loads k-factors for the Titan at 80 keV from 'kfacs Titan 80 keV.csv'.
        In general, all valid k-factor files will be kfacs*.csv in the ConfigData directory.
    InputType='Counts' (str) can be 'Counts', or 'AtPct' or 'WtPct'.  kfacsfile is only used if InputType=Counts.
        if AtPct or WtPct, the output will produce the other, and can still apply absorption correction.
    AbsorptionCorrection=0 (float) is the thin film thickness to apply an absorption correction for.
    OByStoichiometry=None if we are not computing oxygen by stoichiometry.  Vector of element charge if we are.
    """

    # First let's handle conversion by counts.
    if InputType == 'Counts':
        # If we're using k-factors, get them and multiply them now.
        if kfacsfile is not None:

            # Load the k-factor file.
            # Skip one header line, skip comments, and be tolerant of missing entries (using the converter.)
            try:
                kfacs = genfromtxt('ConfigData/kfacs ' + kfacsfile + '.csv', dtype=None, comments='#', skip_header=1, delimiter=',', converters={1:floatme, 2:floatme, 3:floatme})
            except:
                mp.ReportError('Could not read k-factor file.')

            # Now we want a single array of the k-factors for quanting each element.  For now, we only implement K-shell.
            # TODO implement L, M shells.
            kfactors = ones(pb.MAXELEMENT)
            for Z in range(1, pb.MAXELEMENT + 1):
                kfactors[Z-1] = kfacs[Z-1][1] # First column is the K-shell.

            # Now multiply by the k-factors.
            Counts = Counts*kfactors

        # If we are including an arbitrary absorption correction, then do that.
        if ArbitraryAbsorptionCorrection is not None:
            Counts = DoArbitraryAbsorptionCorrection(ArbitraryAbsorptionCorrection, Counts)

        Counts = ComputeOxygenStoichiometry(Counts, OByStoichiometry)

        # Make Wt % from counts.
        WtPct = nan_to_num(Counts/sum(Counts)*100)

        # Make At % too.
        M_el = array(pb.ElementalWeights[1:])
        AtPct = nan_to_num(WtPct / M_el)
        AtPct = nan_to_num(AtPct / sum(AtPct) *100)

    # In the case of at %, we just convert to wt %
    if InputType == 'At %':

        #If we want to do an arbitrary absorption correction, then it expects to operate on something proportional to
        #  Wt % since the CXRO scattering profiles were based on Wt %.  So in this case, first we convert to Wt% and
        # then do our correction, and recompute At %.
        # TODO Arbitrary absorption on At %
        # If we are including an arbitrary absorption correction, then do that.
        if ArbitraryAbsorptionCorrection is not None:
            mp.ReportError('TODO: Arbitrary absorption on At %.  Correction not computed.')

        Counts = ComputeOxygenStoichiometry(Counts, OByStoichiometry, ByMass=False)

        # Normalize it for atom %
        AtPct = nan_to_num(Counts/sum(Counts)*100)

        # Also convert to weight %
        M_el = array(pb.ElementalWeights[1:])
        WtPct = nan_to_num(AtPct * M_el)
        WtPct = nan_to_num(WtPct / sum(WtPct) *100)

    # In the case of wt %, we just convert to at %
    if InputType == 'Wt %':

        # If we are including an arbitrary absorption correction, then do that.
        if ArbitraryAbsorptionCorrection is not None:
            Counts = DoArbitraryAbsorptionCorrection(ArbitraryAbsorptionCorrection, Counts)

        Counts = ComputeOxygenStoichiometry(Counts, OByStoichiometry, ByMass=True)

         # Make Wt % from counts.
        WtPct = nan_to_num(Counts/sum(Counts)*100)

        # Make At % too.
        M_el = array(pb.ElementalWeights[1:])
        AtPct = nan_to_num(WtPct / M_el)
        AtPct = nan_to_num(AtPct / sum(AtPct) *100)

    # TODO Oxide Wt%

    Quant = OrderedDict(zip(pb.ElementalSymbols[1:], zip(AtPct, WtPct)))
    return Quant
