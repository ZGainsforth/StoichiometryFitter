
__author__ = 'Zack Gainsforth'
__copyright__ = 'Copyright 2015, Zack Gainsforth'
__email__ = 'zsg@gainsforth.com'

import matplotlib
import matplotlib.pyplot as plt
from numpy import *
import os
import pickle
from scipy.stats import chisquare
try:
    import ternary
except:
    ternary = None
if __name__ != '__main__':
    import PhysicsBasics as pb

### Tweak the matplotlib settings to make a nice looking plot.
# Set the bold level.
boldlevel=3
FontSizeBasis = (boldlevel+2)*4    # Fonts get bigger as boldlevel increases
TickMajorBasis = boldlevel*4    # As fonts get bigger, they need a larger padding from the axis.
# Increase the size of the tick label fonts.
matplotlib.rc('xtick', labelsize=FontSizeBasis)
matplotlib.rc('ytick', labelsize=FontSizeBasis)
# Increase their padding.
matplotlib.rc('xtick.major', pad=TickMajorBasis)
matplotlib.rc('ytick.major', pad=TickMajorBasis)

def ShowLastPos(plt):
    # Call plt.show but pickles the plot position on window close.  When called a second time
    # it loads the figure to the last position.  So matplotlib now remembers figure positions!
    # This version works for QT and WX backends.

    backend = matplotlib.get_backend()

    FigNums = plt.get_fignums()

    for FigNum in FigNums:
        plt.figure(FigNum)
        fig=plt.gcf()
        fig.canvas.mpl_connect('close_event', RecordLastPos)
        mgr = plt.get_current_fig_manager()
        # WX backend
        if 'WX' in backend:
            try:
                with open('CurrentWindowPos%d.pkl'%FigNum, 'r') as f:
                    CurPos = pickle.load(f)
                mgr.window.SetPosition((CurPos[0], CurPos[1]))
                mgr.window.SetSize((CurPos[2], CurPos[3]))
            except:
                pass
        # QT backend.
        elif 'QT' in backend:
            try:
                with open('CurrentWindowPos%d.pkl'%FigNum, 'r') as f:
                    CurPos = pickle.load(f)
                mgr.window.setGeometry(CurPos[0], CurPos[1], CurPos[2], CurPos[3])
            except:
                pass
        else:
            print('Backend ' + backend + ' not supported.  Plot figure position will not be sticky.')

    plt.show()

def RecordLastPos(evt):

    backend = matplotlib.get_backend()

    FigNums = plt.get_fignums()

    for FigNum in FigNums:
        plt.figure(FigNum)
        mgr = plt.get_current_fig_manager()
        # WX backend
        if 'WX' in backend:
            p = mgr.window.GetPosition()
            s = mgr.window.GetSize()
            CurPos = (p[0], p[1], s[0], s[1])
            with open('CurrentWindowPos%d.pkl'%FigNum, 'w') as f:
                pickle.dump(CurPos, f)
        # QT backend.
        elif 'QT' in backend:
            CurPos = mgr.window.geometry().getRect()
            with open('CurrentWindowPos%d.pkl'%FigNum, 'w') as f:
                pickle.dump(CurPos, f)
        else:
            pass


def AnalyzePhase(AtPct=None, WtPct=None, OxWtPct=None, OByStoich=None):

    #Normalize our AtPct vector.
    AtPct = AtPct/sum(AtPct)*100

    # A dictionary of the AtPct values would be useful so we can look up by element name.
    E = dict(list(zip(pb.ElementalSymbols, AtPct)))


    ### We output an output string which contains Mg, Si and Fe ratioed values.
    OutStr = '--- Simple At% ratios ---\n\n'

    OutStr += "Abundances ratioed to:\n"
    OutStr += "Element to   Mg       Si       Fe\n"
    OutStr += '-'*41 + '\n'
    for Zminus, E in enumerate(AtPct):
        if E != 0:
            EtoMg = E / AtPct[pb.Mg-1]
            EtoSi = E / AtPct[pb.Si-1]
            EtoFe = E / AtPct[pb.Fe-1]
            OutStr += '%-13s%-9.3f%-9.3f%-9.3f\n' % (tuple([pb.ElementalSymbols[Zminus+1]]) + tuple([EtoMg, EtoSi, EtoFe]))



    ### We output an output string which contains ratios to chondritic (protosolar).
    OutStr += '--- Chondritic Analysis ---\n\n'

    # Load the prosolar abundances.  This is recorded from the Lodders ref with logarithmic values.
    ProtosolarAbundancesFileName = 'ProtosolarAbundances.csv'
    if not os._exists(ProtosolarAbundancesFileName):
        ProtosolarAbundancesFileName = os.path.join('ConfigData', ProtosolarAbundancesFileName)
    Protosolar = genfromtxt(ProtosolarAbundancesFileName, delimiter=',', skip_header=1, dtype=None)
    ProtosolarDict = dict(Protosolar)   # This dictionary could be handy...
    Protosolar = array(list(zip(*Protosolar))[1]) # But we really need just a numpy array with the numbers.

    # Convert to vectors which are normalized to Mg, Si, and Fe.
    ProtosolarToMg = power(10, Protosolar)  # Get out of log space into linear space.  Now the numbers relate to AtPct.
    ProtosolarToMg /= ProtosolarToMg[pb.Mg-1]
    ProtosolarToSi = power(10, Protosolar)
    ProtosolarToSi /= ProtosolarToSi[pb.Si-1]
    ProtosolarToFe = power(10, Protosolar)
    ProtosolarToFe /= ProtosolarToFe[pb.Fe-1]
    ProtosolarChondricity = ProtosolarToFe

    GEMSAtPct, GEMSAtPctSD = GEMSPlot(AtPct, ProtosolarToSi)

    #PrintTernary(AtPct, GEMSAtPct, GEMSAtPctSD)

    Chondricity, ElementSigma, GEMSChiSqRed, DOF = GEMSChiPlot(AtPct, Protosolar)

    ShowLastPos(plt)

    # Print out the abundances normalized to protosolar.
    Ratios = list() # Keep track of the ratios, so at the end we can compute standard deviations.
    OutStr += "Abundances ratioed to protosolar and normalized to:\n"
    OutStr += "Element to   Mg       Si       Fe      Chondricity GEMSSigmas\n"
    OutStr += '-'*60 + '\n'
    for Zminus, E in enumerate(AtPct):
        if E != 0:
            EtoMg = E / AtPct[pb.Mg-1] # Norm to Mg
            EtoSi = E / AtPct[pb.Si-1] # Si
            EtoFe = E / AtPct[pb.Fe-1] # Fe
            Ratios.append([EtoMg/ProtosolarToMg[Zminus], # Norm Mg and protosolar
                           EtoSi/ProtosolarToSi[Zminus], # Si and protosolar
                           EtoFe/ProtosolarToFe[Zminus], # Fe and protosolar
                           Chondricity[Zminus],         # Chondritic-like ratio.
                           ElementSigma[Zminus]])          # How many sigmas away from GEMS mean per element.
            OutStr += '%-13s%-9.3f%-9.3f%-9.3f%-11.3f%-9.3f\n' % (tuple([pb.ElementalSymbols[Zminus+1]]) + tuple(Ratios[-1]))
    Ratios = array(Ratios)
    Means = nanmean(Ratios, axis=0)
    Stdevs = nanstd(Ratios, axis=0)
    OutStr += '-'*60 + '\n'
    OutStr += '%-13s%-9.3f%-9.3f%-9.3f%-11.3f%-9.3f\n' % (tuple(['Mean']) + tuple(Means))
    OutStr += '%-13s%-9.3f%-9.3f%-9.3f%-11.3f%-9.3f\n' % (tuple(['Standard dev']) + tuple(Stdevs))
    OutStr += 'GEMS reduced ChiSquared: %g, with DOF: %g\n' % (GEMSChiSqRed, DOF)
    OutStr += '-'*60 + '\n'

    OutStr += '\nRefs:\n    Lodders, K. (2003). Solar System Abundances and Condensation Temperatures of the Elements. The Astrophysical ' \
              'Journal, 591(2), 1220-1247. http://doi.org/10.1086/375492\n' \
              '    Ishii, H. A., et al. (2008). Comparison of Comet 81P/Wild 2 Dust with Interplanetary Dust from Comets. Science, ' \
              '319(5), 447. http://doi.org/10.1126/science.1150683\n' \
              '    Messenger, S., Nakamura-Messenger, K., Keller, L. P., & Clemett, S. J. (2015). ' \
              'Pristine stratospheric collection of interplanetary dust on an oil-free polyurethane foam substrate. Meteoritics and Planetary Science, ' \
              '50(8), 1468-1485. http://doi.org/10.1111/maps.12473\n' \
              '    Keller, L. P., & Messenger, S. (2011). On the origins of GEMS grains. Geochimica Et Cosmochimica Acta, 75(18), 5336-5365. ' \
              'http://doi.org/10.1016/j.gca.2011.06.040'

    return OutStr

def GEMSChiPlot(AtPct, Protosolar):
    AtPct = copy(AtPct[:len(Protosolar)]) # We have to truncate the AtPct vector so it has the same elements as the Protosolar list.
    AtPct[AtPct==0] = nan # We don't want zero abundance elements included in the mean.

    # We also need a trimmed version that will remove elements that are too low Z for comparison with GEMS, or for which we don't have GEMS averages.  Otherwise, it messes up the DOF in the ChiSquared calculation.
    AtPctTrimmed = copy(AtPct[:len(Protosolar)])
    AtPctTrimmed[AtPctTrimmed == 0] = nan # We don't want zero abundance elements included in the mean.
    AtPctTrimmed[:pb.Na-1] = nan # Ignore anything below Na as it is too volatilie for GEMS comparison.

    ProtosolarChondricity = power(10, Protosolar)
    ProtosolarChondricity[isnan(AtPct)] = nan

    GEMSAtPct, GEMSAtPctSD, RefStr = GetGEMSStandardVals(len(AtPctTrimmed))
    GEMSAtPct[GEMSAtPct == 0] = nan # We don't want zero abundance elements included in the mean.
    GEMSAtPctSD /= GEMSAtPct # Make these relative error bars or things get messed up when we renormalize.

    # Sometimes, the user is quanting a spectrum that has extra or missing elements compared to the GEMS average, and the protosolar values always have every element.
    # To compare these, we have to take the intersection elements only, and norm with those.
    GEMSAtPct[isnan(AtPctTrimmed)] = nan # Remove elements that are part of the standard GEMS elements but the user didn't quant.
    AtPctTrimmed[isnan(GEMSAtPct)] = nan # Remove elements that the user did quant but are not in the standard GEMS elements.
    GEMSAtPctSD[isnan(GEMSAtPct)] = nan # And the error bars for the GEMS standards have to be trimmed to.

    # Now we need to renormalize everything so they can be compared.
    Normit = 10
    AtPct /= nansum(AtPct) * Normit
    AtPctTrimmed /= nansum(AtPctTrimmed) * Normit
    GEMSAtPct /= nansum(GEMSAtPct) * Normit
    ProtosolarChondricity /= nansum(ProtosolarChondricity) * Normit

    # Now that things are renormalized, we can turn the GEMS standard deviations back into actual standard deviations instead of relative deviations.
    GEMSAtPctSD *= GEMSAtPct
    # print('GEMSAtPctSD', GEMSAtPctSD)
    # print('GEMSAtPct', GEMSAtPct)

    # Compute the chondricity.
    Chondricity = log10(AtPct/ProtosolarChondricity)

    # Compute how many sigmas away from the mean each element is.
    ElementSigma = (AtPctTrimmed-GEMSAtPct)/GEMSAtPctSD
    # Compute the chi-square values for each element.
    # ElementChiSq = (AtPctTrimmed-GEMSAtPct)**2/GEMSAtPct
    ElementChiSq = (AtPctTrimmed-GEMSAtPct)**2/GEMSAtPctSD**2

    # We assume normal distributions for each element which is wrong -- but this still produced a scalar metric which is better than none.
    # Todo in future work: JointGEMSChi using joint distributions based off GEMS compositions from Keller and Messenger 2011.
    NumElements = nansum(~isnan(GEMSAtPct))
    DOF = NumElements-1 # We have a small number of elements.  Better to use the unbiased estimator.

    # And the reduced chisquared value.
    GEMSChiSqRed = nansum(ElementChiSq)/DOF

    # # Also compute this using scipy stats for kicks.
    # x = AtPctTrimmed
    # xmean = GEMSAtPct
    # x = x[~isnan(x)]
    # xmean = xmean[~isnan(xmean)]
    # ScipyChiSquare = chisquare(x, xmean)
    # print('x: ', x)
    # print('xmean: ', xmean)
    # print('Chi Squared result from scipy:', ScipyChiSquare)


    plt.figure(3)
    plt.clf()
    IncludedZ = where(~isnan(Chondricity))[0]+1
    TickLabels = [El for Z, El in enumerate(pb.ElementalSymbols) if Z in IncludedZ]
    TickInds = list(range(len(TickLabels)))
    plt.scatter(TickInds, Chondricity[IncludedZ-1], marker='o', color='red', s=150, alpha=0.5, label='Chondricity')
    plt.scatter(TickInds, ElementSigma[IncludedZ-1], marker='o', color='blue', s=150, alpha=0.5, label='Elemental sigmas from mean')
    plt.xticks(TickInds, TickLabels, rotation='vertical')
    plt.axhline(0, 0, 92, color='green', linewidth=3, label='Chondritic/GEMSitic')
    plt.legend()
    plt.ylabel('Chondricity:\nlog$_{10}$(At%/Chondritic)\nVariation from GEMS ($\sigma$)', fontsize=FontSizeBasis)
    plt.tight_layout()
    # print(plt.get_backend())

    # print('Chondricity values: ', Chondricity[IncludedZ-1])
    # print('Chondricity mean: %g, Chondricity std: %g' % (nanmean(Chondricity), nanstd(Chondricity)))
    # print('ElementSigma values: ', ElementSigma[IncludedZ-1])
    # print('GEMSChiSqRed: %g' % GEMSChiSqRed)

    return Chondricity, ElementSigma, GEMSChiSqRed, DOF


def GetGEMSStandardVals(AtPctVectorLen, WhichRefs='KMMK'):
    if WhichRefs == 'Ishii':
        # GEMS average values and standard deviations from Ishii 2008 Science paper.
        GEMSAtPct = zeros(AtPctVectorLen);
        GEMSAtPctSD = zeros(AtPctVectorLen)
        GEMSAtPct[pb.O - 1] = 66.71; GEMSAtPctSD[pb.O - 1] = 4.43
        GEMSAtPct[pb.Mg - 1] = 9.37; GEMSAtPctSD[pb.Mg - 1] = 4.42
        GEMSAtPct[pb.Al - 1] = 1.62; GEMSAtPctSD[pb.Al - 1] = 1.09
        GEMSAtPct[pb.Si - 1] = 14.40; GEMSAtPctSD[pb.Si - 1] = 2.36
        GEMSAtPct[pb.S - 1] = 3.69; GEMSAtPctSD[pb.S - 1] = 2.73
        GEMSAtPct[pb.Ca - 1] = 0.82; GEMSAtPctSD[pb.Ca - 1] = 0.70
        GEMSAtPct[pb.Cr - 1] = 0.12; GEMSAtPctSD[pb.Cr - 1] = 0.10
        GEMSAtPct[pb.Mn - 1] = 0.02; GEMSAtPctSD[pb.Mn - 1] = 0.06
        GEMSAtPct[pb.Fe - 1] = 6.39; GEMSAtPctSD[pb.Fe - 1] = 2.39
        GEMSAtPct[pb.Ni - 1] = 0.40; GEMSAtPctSD[pb.Ni - 1] = 0.23
        RefStr = 'Ishii et al., 2008'
    if WhichRefs == 'KMMK':
        # This is using Keller and Messenger 2011 and Messenger and Keller 2015.  Total of 287 GEMS measurements.
        GEMSAtPct = zeros(AtPctVectorLen);
        GEMSAtPctSD = zeros(AtPctVectorLen)
        GEMSAtPct[pb.O - 1] =  57.698014; GEMSAtPctSD[pb.O - 1] =  6.563890
        GEMSAtPct[pb.Mg - 1] = 10.684983; GEMSAtPctSD[pb.Mg - 1] = 4.546400
        GEMSAtPct[pb.Al - 1] = 1.149652; GEMSAtPctSD[pb.Al - 1] =  0.474962
        GEMSAtPct[pb.Si - 1] = 16.173415; GEMSAtPctSD[pb.Si - 1] = 3.500900
        GEMSAtPct[pb.S - 1] =  4.492578; GEMSAtPctSD[pb.S - 1] =   2.886237
        GEMSAtPct[pb.Ca - 1] = 0.598641; GEMSAtPctSD[pb.Ca - 1] =  0.454145
        GEMSAtPct[pb.Cr - 1] = 0.048711; GEMSAtPctSD[pb.Cr - 1] =  0.108731
        GEMSAtPct[pb.Fe - 1] = 8.670697; GEMSAtPctSD[pb.Fe - 1] =  3.147095
        GEMSAtPct[pb.Ni - 1] = 0.512613; GEMSAtPctSD[pb.Ni - 1] =  0.284516
        RefStr = 'K&M 2011 and M&K 2015'
    else:
        print('Unknown reference(s) for GEMS standard vals.')
        GEMSAtPct = None
        GEMSAtPctSD = None
        RefStr = None

    return GEMSAtPct, GEMSAtPctSD, RefStr

def GEMSPlot(AtPct, ProtosolarToSi):
    ### Draw a plot comparing this spectrum normalized to CI and plotted against GEMS compositions.
    # First we have mean and standard deviation values for GEMS compositions.
    GEMSAtPct, GEMSAtPctSD, RefStr = GetGEMSStandardVals(pb.U-1)
    # Make these Si normalized.
    SiTemp = GEMSAtPct[pb.Si - 1]
    # GEMSRel is derived from GEMSAtPct, but is normalized against Si and normalized against chondritic.
    GEMSRel = copy(GEMSAtPct) / SiTemp
    GEMSRelSD = copy(GEMSAtPctSD) / SiTemp
    # And normalize to chondritic
    GEMSRel /= ProtosolarToSi[0:pb.U - 1]
    GEMSRelSD /= ProtosolarToSi[0:pb.U - 1]
    # Make a version of the sample quant which is ratioed to si
    AtPctToSi = AtPct / AtPct[pb.Si - 1]
    # And chondritic
    AtPctToSi[:len(ProtosolarToSi)] /= ProtosolarToSi
    # Get the union of elements which are in our spectrum and in the GEMS mean values.
    # All indices for elements which have non zero values from either array.
    IncludedZ = hstack((nonzero(AtPct)[0], nonzero(GEMSRel)[0]))
    # Eliminate duplicates and make sure in ascending order.
    IncludedZ = sort(unique(IncludedZ))
    # Indices are 0 based, Z is 1 based.
    IncludedZ += 1
    # Get the list of element names for those elements.
    TickLabels = [El for Z, El in enumerate(pb.ElementalSymbols) if Z in IncludedZ]
    TickInds = list(range(len(TickLabels)))
    GEMSInds = []
    GEMSVals = []
    GEMSErrs = []
    SpectrumInds = []
    SpectrumVals = []
    ChondriticInds = []
    ChondriticVals = []
    for Zminus1, Val in enumerate(AtPctToSi[:pb.U - 1]):
        if GEMSRel[Zminus1] > 0:
            GEMSInds.append(TickLabels.index(pb.ElementalSymbols[Zminus1 + 1]))
            GEMSVals.append(GEMSRel[Zminus1])
            GEMSErrs.append(GEMSRelSD[Zminus1])
        if AtPct[Zminus1] > 0:
            SpectrumInds.append(TickLabels.index(pb.ElementalSymbols[Zminus1 + 1]))
            SpectrumVals.append(AtPctToSi[Zminus1])
        # This part only applies if not normalizing to chondritic.
        # if pb.ElementalSymbols[Zminus1+1] in TickLabels:
        #     ChondriticInds.append(TickLabels.index(pb.ElementalSymbols[Zminus1+1]))
        #     ChondriticVals.append(ProtosolarToSi[Zminus1])
    # We will be plotting so clear the plot that may already be plotted.
    plt.figure(1)
    plt.clf()
    # GEMS plot
    plt.scatter(GEMSInds, GEMSVals, marker='o', color='red', s=150, alpha=0.5, label=RefStr)
    # plt.errorbar(GEMSInds, GEMSVals, yerr=GEMSErrs, fmt='none', elinewidth=3, capsize=7, capthick=3, ecolor='red')
    plt.errorbar(GEMSInds, GEMSVals, yerr=GEMSErrs, fmt='none', alpha=0.5, elinewidth=5, capsize=0, capthick=3, ecolor='red')
    # This spectrum.
    plt.scatter(SpectrumInds, SpectrumVals, marker='v', color='blue', s=150, alpha=0.5, label='This Spectrum')
    # Chondritic
    # plt.scatter(ChondriticInds, ChondriticVals, marker='s', color='green', s=200,alpha=0.5)
    plt.axhline(1, 0, 92, color='green', linewidth=3, label='Chondritic')
    plt.xticks(TickInds, TickLabels, rotation='vertical')
    plt.gca().set_yscale('log')
    plt.legend()
    # plt.legend(['Ishii et al., 2008', 'This Spectrum', 'Chondritic'])
    plt.ylabel('Element/Si/chondritic, At%', fontsize=FontSizeBasis)
    plt.gca().set_ylim([3e-2, 30])
    plt.tight_layout()
    return GEMSAtPct, GEMSAtPctSD


def PrintTernary(AtPct, GEMSAtPct, GEMSAtPctSD):

    if ternary == None:
        print("For ternary plot please pip install python-ternary")
        return

    ### Now print a ternary plot
    if plt.fignum_exists(2):
        plt.figure(2)
        plt.close()
    fig, tax = ternary.figure(scale=100)
    tax.boundary(linewidth=4)
    tax.gridlines(color='black', multiple=10)
    tax.left_axis_label("Fe-S", fontsize=FontSizeBasis)
    tax.bottom_axis_label("Si", fontsize=FontSizeBasis)
    tax.right_axis_label("Mg", fontsize=FontSizeBasis)
    # Remove default matplotlib ticks.
    tax.ticks(axis='lbr', linewidth=1, multiple=10)
    tax.clear_matplotlib_ticks()

    # Compute and plot this point on the ternary for this composition
    FeminusS = AtPct[pb.Fe - 1] - AtPct[pb.S - 1]
    ThisPoint = array([FeminusS, AtPct[pb.Si - 1], AtPct[pb.Mg - 1]]).astype('float')
    ThisPoint = ThisPoint / sum(ThisPoint) * 100
    ThisPoint = vstack((ThisPoint, ThisPoint))  # Seems to be a bug -- you need a minimum of two points...
    tax.scatter(ThisPoint, marker='.', s=300, alpha=0.5, color='blue', label="This Spectrum")

    # Compute and plot the point for the average of GEMS.
    FeminusS = GEMSAtPct[pb.Fe - 1] - GEMSAtPct[pb.S - 1]
    GEMSPoint = array([FeminusS, GEMSAtPct[pb.Si - 1], GEMSAtPct[pb.Mg - 1]]).astype('float')
    GEMSPoint = GEMSPoint / sum(GEMSPoint) * 100
    GEMSPoint = vstack((GEMSPoint, GEMSPoint))  # Seems to be a bug -- you need a minimum of two points...
    tax.scatter(GEMSPoint, marker='.', s=300, alpha=0.5, color='red', label="Ishii et al., 2008")

    tax.legend()

    plt.title('At %')

def SaveResults(FileRoot):
    plt.figure(1)
    plt.savefig(FileRoot + '_GEMSplot.png')
    plt.figure(3)
    plt.savefig(FileRoot + '_Chondricity_GEMSChi.png')


if __name__ == '__main__':

    import imp
    pb = imp.load_source('PhysicsBasics', 'PhysicsBasics.py')

    # AtPct = zeros(pb.MAXELEMENT)
    # AtPct[pb.O-1] = 61.9
    # AtPct[pb.Mg-1] = 2.9
    # AtPct[pb.Al-1] = 0.8
    # AtPct[pb.Si-1] = 16.9
    # AtPct[pb.S-1] = 6.1
    # AtPct[pb.Cr-1] = 0.3
    # AtPct[pb.Fe-1] = 11.1
    # print 'Planetary Materials Page 2-54 (Rietmeijer: Interplanetary Dust Particles): Table 23, Line 1\n'
    # print AnalyzePhase(AtPct)
    #
    # # Bradley, J. P. (2007). 1.26 - Interplanetary Dust Particles. In A. M. Davis (Ed.), Treatise on Geochemistry, Vol. 1, Meteorites, Comets, and Planets (pp. 689-711). Oxford: Pergamon. http://doi.org/10.1016/B0-08-043751-6/01152-X
    # AtPct = zeros(pb.MAXELEMENT)
    # AtPct[pb.C-1] = 1.75
    # AtPct[pb.O-1] = 4.173
    # AtPct[pb.Na-1] = 0.052
    # AtPct[pb.Mg-1] = 0.980
    # AtPct[pb.Al-1] = 0.075
    # AtPct[pb.Si-1] = 1
    # AtPct[pb.S-1] = 0.356
    # AtPct[pb.Ca-1] = 0.052
    # AtPct[pb.Cr-1] = 0.015
    # AtPct[pb.Fe-1] = 0.697
    # AtPct[pb.Ni-1] = 0.027
    # print 'Chondritic IDPs bulk\n'
    # print AnalyzePhase(AtPct)
    #
    # # Protosolar abundances: Planetary Scientists Handbook, Chapter 2.1, Table 2.1, column 1.
    # AtPct = zeros(pb.MAXELEMENT)
    # AtPct[pb.C-1] = 1*10**(8.55)
    # AtPct[pb.O-1] = 1*10**(8.87)
    # AtPct[pb.Na-1] = 1*10**(6.31)
    # AtPct[pb.Mg-1] = 1*10**(7.56)
    # AtPct[pb.Al-1] = 1*10**(6.48)
    # AtPct[pb.Si-1] = 1*10**(7.55)
    # AtPct[pb.S-1] = 1*10**(7.20)
    # AtPct[pb.Ca-1] = 1*10**(6.36)
    # AtPct[pb.Cr-1] = 1*10**(5.68)
    # AtPct[pb.Fe-1] = 1*10**(7.50)
    # AtPct[pb.Ni-1] = 1*10**(6.25)
    # print 'Protosolar values\n'
    # print AnalyzePhase(AtPct)

    # # GEMS mean from Ishii's science paper in 2008.
    # AtPct = zeros(pb.MAXELEMENT)
    # AtPct[pb.O - 1] = 66.71;
    # AtPct[pb.Mg - 1] = 9.37;
    # AtPct[pb.Al - 1] = 1.62;
    # AtPct[pb.Si - 1] = 14.40;
    # AtPct[pb.S - 1] = 3.69;
    # AtPct[pb.Ca - 1] = 0.82;
    # AtPct[pb.Cr - 1] = 0.12;
    # AtPct[pb.Mn - 1] = 0.02;
    # AtPct[pb.Fe - 1] = 6.39;
    # AtPct[pb.Ni - 1] = 0.40;
    # print 'Ishii GEMS mean values\n'
    # print AnalyzePhase(AtPct)

    # # Protosolar abundances: Planetary Scientists Handbook, Chapter 2.1, Table 2.1, column 1.
    # # With wild K.
    # AtPct = zeros(pb.MAXELEMENT)
    # AtPct[pb.C-1] = 1*10**(8.55)
    # AtPct[pb.O-1] = 1*10**(8.87)
    # AtPct[pb.Na-1] = 1*10**(6.31)
    # AtPct[pb.Mg-1] = 1*10**(7.56)
    # AtPct[pb.Al-1] = 1*10**(6.48)
    # AtPct[pb.Si-1] = 1*10**(7.55)
    # AtPct[pb.S-1] = 1*10**(7.20)
    # AtPct[pb.K-1] = 10*10**(5.12)
    # AtPct[pb.Ca-1] = 1*10**(6.36)
    # AtPct[pb.Cr-1] = 1*10**(5.68)
    # AtPct[pb.Fe-1] = 1*10**(7.50)
    # AtPct[pb.Ni-1] = 1*10**(6.25)
    # print 'Protosolar values\n'
    # print AnalyzePhase(AtPct)

    # Protosolar abundances from Lodders
    # With wild K.
    AtPct = zeros(pb.MAXELEMENT)
    AtPct[pb.C-1] = 288.40315031266118
    AtPct[pb.O-1] = 575.43993733715661
    AtPct[pb.Na-1] = 2.3442288153199229
    AtPct[pb.Mg-1] = 41.686938347033553
    AtPct[pb.Al-1] = 3.4673685045253171
    AtPct[pb.Si-1] = 40.738027780411301
    AtPct[pb.P-1] = 0.34673685045253166
    AtPct[pb.S-1] = 18.197008586099827
    AtPct[pb.Cl-1] = 0.21379620895022325
    AtPct[pb.K-1] = 0.15135612484362074
    AtPct[pb.Ca-1] = 2.5703957827688648
    AtPct[pb.Cr-1] = 0.52480746024977232
    AtPct[pb.Mn-1] = 0.38018939632056126
    AtPct[pb.Fe-1] = 34.673685045253166
    AtPct[pb.Ni-1] = 1.9498445997580456
    print('Protosolar values\n')
    print(AnalyzePhase(AtPct))

