""" ReportResults.py: Takes the quantification results and the results of the fitting of phases and produces human
    friendly outputs."""

__author__ = 'Zack Gainsforth'
__copyright__ = 'Copyright 2014, Zack Gainsforth'
__email__ = 'zsg@gainsforth.com'

from numpy import *
from collections import OrderedDict

import PhysicsBasics as pb

def BuildInputTable(Quant, InputType):
    """Build a structured table for input data."""
    rows = []
    SumAbundance = 0
    for El, Abund in OrderedDict([(El, Abund) for (El, Abund) in Quant.items() if Abund > 0]).items():
        SumAbundance += Abund
        rows.append({'element': El, InputType: float(Abund)})
    return {
        'name': 'input',
        'title': 'Input Data',
        'columns': ['element', InputType],
        'rows': rows,
        'metadata': {'total': float(SumAbundance), 'input_type': InputType},
        'description': 'Non-zero element values supplied to the calculation.',
    }

def BuildQuantTable(Quant, OByStoichiometry=None):
    """Build a structured table for quantification results."""
    rows = []
    if OByStoichiometry is None:
        OStoich = [None] * len(Quant)
    else:
        OStoich = list(map(float, OByStoichiometry))

    Q = OrderedDict([(El, Abund) for (El, Abund) in Quant.items() if Abund[0] > 0])
    for El, Abund in Q.items():
        ElIndex = pb.ElementalSymbols.index(El)-1
        rows.append({
            'element': El,
            'at_pct': float(Abund[0]),
            'wt_pct': float(Abund[1]),
            'oxide_wt_pct': float(Abund[2]),
            'valence': OStoich[ElIndex],
            'k_factor': float(Abund[3]),
        })
    return {
        'name': 'quantification',
        'title': 'Quantification Results',
        'columns': ['element', 'at_pct', 'wt_pct', 'oxide_wt_pct', 'valence', 'k_factor'],
        'rows': rows,
        'metadata': {},
        'description': 'Elemental abundances calculated from the supplied input data and correction options.',
    }

def BuildPhaseTables(FitResult, Residual, FitComposition):
    """Build structured tables for phase fit results."""
    phase_rows = []
    for Phase, Result in FitResult.items():
        phase_rows.append({
            'phase': Phase,
            'formula': Result[0],
            'molar_pct': float(Result[1]),
        })

    composition_rows = []
    Q = OrderedDict([(El, Abund) for (El, Abund) in enumerate(FitComposition) if Abund > 0])
    SumAbundance = 0
    for El, Abund in Q.items():
        SumAbundance += Abund
        composition_rows.append({
            'element': pb.ElementalSymbols[El+1],
            'at_pct': float(Abund),
        })

    return [
        {
            'name': 'phase_fit',
            'title': 'Phase Fit Results',
            'columns': ['phase', 'formula', 'molar_pct'],
            'rows': phase_rows,
            'metadata': {'residual': float(Residual)},
            'description': 'Non-negative least-squares phase abundances for the selected phase set.',
        },
        {
            'name': 'phase_fit_composition',
            'title': 'Composition Of Phase Fit',
            'columns': ['element', 'at_pct'],
            'rows': composition_rows,
            'metadata': {'total': float(SumAbundance)},
            'description': 'Elemental composition reconstructed from the phase fit.',
        },
    ]

def FormatQuantResults(Quant, ArbitraryAbsorptionCorrection=None,
                       AbsorptionCorrection=None,
                       Takeoff=90,
                       OByStoichiometry=None,
                       kFactors=None):
    """ReportQuantResults(Quant): Generates human readable report strings for the At% and Wt% results from the quant.

    :param Quant: An OrderedDict with key = element name (e.g. 'H' or 'Fe') and value = (At%, Wt %).  The first
    entry is H and the next is He, etc on up the periodic table until PhysicsBasics.MAXELEMENT
    """

    # Start with a blank report.
    ReportStr = ''

    # Report on the parameters used in the fit.
    if ArbitraryAbsorptionCorrection is not None:
        ReportStr += 'Arbitrary Absorption Correction used: %s\n' % (ArbitraryAbsorptionCorrection)
        print(ArbitraryAbsorptionCorrection)

    if kFactors is not None:
        ReportStr += 'k-factors used: %s\n' % (kFactors)

    if AbsorptionCorrection is not None and AbsorptionCorrection != 0:
        ReportStr += 'Absorption Correction: %f nm*g/cm3\n' % (AbsorptionCorrection*1000)
        ReportStr += 'Takeoff angle: %0.2f degrees\n' % (Takeoff)

    if OByStoichiometry is not None:
        ReportStr += 'Oxygen determined by stoichiometry\n'
        print(OByStoichiometry)
        OStoich = list(map('{:8.3f}'.format, OByStoichiometry))
    else:
        OStoich =  ['{:>8s}'.format('n/a')]*len(Quant)

    ReportStr += '\n'

# For every element that is in the sample (non-zero abundance), we are going to include it in the result.

    # Comprehend all the zero-abundance elements out.
    Q = OrderedDict([(El, Abund) for (El, Abund) in Quant.items() if Abund[0] > 0])

    # Now let's print out each element
    ReportStr += 'Quantification results:\n'.format()
    ReportStr += '{:<8s} {:>8s} {:>8s} {:>8s} {:>8s} {:>8s}\n'.format('Element', 'At%', 'Wt%', 'Ox Wt %', 'Valence', 'k-factor')
    for El, Abund in Q.items():
        ElIndex = list(pb.ElementDict.keys()).index(El)-1
        if Abund[1] > 0.1:
            # Report straightforward percentages.
            ReportStr += '{:8s} {:8.3f} {:8.3f} {:8.3f} {:8s} {:8.3f}\n'.format(El, Abund[0], Abund[1], Abund[2], OStoich[ElIndex], Abund[3])
        else:
            # For trace elements report ppm.
            ReportStr += '{:8s} {:4.0f} ppm {:4.0f} ppm {:4.0f} ppm {:8s} {:8.3f}\n'.format(El, Abund[0]*1e4, Abund[1]*1e4, Abund[2]*1e4, OStoich[ElIndex], Abund[3])

    ReportStr += '\n'.format()

    return ReportStr

def FormatInputResults(Quant, InputType):
    """FormatInputResults(Quant): Generates human readable report strings for input data (counts or %).

    :param Quant: An OrderedDict with key = element name (e.g. 'H' or 'Fe') and value = (a number).  The first
    entry is H and the next is He, etc on up the periodic table until PhysicsBasics.MAXELEMENT

    :param InputType: Is either 'Counts', 'At %', or 'Wt %'
    """

    # Start with a blank report.
    ReportStr = ''

    # For every element that is in the sample (non-zero abundance), we are going to include it in the result.

    # Comprehend all the zero-abundance elements out.
    Q = OrderedDict([(El, Abund) for (El, Abund) in Quant.items() if Abund > 0])

    # Now let's print out each element
    SumAbundance = 0
    ReportStr += 'Input data:\n'.format()
    ReportStr += '{:<8s} {:>15s}\n'.format('Element', InputType)
    for El, Abund in Q.items():
        SumAbundance += Abund
        if Abund > 0.1:
            # Report straightforward percentages.
            ReportStr += '{:8s} {:15.3f}\n'.format(El, Abund)
        else:
            # For trace elements report ppm.
            ReportStr += '{:8s} {:11.0f} ppm\n'.format(El, Abund*1e4)
    # Report the sum.
    ReportStr += '{:8s} {:15.3f}\n'.format('Total:', SumAbundance)

    ReportStr += '\n'.format()

    return ReportStr

def FormatPhaseResults(FitResult, Residual, FitComposition):
    """FormatPhaseResults(FitResult, Residual): Generates human readable report strings for the reesults of
    fitting phases against the quantitative element abundances.

    :param FitComposition:
    :param FitResult: OrderedDict with key = phase name (e.g. 'Forsterite') and value = (Formula, mol%),
    where formula is a string and mol % is a float.
    :param Residual: A float giving the residual of the fit.
    """

    # Start with a blank report.
    ReportStr = ''

    ReportStr += 'Phase fit results:\n'.format()
    ReportStr += '{:<30s} {:>5s}\n'.format('Phase', 'Molar %')
    for Phase, Result in FitResult.items():
        ReportStr += '{:30s} {:5.3f}%\n'.format(Phase, Result[1])

    ReportStr += '{:30s} {:g}\n'.format('Fit residual', Residual)

    ReportStr += '\n'.format()

    # We also need to report new At%'s
    # Comprehend all the zero-abundance elements out.
    Q = OrderedDict([(El, Abund) for (El, Abund) in enumerate(FitComposition) if Abund > 0])

    # Now let's print out each element
    SumAbundance = 0
    ReportStr += 'Composition of phase fit:\n'.format()
    ReportStr += '{:<8s} {:>8s}\n'.format('Element', 'At %')
    for El, Abund in Q.items():
        SumAbundance += Abund
        if Abund > 0.1:
            # Report straightforward percentages.
            ReportStr += '{:8s} {:8.3f}\n'.format(pb.ElementalSymbols[El+1], Abund)
        else:
            # For trace elements report ppm.
            ReportStr += '{:8s} {:4.0f} ppm\n'.format(pb.ElementalSymbols[El+1], Abund*1e4)
    # Report the sum.
    ReportStr += '{:8s} {:8.3f}\n'.format('Total:', SumAbundance)

    ReportStr += '\n'.format()

    return ReportStr

if __name__ == '__main__':
    print(FormatQuantResults.__doc__)
