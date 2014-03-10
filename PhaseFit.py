""" PhaseFit.py: Uses the quantified composition from the EDS spectrum to determine what mineral(s) are the best fit.
    For example, in the case of MgFeSiO4, it would determine that this is a good fit for olivine and that it would be Fo50."""

__author__ = 'Zack Gainsforth'
__copyright__ = 'Copyright 2014, Zack Gainsforth'
__email__ = 'zsg@gainsforth.com'

from numpy import *
import MyPython as mp
import PhysicsBasics as pb

#def BuildPhaseMatrix()