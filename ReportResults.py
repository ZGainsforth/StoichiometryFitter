""" ReportResults.py: Takes the quantification results and the results of the fitting of phases and produces human
    friendly outputs."""

__author__ = 'Zack Gainsforth'
__copyright__ = 'Copyright 2014, Zack Gainsforth'
__email__ = 'zsg@gainsforth.com'

from numpy import *
from collections import OrderedDict

import MyPython as mp
import PhysicsBasics as pb

def FormatQuantResults(Quant):
    """ReportQuantResults(Quant): Generates human readable report strings for the At% and Wt% results from the quant.

    :param Quant: An OrderedDict with key = element name (e.g. 'H' or 'Fe') and value = (At%, Wt %).  The first
    entry is H and the next is He, etc on up the periodic table until PhysicsBasics.MAXELEMENT
    """
    # TODO implement output for Ox Wt %.
    # TODO implement ppm reporting for elements below 0.1 wt%.

    # Start with a blank report.
    ReportStr = ''

    # For every element that is in the sample (non-zero abundance), we are going to include it in the result.

    # Comprehend all the zero-abundance elements out.
    Q = OrderedDict([(El, Abund) for (El, Abund) in Quant.iteritems() if Abund[0] > 0])

    # Now let's print out each element
    ReportStr += '{:8s} {:>8s} {:>8s}\n'.format('Element', 'At%', 'Wt%')
    for El, Abund in Q.iteritems():
        if Abund[1] > 0.1:
            # Report straightforward percentages.
            ReportStr += '{:8s} {:8.3f} {:8.3f}\n'.format(El, Abund[0], Abund[1])
        else:
            # For trace elements report ppm.
            ReportStr += '{:8s} {:4.0f} ppm {:4.0f} ppm\n'.format(El, Abund[0]*1e4, Abund[1]*1e4)

    return ReportStr

if __name__ == '__main__':
    print FormatQuantResults.__doc__