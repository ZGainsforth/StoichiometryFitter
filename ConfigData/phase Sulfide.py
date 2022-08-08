
__author__ = 'Zack Gainsforth'
__copyright__ = 'Copyright 2014, Zack Gainsforth'
__email__ = 'zsg@gainsforth.com'

from numpy import *
if __name__ != '__main__':
    import PhysicsBasics as pb


def AnalyzePhase(AtPct=None, WtPct=None, OxWtPct=None, OByStoich=None):

    #Normalize our AtPct vector.
    AtPct = AtPct/sum(AtPct)*100

    # We output an output string which contains the analysis.
    OutStr = '--- Sulfide Analysis ---\n\n'

    # This analysis only knows about these elements:
    KnownElements = ['Fe', 'Ni', 'S', 'Se', 'Cr', 'Mn', 'Cu', 'Zn', 'Co']

    # If anything else accounts for more than 2 At % then note this
    OtherCations = 0
    for Zsub, ElAtPct in enumerate(AtPct):
        # If this is an unknown cation, and it has any abundance, add it to our cumulative abundance of unknowns.
        if ElAtPct > 0 and pb.ElementalSymbols[Zsub+1] not in KnownElements:
            OtherCations += ElAtPct

    if OtherCations > 2:
        OutStr += 'More than 2% of the atomic abundance is comprised by atoms other than: ' + ' '.join(KnownElements) + '.'
        OutStr += '\nTake care with interpretation.\n'

    E = dict()

    for Element in KnownElements:
        E[Element] = eval('AtPct[pb.%s-1]'%Element)

    Cations = (E['Fe']+E['Ni']+E['Cr']+E['Mn']+E['Cu']+E['Zn']+E['Co'])
    Anions = (E['S']+E['Se'])

    # Based on: Nakazawa, H., & Morimoto, N. (1971). Phase relations and superstructures of pyrrhotite, Fe1-xS. Materials Research Bulletin, 6(5), 345-357.

    if Cations/Anions > 1:
        NakazawaPhase = '(Too many cations)'
    elif Cations/Anions > 0.975:
        NakazawaPhase = 'Troilite: 2C'
    elif Cations/Anions > 0.965:
        NakazawaPhase = 'Pyrrhotite: 2C and disordered NC'
    elif Cations/Anions > 0.955:
        NakazawaPhase = 'Pyrrhotite: 2C and 6C'
    elif Cations/Anions > 0.945:
        NakazawaPhase = 'Pyrrhotite: 2C, 6C and metastable 4.5C'
    elif Cations/Anions > 0.935:
        NakazawaPhase = 'Pyrrhotite: 2C, 6C'
    elif Cations/Anions > 0.925:
        NakazawaPhase = 'Pyrrhotite: 5.8C and 4.4C'
    elif Cations/Anions > 0.915:
        NakazawaPhase = 'Pyrrhotite: disordered 5.5C'
    elif Cations/Anions > 0.905:
        NakazawaPhase = 'Pyrrhotite: disordered 5.3C and 3.8C'
    elif Cations/Anions > 0.895:
        NakazawaPhase = 'Pyrrhotite: 4.7C and 50A'
    elif Cations/Anions > 0.885:
        NakazawaPhase = 'Pyrrhotite: NA, 4C, MC (M=3.2)'
    elif Cations/Anions > 0.875:
        NakazawaPhase = 'Pyrrhotite: NA, 4C, MC (M=3.2)'
    elif Cations/Anions > 0.865:
        NakazawaPhase = 'Pyrrhotite: Fe7S8 (4C)'
    else:
        NakazawaPhase = '(Too few cations)'


    # Report the atom ratios.
    OutStr += '(Fe+Ni)/S = %0.3f\n' % ((E['Fe']+E['Ni'])/E['S'])
    if E['Ni'] > 0:
        OutStr += 'Ni/Fe = %0.3f, %0.3f X chondritic\n' % (E['Ni']/E['Fe'], (E['Ni']/E['Fe'])/float('5.751E-2'))
    if E['Se'] > 0:
        OutStr += 'S/Se = %0.3f, %0.3f X chondritic\n' % (E['S']/E['Se'], (E['S']/E['Se'])/float('6.344E+3'))
    if E['Cr'] > 0:
        OutStr += 'Cr/Fe = %0.3f, %0.3f X chondritic\n' % (E['Cr']/E['Fe'], (E['Cr']/E['Fe'])/float('1.564E-2'))
    if E['Mn'] > 0:
        OutStr += 'Mn/Fe = %0.3f, %0.3f X chondritic\n' % (E['Mn']/E['Fe'], (E['Mn']/E['Fe'])/float('1.084E-2'))
    if E['Cu'] > 0:
        OutStr += 'Cu/Fe = %0.3f, %0.3f X chondritic\n' % (E['Cu']/E['Fe'], (E['Cu']/E['Fe'])/float('6.036E-4'))
    if E['Zn'] > 0:
        OutStr += 'Zn/Fe = %0.3f, %0.3f X chondritic\n' % (E['Zn']/E['Fe'], (E['Zn']/E['Fe'])/float('1.478E-3'))
    OutStr += '(Fe+Ni+Cr+Mn+Cu+Zn+Co)/(S+Se) = %0.3f\n' % (Cations/Anions)
    OutStr += 'Probable superlattice at room temperature: %s\n' % (NakazawaPhase)
    OutStr += 'Ref: Nakazawa, H., & Morimoto, N. (1971). Phase relations and superstructures of pyrrhotite, Fe1-xS. Materials Research Bulletin, 6(5), 345-357.\n'

    return OutStr
    
if __name__ == '__main__':

    import imp
    pb = imp.load_source('PhysicsBasics', '../PhysicsBasics.py')

    AtPct = zeros(pb.MAXELEMENT)
    AtPct[pb.S-1] = 50
    AtPct[pb.Fe-1] = 50
    print('Troilite: FeS\n')
    print(AnalyzePhase(AtPct))

    AtPct = zeros(pb.MAXELEMENT)
    AtPct[pb.S-1] = 8
    AtPct[pb.Fe-1] = 7
    print('Pyrrhotite: Fe7S8\n')
    print(AnalyzePhase(AtPct))

    AtPct = zeros(pb.MAXELEMENT)
    AtPct[pb.S-1] = 8
    AtPct[pb.Fe-1] = 6
    print('Not enough cations\n')
    print(AnalyzePhase(AtPct))

    AtPct = zeros(pb.MAXELEMENT)
    AtPct[pb.S-1] = 8
    AtPct[pb.Fe-1] = 9
    print('Too many cations\n')
    print(AnalyzePhase(AtPct))

    AtPct = zeros(pb.MAXELEMENT)
    AtPct[pb.S-1] = 7.9
    AtPct[pb.Fe-1] = 7
    AtPct[pb.Ni-1] = 0.1
    AtPct[pb.Cr-1] = 0.1
    AtPct[pb.Mn-1] = 0.1
    AtPct[pb.Cu-1] = 0.1
    AtPct[pb.Zn-1] = 0.1
    AtPct[pb.Se-1] = 0.1

    print('A bit of everything (Cation)7.5(Anion)8\n')
    print(AnalyzePhase(AtPct))
