"""
This script constructs the file 'Detector Titan.csv'
"""
__author__ = 'Zack Gainsforth'
__copyright__ = 'Copyright 2016, Zack Gainsforth'
__email__ = 'zsg@gainsforth.com'

from numpy import *
from configparser import ConfigParser
from io import StringIO
import csv
import imp
import PhysicsBasics as pb
from collections import *

# The detector window and Si dead layer are encapsulated as absorption through a thin film of thickness tau,
# density rho and composition in Wt %'s determined from the actual window composition plus Si deadlayer.

# The Bruker software reports the detector coating as being 5 nm of Al, 85 nm of N, etc., and a Si dead layer of 80 nm.
# It doesn't really say what the densities of these elements are, or what is going on exactly.

# So I ASSUME:
# The thin film has a density of 1.4 which is typical for mylar or kapton etc.
# The thin film has At%'s propotional to the "thickness" of that element.

# For the Si dead layer, I know that the silicon density is 2.33 g/cm3

# It says there is a 1 nm Be layer, which is probably actually a coating on the polymer.  Density 1.85 g/cm3

El =  [      'Al', 'N', 'B', 'C', 'O', 'Si', 'Be']
tau = array([ 5.,    85,  6,   6,   65,  80,   1])
rho = array([1.4]*5 + [2.33, 1.85])
#rho = array([pb.ElementalRho[pb.ElementDict[it][0]] for it in El])
# El = ['Si']
# tau = array([80])
# rho = array([2.33])
ElWt = array([pb.ElementDict[it][1] for it in El])

ElMass = tau*rho

#Normalize it, and this is basically a wt% list
ElMass = ElMass/sum(ElMass)*100

# To make the rest easy, we'll dictionary the elements in the film.
ElDict = defaultdict(int, list(zip(El, ElMass)))

""" NOW PRODUCE A CSV FILE WHICH HAS ALL THIS INFO """
#tau is the total thickness, and convert nm to microns.
tautot = sum(tau)/1000
# rho is the mean rho, treating the thickness as a weight%
rhoave = sum((tau/sum(tau))*rho)
SavStr = '#tau=%f\n'% tautot
SavStr += '#rho=%f\n'% rhoave
SavStr += 'Element,Wt %\n'
for i in range(1, pb.MAXELEMENT+1):
    ElName = pb.ElementalSymbols[i]
    SavStr += '%s,%f\n' %(ElName, ElDict[ElName])

with open('ConfigData/Absorption Titan Detector Window.csv', 'w') as f:
    f.write(SavStr)

# ConfigParser.add_section('THIN FILM')
# ConfigParser.set('THIN FILM', 'TAU', tau)
# ConfigParser.set('THIN FILM', 'RHO', rho)
#
# s = StringIO()
# savetxt(s, ElMass)
#
# ConfigParser.s
## Lets add these to a Wt% vector
#
#WtPct = zeros(MAXELEMENT)
#print WtPct
#for i, v in enumerate(DetectorEl):
#    Z = ElementDict[v][0]
#    WtPct[Z-1] = DetectorCompo[i]
#    
#print WtPct
