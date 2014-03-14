from __future__ import division
#numpy.set_printoptions(threshold=numpy.nan) # Makes arrays print fully when they are large.
from collections import OrderedDict

# Planck's constant [eV-s]
h = 4.135667517e-15;
#h = 6.626068e-34 ; %SI
# Classical electron radius [m]
r0 = 2.8179403268e-15;
# Speed-o-light m/s
c = 299792458;
# Avogadro's number [mol-1]
NAvogadro = 6.02214129e23;
# Electron charge
q = 1.60217646e-19;

# Define symbols for easy indexing.
H = 1;
He = 2;
Li = 3;
Be = 4;
B = 5;
C = 6;
N = 7;
O = 8;
F = 9;
Ne = 10;
Na = 11;
Mg = 12;
Al = 13;
Si = 14;
P = 15;
S = 16;
Cl = 17;
Ar = 18;
K = 19;
Ca = 20;
Sc = 21;
Ti = 22;
V = 23;
Cr = 24;
Mn = 25;
Fe = 26;
Co = 27;
Ni = 28;
Cu = 29;
Zn = 30;
Ga = 31;
Ge = 32;
As = 33;
Se = 34;
Br = 35;
Kr = 36;
Rb = 37;
Sr = 38;
Y = 39;
Zr = 40;
Nb = 41;
Mo = 42;
Tc = 43;
Ru = 44;
Rh = 45;
Pd = 46;
Ag = 47;
Cd = 48;
In = 49;
Sn = 50;
Sb = 51;
Te = 52;
I = 53;
Xe = 54;
Cs = 55;
Ba = 56;
La = 57;
Ce = 58;
Pr = 59;
Nd = 60;
Pm = 61;
Sm = 62;
Eu = 63;
Gd = 64;
Tb = 65;
Dy = 66;
Ho = 67;
Er = 68;
Tm = 69;
Yb = 70;
Lu = 71;
Hf = 72;
Ta = 73;
W = 74;
Re = 75;
Os = 76;
Ir = 77;
Pt = 78;
Au = 79;
Hg = 80;
Tl = 81;
Pb = 82;
Bi = 83;
Po = 84;
At = 85;
Rn = 86;
Fr = 87;
Ra = 88;
Ac = 89;
Th = 90;
Pa = 91;
U = 92;
Np = 93;
Pu = 94;
Am = 95;
Cm = 96;
Bk = 97;
Cf = 98;
Es = 99;
Fm = 100;
Md = 101;
No = 102;
Lr = 103;
Rf = 104;
Db = 105;
Sg = 106;
Bh = 107;
Hs = 108;
Mt = 109;
Ds = 110;
Rg = 111;
Cn = 112;
Uut = 113;
Fl = 114;
Uup = 115;
Lv = 116;
Uus = 117;
Uuo = 118;

MAXELEMENT = 118

# ELEMENT PROPERTIES:
# Each of these vectors is indexed by the atomic number.  For example, the density of iron metal is rho(26).
# Element names
ElementalSymbols = ['None', 'H', 'He', 'Li', 'Be', 'B', 'C', 'N', 'O', 'F', 'Ne', 'Na', 'Mg', 'Al', 'Si', 'P', 'S', 'Cl', 'Ar', 'K', 'Ca', 
                    'Sc', 'Ti', 'V', 'Cr', 'Mn', 'Fe', 'Co', 'Ni', 'Cu', 'Zn', 'Ga', 'Ge', 'As', 'Se', 'Br', 'Kr', 'Rb', 'Sr', 
                    'Y', 'Zr', 'Nb', 'Mo', 'Tc', 'Ru', 'Rh', 'Pd', 'Ag', 'Cd', 'In', 'Sn', 'Sb', 'Te', 'I', 'Xe', 'Cs', 'Ba', 
                    'La', 'Ce', 'Pr', 'Nd', 'Pm', 'Sm', 'Eu', 'Gd', 'Tb', 'Dy', 'Ho', 'Er', 'Tm', 'Yb', 'Lu', 'Hf', 'Ta', 'W', 
                    'Re', 'Os', 'Ir', 'Pt', 'Au', 'Hg', 'Tl', 'Pb', 'Bi', 'Po', 'At', 'Rn', 'Fr', 'Ra', 'Ac', 'Th', 'Pa', 'U', 'Np', 'Pu',
                    'Am', 'Cm', 'Bk', 'Cf', 'Es', 'Fm', 'Md', 'No', 'Lr', 'Rf', 'Db', 'Sg', 'Bh', 'Hs', 'Mt', 'Ds', 'Rg', 'Cn', 
                    'Uut', 'Fl', 'Uup', 'Lv', 'Uus', 'Uuo']

                    
# Element densities
ElementalRho = [0, 8.99E-05, 1.79E-04, 0.534, 1.848, 2.34, 2.26, 1.25E-03, 1.43E-03, 1.70E-03, 9.00E-04, 0.971, 1.738, 2.702, 2.33, 1.82, 2.07, 
       3.21E-03, 1.78E-03, 0.862, 1.55, 2.99, 4.54, 6.11, 7.19, 7.43, 7.874, 8.9, 8.9, 8.96, 7.13, 5.907, 5.323, 5.72, 4.79, 3.119, 
       3.75E-03, 1.63, 2.54, 4.47, 6.51, 8.57, 10.22, 11.5, 12.37, 12.41, 12.02, 10.5, 8.65, 7.31, 7.31, 6.684, 6.24, 4.93, 5.90E-03, 
       1.873, 3.59, 6.15, 6.77, 6.77, 7.01, 7.3, 7.52, 5.24, 7.895, 8.23, 8.55, 8.8, 9.07, 9.32, 6.9, 9.84, 13.31, 16.65, 19.35, 
       21.04, 22.6, 22.4, 21.45, 19.32, 13.546, 11.85, 11.35, 9.75, 9.3, 9.73E-03, 5.5, 10.07, 11.724, 15.4, 18.95, 20.2, 19.84, 
       13.67, 13.5, 14.78, 15.1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0];
       
# Element weights (for wt%)
ElementalWeights = [0, 1.00794, 4.002602, 6.941, 9.012182, 10.811, 12.0107, 14.0067, 15.9994, 18.9984032, 20.1797, 22.98976928, 24.3050, 
       26.9815386, 28.0855, 30.973762, 32.065, 35.453, 39.948, 39.0983, 40.078, 44.955912, 47.867, 50.9415, 51.9961, 54.938045, 
       55.845, 58.933195, 58.6934, 63.546, 65.409, 69.723, 72.64, 74.92160, 78.96, 79.904, 83.798, 85.4678, 87.62, 88.90585, 
       91.224, 92.906, 95.94, 981, 101.07, 102.905, 106.42, 107.8682, 112.411, 114.818, 118.710, 121.760, 127.60, 126.904, 
       131.293, 132.9054519, 137.327, 138.90547, 140.116, 140.90765, 144.242, 145.1, 150.36, 151.964, 157.25, 158.92535, 162.500, 
       164.930, 167.259, 168.93421, 173.04, 174.967, 178.49, 180.94788, 183.84, 186.207, 190.23, 192.217, 195.084, 196.966569, 
       200.59, 204.3833, 207.2, 208.98040, 210, 210, 220, 223, 226, 227, 231.03588, 232.03806, 237, 238.02891, 243, 
       244, 247, 247, 251, 0, 0, 0, 259, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0];

# And the end all cooleset thing in the world is an ordered dictionary that has El: Z, weight
ElementDict= OrderedDict(zip(ElementalSymbols, zip(range(0, MAXELEMENT), ElementalWeights)))