"""CountsToQuant.py: Used to convert EDS counts to a quantitative number by applying k-factors, PRZ, and then doing At% Wt% conversions."""

__author__ = 'Zack Gainsforth'
__coauthor__ = 'Zhenbang Yu'
__copyright__ = 'Copyright 2014, Zack Gainsforth'
__email__ = 'zsg@gainsforth.com'

from numpy import *
from collections import OrderedDict
import linecache
from fractions import Fraction
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


def AbsorptionUsingWtPct(AbsRho, AbsTau, AbsWtPct, Counts, Takeoff=90):
    # Get the energy of each line (actually a weighted average of the lines of that series).
    LineEnergies = zeros(pb.MAXELEMENT)
    for Z in range(3, 92):  # We start at 3 because H and He don't have fluor emission per se.
        # For now, we only use K-shell.
        LineEnergies[Z - 1] = ce.GetFluorescenceLineEnergy(pb.ElementalSymbols[Z], 'K')

    # For the really heavy elements (Uuo, etc.) we get nans because those lines aren't measured.  Also,
    # we don't care about
    LineEnergies = nan_to_num(LineEnergies)
    # Update counts with the new corrected (after absorption) values.
    Counts = abs.DoAbsorption(LineEnergies, Counts, AbsWtPct, AbsRho, AbsTau, Takeoff)
    return Counts


def DoArbitraryAbsorptionCorrection(ArbitraryAbsorptionCorrection, Counts):
    """DoArbitraryAbsorptionCorrection(ArbitraryAbsorptionCorrection, Counts):

    :param ArbitraryAbsorptionCorrection: Name of csv file with absorption parameters including abs length, density,
    and elements.
    :param Counts: The counts in which we are applying absorption correction to.  These must be either raw counts or
    wt % (since the absorption correction assumes the counts are proportional to wt %.
    :return: A new counts vector (proportional to wt %) after absorption.
    """
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
        print('Could not read Arbitrary Absorption Correction file.')
        return

    # Use negative Tau to correct for absorption, not add absorption.
    Counts = AbsorptionUsingWtPct(ArbAbsRho, -ArbAbsTau, ArbAbsWtPct, Counts)
    return Counts



def WtPctToOxWtPct(OByStoichiometry, WtPct):
    """ WtPctToOxWtPct(OByStoichiometry, WtPct): Takes a weight % vector, and produces oxide wt % using the cation
    charges in OByStoichiometry.

    :param OByStoichiometry: List of cation charge states.  Fe = 2 for example means that it is Fe2+ and would pair
    with one oxygen (2-) as FeO.
    :param WtPct: How much of each element as a weight %.
    :return: OxWtPct vector of oxide weights.
    """

    # Get element masses (a vector for all elements, and the mass of O specifically.)
    M_el = array(pb.ElementalWeights[1:])
    M_O = pb.ElementalWeights[pb.O]

    # We only make oxides with positively charged cations.  The negs are transferred directly.
    PosCharges = OByStoichiometry.clip(min=0)
    # 1 means that we can multiply by this vector to extract the elements that are not stoichometrically tied to O.
    NegMask = (OByStoichiometry <= 0).astype(float)

    # Oxide weight is the cation + the oxygen (where the relative amount of oxygen is computed based on the
    # cation charge.
    OxWtPct = nan_to_num(WtPct * (1 + PosCharges / 2 * M_O / M_el))

    # Of course this means that the weight of oxygen by itself is none.
    OxWtPct[pb.O - 1] = 0

    # Finally, renormalize.
    OxWtPct = nan_to_num(OxWtPct / sum(OxWtPct) * 100)

    return OxWtPct

def OxWtPctToWtPct(OByStoichiometry, OxWtPct):
    """ OxWtPctToWtPct(OByStoichiometry, WtPct): Takes an oxide weight % vector, and produces wt % using the
    cation charges in OByStoichiometry.

    :param OByStoichiometry: List of cation charge states.  Fe = 2 for example means that it is Fe2+ and would pair
    with one oxygen (2-) as FeO.
    :param OxWtPct: How much of each element as an oxide weight %.
    :return: WtPct vector of elemental weights.
    """

    # Get element masses (a vector for all elements, and the mass of O specifically.)
    M_el = array(pb.ElementalWeights[1:])
    M_O = pb.ElementalWeights[pb.O]

    # We only make oxides with positively charged cations.  The negs are transferred directly.
    PosCharges = OByStoichiometry.clip(min=0)
    # 1 means that we can multiply by this vector to extract the elements that are not stoichometrically tied to O.
    # 1 means that we can multiply by this vector to extract the elements that are not stoichometrically tied to O.
   # NegMask = (OByStoichiometry <= 0).astype(float)
    # And specifically ignore oxygen.
   # NegMask[pb.O-1] = 0

    # Sometimes the oxygen deficit is reported in the oxide wt %'s from microprobe folks.
    ODeficit = OxWtPct[pb.O-1]

    # Oxide weight is the cation + the oxygen (where the relative amount of oxygen is computed based on the
    # cation charge.
    # First get the cation weight
    WtPct = nan_to_num(OxWtPct / (1 + M_O/M_el * PosCharges/2))
    # Now get the oxygen weight.
    OxygenWt = nan_to_num(OxWtPct - WtPct)
    # For the non-oxidized elements, we just copy them over.
    #WtPct  = WtPct + nan_to_num(OxWtPct * NegMask)

    # Now plug in the oxygen weight
    WtPct[pb.O - 1] = sum(OxygenWt) + ODeficit

    # Finally, renormalize.
    WtPct = nan_to_num(WtPct / sum(WtPct) * 100)

    return WtPct


def WtPctToEverything(WtPct, OByStoichiometry=None):
    WtPct = ComputeOxygenStoichiometry(WtPct, OByStoichiometry, ByMass=True)

    # Normalize Wt %.
    WtPct = nan_to_num(WtPct / sum(WtPct) * 100)

    # Make oxide Wt % from Wt % if we have stoichiometry info
    if OByStoichiometry is not None:
        OxWtPct = WtPctToOxWtPct(OByStoichiometry, WtPct)
    else:
        OxWtPct = zeros(shape(WtPct))

    # Make At % too.
    M_el = array(pb.ElementalWeights[1:])
    AtPct = nan_to_num(WtPct / M_el)
    AtPct = nan_to_num(AtPct / sum(AtPct) * 100)

    return AtPct, WtPct, OxWtPct

def AtPctToWtPct(AtPct, OByStoichiometry=None):
    # We have to do O stoichoimetry before conversion to wt % or it could be WAY off.
    AtPct = ComputeOxygenStoichiometry(AtPct, OByStoichiometry, ByMass=False)

    # Convert to weight %
    M_el = array(pb.ElementalWeights[1:])
    WtPct = nan_to_num(AtPct * M_el)
    WtPct = nan_to_num(WtPct / sum(WtPct) * 100)
    return WtPct

def GetAbundancesFromCounts(Counts, kfacsfile=None, InputType='Counts', ArbitraryAbsorptionCorrection=None,
                            AbsorptionCorrection=0, Takeoff=0, OByStoichiometry=None):
    """Counts (ndarray) is the input vector giving all the counts for each element in order. It is MAXELEMENTS long.
    kfacsfile=None (str) gives the k-factors for each element, or None means not to apply k-factors.
        'Titan 80 keV' loads k-factors for the Titan at 80 keV from 'kfacs Titan 80 keV.csv'.
        In general, all valid k-factor files will be kfacs*.csv in the ConfigData directory.
    InputType='Counts' (str) can be 'Counts', or 'AtPct' or 'WtPct'.  kfacsfile is only used if InputType=Counts.
        if AtPct or WtPct, the output will produce the other, and can still apply absorption correction.
    AbsorptionCorrection=0 (float) is the thin film thickness to apply an absorption correction for.
    OByStoichiometry=None if we are not computing oxygen by stoichiometry.  Vector of element charge if we are.
    :param Takeoff:
    """

    # Start with default k-factors.  Ones means that if this is multiplied, it doesn't change anything.
    kfactors = ones(pb.MAXELEMENT)

    # The if else here basically takes the data in from whatever form it is, and outputs wt %.  From there we can do
    # the absorption corrections and convert to all the requested formats.

    # First let's handle conversion by counts.
    if InputType == 'Counts':
        # If we're using k-factors, get them and multiply them now.
        if kfacsfile is not None:

            # Load the k-factor file.
            # Skip one header line, skip comments, and be tolerant of missing entries (using the converter.)
            try:
                kfacs = genfromtxt('ConfigData/kfacs ' + kfacsfile + '.csv', dtype=None, comments='#', skip_header=1, delimiter=',', converters={1:floatme, 2:floatme, 3:floatme})
            except:
                print('Could not read k-factor file.')
                return

            # Now we want a single array of the k-factors for quanting each element.  For now, we only implement K-shell.
            # TODO implement L, M shells.
            kfactors = ones(pb.MAXELEMENT)
            for Z in range(1, pb.MAXELEMENT + 1):
                kfactors[Z-1] = kfacs[Z-1][1] # First column is the K-shell.

            # Now multiply by the k-factors.
            WtPct = Counts*kfactors
        else:
            # If we have counts input, but no k-factors, counts are expected to be proportional to wt %
            WtPct = Counts

        # Normalize WtPct
        WtPct = nan_to_num(WtPct / sum(WtPct) * 100)

    # In the case of at %, we just convert to wt %
    if InputType == 'At %':
        WtPct = AtPctToWtPct(Counts, OByStoichiometry)

    # In the case of wt %, we just convert to at %
    if InputType == 'Wt %':
        # This is the simple case, right?
        WtPct = Counts

    if InputType == 'Ox Wt %':
        # O by stoichiometry is already done by inputting oxides.  Nothing to do here.
        if OByStoichiometry is None:
            print('Cannot do oxide wt % without doing oxygen by stoichiometry.')
            return

        # Normalize the oxide Wt %.
        OxWtPct = nan_to_num(Counts / sum(Counts) * 100)

        # Make Wt % from oxide Wt %.
        WtPct = OxWtPctToWtPct(OByStoichiometry, OxWtPct)



    # Handle any O by stoichiometry if needed.
    WtPct = ComputeOxygenStoichiometry(WtPct, OByStoichiometry)

    # Do the self absorption correction if requested.
    if AbsorptionCorrection != 0:
        # Note that absorption correction is already the product of rho and tau.  So: 1, AbsorptionCorrection
        # Since we're self-absorbing, the absorption cross-sections are computed from WtPct, and the "counts" are from WtPct.
        # Also, we're trying to figure out what intensity the spectrum would have had BEFORE it was absorbed, not see what absorbing our spectrum would create.  So the AbsorptionCorrection should be *negative*.
        WtPct = AbsorptionUsingWtPct(1, -AbsorptionCorrection, WtPct, WtPct, Takeoff=Takeoff)

    # Do the arbitrary absorption correction if requested.
    if ArbitraryAbsorptionCorrection is not None:
        WtPct = DoArbitraryAbsorptionCorrection(ArbitraryAbsorptionCorrection, WtPct)

    # After absorption corrections, we have to recompute O by stoichiometry.
    WtPct = ComputeOxygenStoichiometry(WtPct, OByStoichiometry)

    # And now we have a stoichiometry and absorption corrected wt %, get all the rest.
    AtPct, WtPct, OxWtPct = WtPctToEverything(WtPct, OByStoichiometry)

    Quant = OrderedDict(list(zip(pb.ElementalSymbols[1:], list(zip(AtPct, WtPct, OxWtPct, kfactors)))))
    return Quant

if __name__ == '__main__':
    print('Implement ye old test harness please!')

    # Fo87 standard.
    counts = array([0., 0., 0., 0., 0., 0.,
                    0., 4831091., 0., 0., 0., 4209156.,
                    69373., 2874614., 0., 12949., 0., 0.,
                    0., 28085., 0., 0., 0., 5491.,
                    14945., 1078728., 0., 20272., 0., 0.,
                    0., 0., 0., 0., 0., 0.,
                    0., 0., 0., 0., 0., 0.,
                    0., 0., 0., 0., 0., 0.,
                    0., 0., 0., 0., 0., 0.,
                    0., 0., 0., 0., 0., 0.,
                    0., 0., 0., 0., 0., 0.,
                    0., 0., 0., 0., 0., 0.,
                    0., 0., 0., 0., 0., 0.,
                    0., 0., 0., 0., 0., 0.,
                    0., 0., 0., 0., 0., 0.,
                    0., 0., 0., 0., 0., 0.,
                    0., 0., 0., 0., 0., 0.,
                    0., 0., 0., 0., 0., 0.,
                    0., 0., 0., 0., 0., 0.,
                    0., 0., 0., 0.])
    InputType = 'Counts'
    OByStoichiometry = array([1., 0., 1., 2., 3., 4., -3., -2., -1., 0., 1., 2., 3.,
                              4., 5., -2., -1., 0., 1., 2., 3., 4., 3., 3., 2., 2.,
                              2., 2., 2., 2., 0., 0., 0., -2., -1., 0., 1., 2., 3.,
                              4., 0., 0., 0., 2., 0., 0., 0., 0., 0., 0., 0., 0.,
                              0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.,
                              0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.,
                              0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.,
                              0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.,
                              0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.])
    kfacsfile = 'Titan 80 keV Esprit'
    ArbitraryCorr = None #'Titan Detector Experiment'

    # Quant it.
    Quant = GetAbundancesFromCounts(counts, kfacsfile=kfacsfile, InputType=InputType,
                                    ArbitraryAbsorptionCorrection=ArbitraryCorr, AbsorptionCorrection=0,
                                    OByStoichiometry=OByStoichiometry)
    print(Quant)

    if Quant == OrderedDict([('H', (0.0, 0.0, 0.0)), ('He', (0.0, 0.0, 0.0)), ('Li', (0.0, 0.0, 0.0)), ('Be', (0.0, 0.0, 0.0)), ('B', (0.0, 0.0, 0.0)), ('C', (0.0, 0.0, 0.0)), ('N', (0.0, 0.0, 0.0)), ('O', (57.387880689327353, 42.52227907194424, 0.0)), ('F', (0.0, 0.0, 0.0)), ('Ne', (0.0, 0.0, 0.0)), ('Na', (0.0, 0.0, 0.0)), ('Mg', (22.770862592362683, 25.631130297848344, 42.503490145097665)), ('Al', (0.36418624074129041, 0.45507491376739712, 0.85984754459858115)), ('Si', (14.6440752260316, 19.047446458946819, 40.748873520973397)), ('P', (0.0, 0.0, 0.0)), ('S', (0.061361233043780619, 0.091120894150348644, 0.091120894150348644)), ('Cl', (0.0, 0.0, 0.0)), ('Ar', (0.0, 0.0, 0.0)), ('K', (0.0, 0.0, 0.0)), ('Ca', (0.12773278755077558, 0.2370833642571108, 0.33172859550855094)), ('Sc', (0.0, 0.0, 0.0)), ('Ti', (0.0, 0.0, 0.0)), ('V', (0.0, 0.0, 0.0)), ('Cr', (0.021908530592510082, 0.052756584478407038, 0.077106690477813503)), ('Mn', (0.060522615336063783, 0.15398681555037758, 0.19883181607263334)), ('Fe', (4.4716803207256399, 11.565054774955751, 14.878403102763556)), ('Co', (0.0, 0.0, 0.0)), ('Ni', (0.089789764288306456, 0.24406682410120242, 0.31059769035745571)), ('Cu', (0.0, 0.0, 0.0)), ('Zn', (0.0, 0.0, 0.0)), ('Ga', (0.0, 0.0, 0.0)), ('Ge', (0.0, 0.0, 0.0)), ('As', (0.0, 0.0, 0.0)), ('Se', (0.0, 0.0, 0.0)), ('Br', (0.0, 0.0, 0.0)), ('Kr', (0.0, 0.0, 0.0)), ('Rb', (0.0, 0.0, 0.0)), ('Sr', (0.0, 0.0, 0.0)), ('Y', (0.0, 0.0, 0.0)), ('Zr', (0.0, 0.0, 0.0)), ('Nb', (0.0, 0.0, 0.0)), ('Mo', (0.0, 0.0, 0.0)), ('Tc', (0.0, 0.0, 0.0)), ('Ru', (0.0, 0.0, 0.0)), ('Rh', (0.0, 0.0, 0.0)), ('Pd', (0.0, 0.0, 0.0)), ('Ag', (0.0, 0.0, 0.0)), ('Cd', (0.0, 0.0, 0.0)), ('In', (0.0, 0.0, 0.0)), ('Sn', (0.0, 0.0, 0.0)), ('Sb', (0.0, 0.0, 0.0)), ('Te', (0.0, 0.0, 0.0)), ('I', (0.0, 0.0, 0.0)), ('Xe', (0.0, 0.0, 0.0)), ('Cs', (0.0, 0.0, 0.0)), ('Ba', (0.0, 0.0, 0.0)), ('La', (0.0, 0.0, 0.0)), ('Ce', (0.0, 0.0, 0.0)), ('Pr', (0.0, 0.0, 0.0)), ('Nd', (0.0, 0.0, 0.0)), ('Pm', (0.0, 0.0, 0.0)), ('Sm', (0.0, 0.0, 0.0)), ('Eu', (0.0, 0.0, 0.0)), ('Gd', (0.0, 0.0, 0.0)), ('Tb', (0.0, 0.0, 0.0)), ('Dy', (0.0, 0.0, 0.0)), ('Ho', (0.0, 0.0, 0.0)), ('Er', (0.0, 0.0, 0.0)), ('Tm', (0.0, 0.0, 0.0)), ('Yb', (0.0, 0.0, 0.0)), ('Lu', (0.0, 0.0, 0.0)), ('Hf', (0.0, 0.0, 0.0)), ('Ta', (0.0, 0.0, 0.0)), ('W', (0.0, 0.0, 0.0)), ('Re', (0.0, 0.0, 0.0)), ('Os', (0.0, 0.0, 0.0)), ('Ir', (0.0, 0.0, 0.0)), ('Pt', (0.0, 0.0, 0.0)), ('Au', (0.0, 0.0, 0.0)), ('Hg', (0.0, 0.0, 0.0)), ('Tl', (0.0, 0.0, 0.0)), ('Pb', (0.0, 0.0, 0.0)), ('Bi', (0.0, 0.0, 0.0)), ('Po', (0.0, 0.0, 0.0)), ('At', (0.0, 0.0, 0.0)), ('Rn', (0.0, 0.0, 0.0)), ('Fr', (0.0, 0.0, 0.0)), ('Ra', (0.0, 0.0, 0.0)), ('Ac', (0.0, 0.0, 0.0)), ('Th', (0.0, 0.0, 0.0)), ('Pa', (0.0, 0.0, 0.0)), ('U', (0.0, 0.0, 0.0)), ('Np', (0.0, 0.0, 0.0)), ('Pu', (0.0, 0.0, 0.0)), ('Am', (0.0, 0.0, 0.0)), ('Cm', (0.0, 0.0, 0.0)), ('Bk', (0.0, 0.0, 0.0)), ('Cf', (0.0, 0.0, 0.0)), ('Es', (0.0, 0.0, 0.0)), ('Fm', (0.0, 0.0, 0.0)), ('Md', (0.0, 0.0, 0.0)), ('No', (0.0, 0.0, 0.0)), ('Lr', (0.0, 0.0, 0.0)), ('Rf', (0.0, 0.0, 0.0)), ('Db', (0.0, 0.0, 0.0)), ('Sg', (0.0, 0.0, 0.0)), ('Bh', (0.0, 0.0, 0.0)), ('Hs', (0.0, 0.0, 0.0)), ('Mt', (0.0, 0.0, 0.0)), ('Ds', (0.0, 0.0, 0.0)), ('Rg', (0.0, 0.0, 0.0)), ('Cn', (0.0, 0.0, 0.0)), ('Uut', (0.0, 0.0, 0.0)), ('Fl', (0.0, 0.0, 0.0)), ('Uup', (0.0, 0.0, 0.0)), ('Lv', (0.0, 0.0, 0.0)), ('Uus', (0.0, 0.0, 0.0)), ('Uuo', (0.0, 0.0, 0.0))]):
        print('Fo87, Titan 80 keV kfacs = PASS')
    else:
        print('Fo87, Titan 80 keV kfacs = FAIL')
