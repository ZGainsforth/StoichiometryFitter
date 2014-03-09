"""CountsToQuant.py: Used to convert EDS counts to a quantitative number by applying k-factors, PRZ, and then doing At% Wt% conversions."""

__author__ = 'Zack Gainsforth'
__copyright__ = 'Copyright 2014, Zack Gainsforth'
__email__ = 'zsg@gainsforth.com'

from numpy import *
import MyPython as mp
import PhysicsBasics as pb


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


def GetAbundancesFromCounts(Counts, kfacsfile=None, InputType='Counts', AbsorptionCorrection=0, OByStoichiometry=None):
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
            # The converter ensures the second and on columns are floats.
            floatme = lambda s: float(s or 0)
            # Skip one header line, skip comments, and be tolerant of missing entries (using the converter.)
            try:
                kfacs = genfromtxt('ConfigData/kfacs ' + kfacsfile + '.csv', dtype=None, comments='#', skip_header=1, delimiter=',', converters={1:floatme, 2:floatme, 3:floatme})
            except:
                ReportError('Could not read k-factor file.')

            # Now we want a single array of the k-factors for quanting each element.  For now, we only implement K-shell.
            # TODO implement L, M shells.
            kfactors = ones(pb.MAXELEMENT)
            for Z in range(1, pb.MAXELEMENT):
                kfactors[Z-1] = kfacs[Z-1][1] # First column is the K-shell.

            # Now multiply by the k-factors.
            Counts = Counts*kfactors

        Counts = ComputeOxygenStoichiometry(Counts, OByStoichiometry)

        # Make Wt % from counts.
        WtPct = nan_to_num(Counts/sum(Counts)*100)

        # Make At % too.
        M_el = array(pb.ElementalWeights[1:])
        AtPct = nan_to_num(WtPct / M_el)
        AtPct = nan_to_num(AtPct / sum(AtPct) *100)

    # In the case of at %, we just convert to wt %
    if InputType == 'At %':
        Counts = ComputeOxygenStoichiometry(Counts, OByStoichiometry, ByMass=False)

        # Normalize it for atom %
        AtPct = nan_to_num(Counts/sum(Counts)*100)

        # Also convert to weight %
        M_el = array(pb.ElementalWeights[1:])
        WtPct = nan_to_num(AtPct * M_el)
        WtPct = nan_to_num(WtPct / sum(WtPct) *100)

    # In the case of wt %, we just convert to at %
    if InputType == 'Wt %':
        Counts = ComputeOxygenStoichiometry(Counts, OByStoichiometry, ByMass=True)

         # Make Wt % from counts.
        WtPct = nan_to_num(Counts/sum(Counts)*100)

        # Make At % too.
        M_el = array(pb.ElementalWeights[1:])
        AtPct = nan_to_num(WtPct / M_el)
        AtPct = nan_to_num(AtPct / sum(AtPct) *100)

    return (WtPct, AtPct)
