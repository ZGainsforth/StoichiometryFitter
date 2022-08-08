
__author__ = 'Zack Gainsforth'
__copyright__ = 'Copyright 2014, Zack Gainsforth'
__email__ = 'zsg@gainsforth.com'

from numpy import *
from collections import *
if __name__ != '__main__':
    import PhysicsBasics as pb


def AnalyzePhase(AtPct=None, WtPct=None, OxWtPct=None, OByStoich=None):

    #Normalize our AtPct vector.
    AtPct = AtPct/sum(AtPct)*100

    # We output an output string which contains the analysis.
    OutStr = '--- Pyroxene Analysis ---\n\n'

    # This analysis only knows about these elements:
    KnownElements = ['O', 'Na', 'K', 'S', 'Si', 'Al', 'Fe', 'Ni', 'Ti', 'Cr', 'V', 'Zr', 'Sc', 'Zn', 'Mg', 'Mn', 'Li', 'Ca', 'Cl']

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

    # # Convert from At% to atoms assuming 10 atoms basis.
    # for Element in KnownElements:
    #     E[Element] = eval('AtPct[pb.%s-1]/100*10'%Element)
    # Convert from At% to cations assuming 6 oxygens.
    for Element in KnownElements:
        E[Element] = eval('AtPct[pb.%s-1]/AtPct[pb.O-1]*6'%Element)
    
    summmm = 0
    for x in list(E.values()):
        summmm += x
    Cations = summmm - E['O']
    Anions = E['O']

    # Based on: Morimoto, N., Fabries, J., Ferguson, A. K., Ginzburg, I. V., Ross, M., Seifert, F. A., et al. (1988). Nomenclature of pyroxenes. American Mineralogist, 73, 1123-1133.

    # If the cation/O ratio is off by more than 2%, then warn the user.
    if Cations/Anions > 2./3*1.02:
        OutStr += '(Too many cations, non-stoichiometric)\n'
    elif Cations/Anions < 2./3*0.98:
        OutStr += '(Too few cations, non-stoichiometric)\n'

    #OriginalTotalCations = E['Si'] + E['Ti'] + E['Al'] + E['Mn'] + E['Mg'] + E['Ca'] + E['Ni'] + E['Zn'] + E['Cr'] + E['V'] + E['Fe']
    OriginalTotalCations = sum([e for (k, e) in list(E.items()) if k in KnownElements if k != 'O'])
    # For the stoichiometry calculation to work, we have to have EXACTLY 4 cations (10 atom basis).  So make it so, but we will keep the original number for reporting.
    for i in KnownElements:
        E[i] *= 4/OriginalTotalCations

    # Report the En type stuff.
    # First, assume M1+M2 = everything except O, Si and Al.
    M1M2sum = sum([e for (k, e) in list(E.items()) if k in KnownElements]) - E['O'] - E['Al'] - E['Si']
    OutStr += 'Mg/(Mg+Fe) = %0.3f\n' % (E['Mg']/(E['Mg']+E['Fe']))
    Cationtally = 0
    for e in KnownElements:
        if e in ['O', 'Si', 'Al']:
            continue
        if E[e] != 0:
            OutStr += e + '/(M1+M2) = %0.3f\n' % (E[e]/M1M2sum)
            Cationtally += E[e]/M1M2sum

    OutStr += 'Assumed M1+M2 = %0.3f which is everything except O, Si and Al\n\n' % Cationtally

    ECatsPerOxygen = E.copy()

    # We already did stoichiometry so cations/6 oxy can be ratioed against the O exactly.
    for Element in KnownElements:
        ECatsPerOxygen[Element] = eval('AtPct[pb.%s-1]/AtPct[pb.O-1]*6'%Element)

    OutStr += '\n'
    OutStr += 'Cations per 6 oxygens:\n'
    OutStr += '{:>11s}:    {:<10s}\n'.format('Element', '#')
    CationSum = 0
    for ElName in KnownElements:
        if ElName != 'O' and ECatsPerOxygen[ElName] != 0:
            CationSum += ECatsPerOxygen[ElName]
            if E[ElName] < 0.01:
                # Handle ppm levels gracefully.
                OutStr += '{:>11s}:    {:<1.3f}'.format(ElName, ECatsPerOxygen[ElName])
                OutStr += ', {:>11s}:    {:<4.0f} * 10^-6\n'.format(ElName, ECatsPerOxygen[ElName]*1e6)
            else:
                OutStr += '{:>11s}:    {:<1.3f}\n'.format(ElName, ECatsPerOxygen[ElName])
    OutStr += '{:>11s}:    {:<1.3f}\n'.format('Total Cats', CationSum)
    OutStr += 'Ideal number of cats is 4.\n\n'


    # Build the site occupancies.
    # T site gets all the Si, and then as much Al3+ and Fe3+ as necessary to fill it up.
    SiT = E['Si']
    Tdeficit = 2-E['Si']

    # Now we will put in as much Al as possible into the tetrahedral site, the rest goes in M1.
    if Tdeficit < 0:
        AlT = 0
        AlM1 = E['Al']
    elif Tdeficit >= E['Al']:
        AlT = E['Al'] # All Al is tetrahedral.
        AlM1 = 0      # None in M1.
        Tdeficit -= AlT
    else:
        AlT = Tdeficit  # As much as we can.
        AlM1 = E['Al']-Tdeficit # The rest goes in M1.
        Tdeficit = 0

    # Put in as much Fe as possible into the tetrahedral site, the rest goes in M1.
    if Tdeficit < 0:
        FeT = 0
        FeM1 = E['Fe']
    elif Tdeficit >= E['Fe'] and Tdeficit > 0:
        FeT = E['Fe'] # All Fe is 3+ and tetrahedral.
        FeM1 = 0      # None in M1.
        Tdeficit -= AlT
    else:
        FeT = Tdeficit  # As much as we can.
        FeM1 = E['Fe']-Tdeficit # The rest goes in M1.
        Tdeficit = 0

    # And the tetrahedral occupancy is:
    T = SiT + AlT + FeT

    # Now we move to M1.
    # These atoms go exclusively into the M1 site.
    TiM1 = E['Ti']
    CrM1 = E['Cr']
    VM1 = E['V']
    ZrM1 = E['Zr']
    ScM1 = E['Sc']
    ZnM1 = E['Zn']

    M1 = AlM1 + TiM1 + CrM1 + VM1 + ZrM1 + ScM1 + ZnM1
    M1deficit = 1-M1

    # Fe is the only atom that can go in all three sites, so we have to see if we need to split M1 and M2 Fe now.
    if M1deficit >= FeM1:
        # All the Fe is in M1.
        M1deficit -= FeM1
        FeM2 = 0
    else:
        FeM2 = FeM1 - M1deficit
        FeM1 = FeM2
        M1deficit = 0

    # Recompute occupancy and deficit.
    M1 += FeM1
    M1deficit = 1-M1

    # Now we put as much Mg as fits.
    MgM1 = E['Mg']
    MgM2 = 0
    if M1deficit >= MgM1:
        # All the Mg is in M1.
        M1deficit -= MgM1
    else:
        MgM2 = MgM1 - M1deficit
        MgM1 -= MgM2
        M1deficit = 0

    # Recompute occupancy and deficit.
    M1 += MgM1
    M1deficit = 1-M1

    # Now we put as much Mn as fits.
    MnM1 = E['Mn']
    MnM2 = 0
    if M1deficit >= MnM1:
        # All the Mg is in M1.
        M1deficit -= MnM1
    else:
        MnM2 = MnM1 - M1deficit
        MnM1 -= MnM2
        M1deficit = 0

    # Recompute M1 occupancy
    M1 = AlM1 + FeM1 + TiM1 + CrM1 + VM1 + ZrM1 + ScM1 + ZnM1 + MgM1 + MnM1

    # M1 is done.  Move to M2.
    # Li, Ca and Na are always in M2.
    LiM2 = E['Li']
    CaM2 = E['Ca']
    NaM2 = E['Na']

    # Populate M2
    M2 = FeM2 + MgM2 + MnM2 + LiM2 + CaM2 + NaM2
    M2deficit = 1-M2

    # Finally we just have to balance charge.  We can shift Fe2+/3+ and Ti3+/4+ to do this.

    TCharge = SiT*4 + AlT*3 + FeT*3
    TChargeDeficit = 2*4 - TCharge

    M2Charge = MgM2*2 + FeM2*2 + MnM2*2 + LiM2 + CaM2*2 + NaM2
    M2ChargeDeficit = 2 - M2Charge

    # M1 will have a charge excess to offset T and M2 deficits.
    # Compute M1 charges with nominal oxidation states.
    M1Charge = (AlM1 + CrM1 + VM1 + ScM1)*3 + (TiM1 + ZrM1)*4 + (ZnM1 + MgM1 + MnM1 + FeM1)*2
    M1ChargeDeficit = 2 + M2ChargeDeficit + TChargeDeficit - M1Charge

    # Notice we start this assumption with all Fe2+ and Ti4+
    # We also assume that all Fe is 2+ if there is any conversion from Ti4+ to Ti3+.
    # Likewise, all Ti is 4+ if there is any conversion from Fe2+ to Fe3+.

    # If we already have too much charge in M1, then the Ti must be 3+
    if M1ChargeDeficit < 0:
        M1ChargeExcess = -M1ChargeDeficit
        Fe3_M1 = 0
        Fe2_M1 = FeM1
        if TiM1 >= M1ChargeExcess:
            Ti3_M1 = M1ChargeExcess
            Ti4_M1 = TiM1 - Ti3_M1
        elif TiM1 < M1ChargeExcess:
            Ti3_M1 = TiM1
            Ti4_M1 = 0
    else:
        # For this case, we will turn as much Fe to 3+ as needed.
        Ti3_M1 = 0
        Ti4_M1 = TiM1
        if FeM1 >= M1ChargeDeficit:
            Fe3_M1 = M1ChargeDeficit
            Fe2_M1 = FeM1 - Fe3_M1
        elif FeM1 < M1ChargeDeficit:
            Fe3_M1 = FeM1
            Fe2_M1 = 0

    # Recompute M1 charge...
    M1Charge = (AlM1 + CrM1 + VM1 + ScM1 + Fe3_M1 + Ti3_M1)*3 + (Ti4_M1 + ZrM1)*4 + (ZnM1 + MgM1 + MnM1 + Fe2_M1)*2

    PrintIfNonzero = lambda k, v: '{:>11s}:    {:<1.3f}\n'.format(k, v) if v != 0 else ''

    OutStr += 'Assuming exactly 4 cations and compute to fill sites and balance charge:\n'
    OutStr += 'Site T (tetrahedral):\n'
    OutStr += '{:>11s}:    {:<10s}\n'.format('Element', 'Occupancy')
    for k, v in list(OrderedDict((('Si4+', SiT),
                             ('Al3+', AlT),
                             ('Fe3+', FeT))).items()):
        OutStr += PrintIfNonzero(k,v)
    OutStr += '{:>11s}:    {:<1.3f}\n'.format('Total occ', T)
    OutStr += '{:>11s}:    {:<1.3f}\n'.format('Charge', TCharge)
    OutStr += '\n'
    OutStr += 'Site M1 (octahedral):\n'
    OutStr += '{:>11s}:    {:<10s}\n'.format('Element', 'Occupancy')
    for k, v in list(OrderedDict((('Al3+', AlM1),
                             ('Fe3+', Fe3_M1),
                             ('Ti3+', Ti3_M1),
                             ('Cr3+', CrM1),
                             ('V3+', VM1),
                             ('Ti4+', Ti4_M1),
                             ('Zr4+', ZrM1),
                             ('Sc3+', ScM1),
                             ('Zn2+', ZnM1),
                             ('Mg2+', MgM1),
                             ('Fe2+', Fe2_M1),
                             ('Mn2+', MnM1))).items()):
        OutStr += PrintIfNonzero(k,v)
    OutStr += '{:>11s}:    {:<1.3f}\n'.format('Total occ', M1)
    OutStr += '{:>11s}:    {:<1.3f}\n'.format('Charge', M1Charge)
    OutStr += '\n'
    OutStr += 'Site M2 (octahedral):\n'
    OutStr += '{:>11s}:    {:<10s}\n'.format('Element', 'Occupancy')
    for k, v in list(OrderedDict((('Mg2+', MgM2),
                             ('Fe2+', FeM2),
                             ('Mn2+', MnM2),
                             ('Li+', LiM2),
                             ('Ca2+', CaM2),
                             ('Na+', NaM2))).items()):
        OutStr += PrintIfNonzero(k,v)
    OutStr += '{:>11s}:    {:<1.3f}\n'.format('Total occ', M2)
    OutStr += '{:>11s}:    {:<1.3f}\n'.format('Charge', M2Charge)
    OutStr += '\n'
    OutStr += '{:>11s}:    {:<1.3f}\n'.format('Sum Sum Cat', OriginalTotalCations)#T+M1+M2)
    OutStr += '{:>11s}:    {:<1.3f}\n'.format('Sum Charge', TCharge+M1Charge+M2Charge)
    OutStr += '\n'
    OutStr += 'Ideal sum cations = 4, Ideal sum charge = 12\n'
    OutStr += 'Raw sum cat is the unnormalized sum of the cations.\n'
    OutStr += '\n'
    # OutStr += 'Cations per for oxygens:\n'
    # OutStr += '{:>11s}:    {:<10s}\n'.format('Element', '#')
    # for k,v in KnownElements
    #
    OutStr += '\n'
    OutStr += 'Ref: Morimoto, N., Fabries, J., Ferguson, A. K., Ginzburg, I. V., Ross, M., Seifert, F. A., et al. (1988). Nomenclature of pyroxenes. American Mineralogist, 73, 1123-1133.\n'
    OutStr += 'We assume oxidation priority: Ti3+ - Ti4+ - Fe2+ - Fe3+ (i.e. Ti3+ is only possible if all Fe is 2+, and Fe3+ is possible only with Ti4+).\n'

    return OutStr

if __name__ == '__main__':

    import imp
    pb = imp.load_source('PhysicsBasics', '../PhysicsBasics.py')

    AtPct = zeros(pb.MAXELEMENT)
    AtPct[pb.Mg-1] = 20
    AtPct[pb.Si-1] = 20
    AtPct[pb.O-1] = 60
    print('Enstatite: MgSiO3\n')
    print((AnalyzePhase(AtPct)))

    AtPct = zeros(pb.MAXELEMENT)
    AtPct[pb.Mg-1] = 10
    AtPct[pb.Ca-1] = 10
    AtPct[pb.Si-1] = 20
    AtPct[pb.O-1] = 60
    print('Diopside: CaMgSi2O6\n')
    print((AnalyzePhase(AtPct)))

    AtPct = zeros(pb.MAXELEMENT)
    AtPct[pb.Fe-1] = 20
    AtPct[pb.Si-1] = 20
    AtPct[pb.O-1] = 60
    print('Ferrisilite: Fe2Si2O6\n')
    print((AnalyzePhase(AtPct)))

    AtPct = zeros(pb.MAXELEMENT)
    AtPct[pb.Mg-1] = 10
    AtPct[pb.Fe-1] = 10
    AtPct[pb.Si-1] = 20
    AtPct[pb.O-1] = 60
    print('En50: FeMgSi2O6\n')
    print((AnalyzePhase(AtPct)))

    AtPct = zeros(pb.MAXELEMENT)
    AtPct[pb.Si-1] = 2.010
    AtPct[pb.Ti-1] = 0.019
    AtPct[pb.Al-1] = 0.017
    AtPct[pb.Cr-1] = 0.078
    AtPct[pb.Mg-1] = 0.797
    AtPct[pb.Ca-1] = 0.770
    AtPct[pb.Fe-1] = 0.250
    AtPct[pb.Na-1] = 0.113
    AtPct[pb.O-1] = 6
    print('Iris CPX SEM: CaMgSi2O6\n')
    print((AnalyzePhase(AtPct)))

    AtPct = zeros(pb.MAXELEMENT)
    AtPct[pb.Si-1] = 20.49
    AtPct[pb.Ti-1] = 0.18
    AtPct[pb.Al-1] = 0.24
    AtPct[pb.Cr-1] = 0.86
    AtPct[pb.Mg-1] = 7.14
    AtPct[pb.Ca-1] = 7.41
    AtPct[pb.Fe-1] = 1.93
    AtPct[pb.Na-1] = 1.51
    AtPct[pb.O-1] = 60.23
    print('Iris CPX TEM: CaMgSi2O6\n')
    print((AnalyzePhase(AtPct)))
