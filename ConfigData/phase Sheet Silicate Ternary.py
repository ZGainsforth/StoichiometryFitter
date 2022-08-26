
__author__ = 'Zack Gainsforth'
__copyright__ = 'Copyright 2014, Zack Gainsforth'
__email__ = 'zsg@gainsforth.com'

import numpy as np
if __name__ != '__main__':
    import PhysicsBasics as pb
from ternary_diagram import TernaryDiagram
import matplotlib.pyplot as plt

def norm(x):
    return x / np.sum(x)

def AnalyzePhase(AtPct=None, WtPct=None, OxWtPct=None, OByStoich=None):
    """ Sheet silicate ternary diagrams
    """

    #Normalize our AtPct vector.
    AtPct = AtPct/np.sum(AtPct)*100

    # We output an output string which contains the analysis.
    OutStr = '--- Sheet Silicate Ternary Diagrams ---\n\n'

    # This analysis only knows about these elements:
    KnownElements = ['H', 'O', 'Na', 'Mg', 'Al', 'Si', 'K', 'Ca', 'Ti', 'Cr', 'Mn', 'Fe', 'Ni']

    # # Define which atoms are supposed to go in octahedral and tetrahedral sites.
    OctahedralAtoms = ['Mg', 'Ti', 'Cr', 'Mn', 'Fe', 'Ni']
    TetrahedralAtoms = ['Al', 'Si']
    InterstitialAtoms = ['Na', 'K', 'Ca']

    # Calculate the At% values of the octahedral, tetrahedral and interstitial atoms.
    OctAtPct = 0; TetAtPct = 0; InterAtPct = 0
    for Element in OctahedralAtoms:
        OctAtPct += eval('AtPct[pb.%s-1]/AtPct[pb.O-1]*9'%Element)
    for Element in TetrahedralAtoms:
        TetAtPct += eval('AtPct[pb.%s-1]/AtPct[pb.O-1]*9'%Element)
    for Element in InterstitialAtoms:
        InterAtPct += eval('AtPct[pb.%s-1]/AtPct[pb.O-1]*9'%Element)

    # --------------- DIAGRAM 1 (Si+Al), Fe, Mg --------------- 

    # Calculate the (Si+Al), Fe, Mg diagram.
    CompoVector = [0,0,0] # Si+Al, Fe, Mg
    CompoVector[0] = AtPct[pb.Si-1] + AtPct[pb.Al-1]
    CompoVector[1] = AtPct[pb.Fe-1]
    CompoVector[2] = AtPct[pb.Mg-1]
    CompoVector /= np.sum(CompoVector)

    td = TernaryDiagram(['Si+Al', 'Fe', 'Mg'])
    # Draw serpentine and saponite boundary lines on the ternary.
    td.plot([norm([2,3,0]), norm([2,0,3])], color='green', linewidth=3, linestyle='dotted')
    td.annotate('Serpentine', [norm([1.5,1.6,1.4])], ha='center', fontsize='large',color='green')
    td.plot([norm([4,3,0]), norm([4,0,3])], color='royalblue', linewidth=3, linestyle='dotted')
    td.annotate('Saponite', [norm([4,1.6,1.4])], ha='center', fontsize='large', color='royalblue')
    # Now mark the user's point.
    td.scatter([ CompoVector ], marker='X', s=300, alpha=0.7, color='orange') #, annotations=['Experimental'])

    # --------------- Tetrahedrals, Octahedrals, Interstitial --------------- 
    plt.figure()

    # Calculate the Tetrahedrals, Octahedrals, Interstitial.
    # TMs = transition metals.
    CompoVector = [0,0,0] # Tets, Octs, O
    CompoVector[0] = TetAtPct
    CompoVector[1] = OctAtPct 
    CompoVector[2] = InterAtPct*10
    CompoVector /= np.sum(CompoVector)

    td = TernaryDiagram([f'Tetrahedral\n({", ".join(TetrahedralAtoms)})', f'Octahedral\n(Mg, Fe, ...)', f'Interstitial\n({", ".join(InterstitialAtoms)}) x 10'])
    # Draw serpentine and saponite boundary lines on the ternary.
    td.scatter([norm([2,3,0])], marker='s', s=300, alpha=0.7, color='green')
    td.annotate('Serpentine', [norm([2,3,0])], ha='center', fontsize='large', color='green')
    td.plot([norm([4,3,0.25*10]), norm([4,3,0.6*10])], color='royalblue', linewidth=5, linestyle='solid', alpha=0.7)
    td.annotate('Saponite', [norm([3.5,3.5,5])], rotation=-35, ha='center', fontsize='large', color='royalblue')
    # Now mark the user's point.
    td.scatter([ CompoVector ], marker='d', s=300, alpha=0.7, color='orange') #, annotations=['Experimental'])


    plt.show()

    # # Compute how many cations in the Oct sites.
    # Oct = sum(array([e for e in list(E.values())])) - E['O'] - E['H'] - E['Si'] - E['Al']

    # # Tet should be Si and Al.
    # Tet = E['Si'] - E['Al']

    # # Report the compositional ratios
    # OutStr += 'Mg/(Mg+Fe) = %0.3f\n' % (E['Mg']/(E['Mg']+E['Fe']))
    # OutStr += 'Al/(Al+Si) = %0.3f\n' % (E['Al']/(E['Al']+E['Si']))
    # for e in KnownElements:
    #     if e in ['H', 'O', 'Si', 'Al']:
    #         continue
    #     if E[e] != 0:
    #         OutStr += e + '/(Octahedral) = %0.3f\n' % (E[e]/Oct)

    # OutStr += '\n'
    # OutStr += 'Octahedral atoms per 18 atoms:\n'
    # OutStr += '{:>11s}:    {:<10s}\n'.format('Element', '#')
    # CationSum = 0
    # for ElName in KnownElements:
    #     if (ElName in OctahedralAtoms) and (OriginalE[ElName] != 0):
    #         CationSum += OriginalE[ElName]
    #         if OriginalE[ElName] < 0.01:
    #             # Handle ppm levels gracefully.
    #             OutStr += '{:>11s}:    {:<1.3f}'.format(ElName, OriginalE[ElName])
    #             OutStr += ', {:>11s}:    {:<4.0f} * 10^-6\n'.format(ElName, OriginalE[ElName]*1e6)
    #         else:
    #             OutStr += '{:>11s}:    {:<1.3f}\n'.format(ElName, OriginalE[ElName])
    # OutStr += '{:>11s}:    {:<1.3f}\n'.format('Total Cats', CationSum)
    # OutStr += 'Serpentine formula should have 3 octahedral atoms.\n'

    # OutStr += '\n'
    # OutStr += 'Tetrahedral atoms per 18 atoms:\n'
    # OutStr += '{:>11s}:    {:<10s}\n'.format('Element', '#')
    # CationSum = 0
    # for ElName in KnownElements:
    #     if (ElName in TetrahedralAtoms) and (OriginalE[ElName] != 0):
    #         CationSum += OriginalE[ElName]
    #         if OriginalE[ElName] < 0.01:
    #             # Handle ppm levels gracefully.
    #             OutStr += '{:>11s}:    {:<1.3f}'.format(ElName, OriginalE[ElName])
    #             OutStr += ', {:>11s}:    {:<4.0f} * 10^-6\n'.format(ElName, OriginalE[ElName]*1e6)
    #         else:
    #             OutStr += '{:>11s}:    {:<1.3f}\n'.format(ElName, OriginalE[ElName])
    # OutStr += '{:>11s}:    {:<1.3f}\n'.format('Total Cats', CationSum)
    # OutStr += 'Serpentine formula should have 2 tetrahedral atoms.\n'

    # OutStr += '\n'
    # OutStr += 'Atoms per 18 atoms:\n'
    # OutStr += '{:>11s}:    {:<10s}\n'.format('Element', '#')
    # CationSum = 0
    # for ElName in KnownElements:
    #     if OriginalE[ElName] != 0:
    #         CationSum += OriginalE[ElName]
    #         if OriginalE[ElName] < 0.01:
    #             # Handle ppm levels gracefully.
    #             OutStr += '{:>11s}:    {:<1.3f}'.format(ElName, OriginalE[ElName])
    #             OutStr += ', {:>11s}:    {:<4.0f} * 10^-6\n'.format(ElName, OriginalE[ElName]*1e6)
    #         else:
    #             OutStr += '{:>11s}:    {:<1.3f}\n'.format(ElName, OriginalE[ElName])
    # OutStr += '{:>11s}:    {:<1.3f}\n'.format('Total Cats', CationSum)
    # OutStr += 'Serpentine formula is Oct3 Tet2 O9 H4\n'
    # OutStr += 'Serpentine formula is Oct3 Tet2 O5 OH4\n'
    # OutStr += 'Tet is Al or Si, occasionally Fe can be included (not considered here)\n'
    # OutStr += 'All other cations go in the octahedral sites.\n'

    return '' #OutStr
    
if __name__ == '__main__':

    import imp
    pb = imp.load_source('PhysicsBasics', '../PhysicsBasics.py')

    # AtPct = np.zeros(pb.MAXELEMENT)
    # AtPct[pb.H-1] = 4
    # AtPct[pb.O-1] = 9
    # AtPct[pb.Mg-1] = 3
    # AtPct[pb.Si-1] = 2
    # print('Serpentine: Mg3 Si2 O5 (OH)4:\n')
    # print(AnalyzePhase(AtPct))

    AtPct = np.zeros(pb.MAXELEMENT)
    AtPct[pb.O-1] = 12
    AtPct[pb.Mg-1] = 0.7*3
    AtPct[pb.Al-1] = 1
    AtPct[pb.Si-1] = 3
    AtPct[pb.Ca-1] = 0.25
    AtPct[pb.Fe-1] = 0.3*3
    print('Saponite: Ca0.25 (Fe0.3,Mg0.7)3 (Si0.75,Al0.25)4 O10 (OH)2 0H2O:\n')
    print(AnalyzePhase(AtPct))

    # AtPct = np.zeros(pb.MAXELEMENT)
    # AtPct[pb.O-1] = 12 + 4
    # AtPct[pb.Mg-1] = 0.5*3
    # AtPct[pb.Na-1] = 0.7*0.3
    # AtPct[pb.Al-1] = 1
    # AtPct[pb.Si-1] = 3
    # AtPct[pb.Ca-1] = 0.5*0.3
    # AtPct[pb.Fe-1] = 0.3*3
    # print('Saponite: (Na0.5,Ca0.5)0.3 (Fe0.3,Mg0.7)3 (Si0.75,Al0.25)4 O10 (OH)2 4H2O:\n')
    # print(AnalyzePhase(AtPct))

