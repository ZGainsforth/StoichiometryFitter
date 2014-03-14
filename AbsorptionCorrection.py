from matplotlib.pyplot import *
from numpy import *
import PhysicsBasics as pb

def GetAbsorptionCurve(E, WtPct, rho):
    """GetAbsorptionCurve(E, WtPct, rho): Given a material composition and density, and an energy axis,
    GetAbsorptionCurve produces a curve where the abcissa is the absorption length in microns, and the ordinate is
    the energy.

    :param E: numpy vector in eV
    :param WtPct: One based vector of all elements and their weight percents in the sample that is absorbing.
    :param rho: Density of the material.
    :return: A vector of the same length as E but with units microns.
    """

    # mu is the cross-section.  We don't know it yet, so we start out with a matrix.  One row for each element,
    # and thus one measurement of mu for each.  We'll sum them later because they add linearly.
    mu = zeros((pb.MAXELEMENT, len(E)));

    # Get mu for each element.
    for ElementIndex in arange(1, pb.MAXELEMENT, 1):
    
        # We only add a MAC term for those elements that have a non-zero abundance.
        if WtPct[ElementIndex] == 0:
            continue

        # Load the scattering data for this element
        try:
            ScatteringData = loadtxtcaching('CXRO Scattering Files/' + pb.ElementalSymbols[ElementIndex].lower() + '.nff', skiprows=1)
        except:
            # In case this an element for which we dont have attenuation data then the attenuation function "no
            # attenuation".
            # Use Si as the template for this, and set f2 to 0 (which leads to a practically infinite attenuation
            # length.)
            ScatteringData = loadtxtcaching('CXRO Scattering Files/si.nff', skiprows=1)
            ScatteringData[:,2] = sys.float_info.min # The TINIEST cross-section we can keep (without div/0)

        f2 = interp(E, ScatteringData[:,0], ScatteringData[:, 2])

        # mua, (f2 is implicitly measured in grams, so I have to unfold that...)
        mua = 2 * pb.r0 * pb.h*pb.c/E * f2/pb.ElementalWeights[ElementIndex]
    
        # Density in atoms/m3 
        n = 1000*pb.NAvogadro*(WtPct[ElementIndex]/100)

        # And this gives mu for this element.
        mu[ElementIndex, :] = n*mua
    
    # Absorption length.  A = 1/e intensity.
    A = 1./(sum(mu, 0)*rho)*1e3
    return A

#    loglog(E, A)
#    show()
#    xlabel('Energy in eV');
#    ylabel('Absorption length in microns 1/(mu x rho)')
#    title(['Absorption curve, rho = ' num2str(rho) ' '])
#    axis([30, E(length(E)), min(A), max(A)*2]);

def DoAbsorption(E, Iin, WtPct, rho, AbsorptionLength):
    # Get the vector describing the attenuation length as a function of energy.
    """DoAbsorption(E0, E, Iin, WtPct, rho, AbsorptionLength):

    :param E: (E, Iin) are an (abscissa,ordinate) pair.  E in eV.
    :param Iin: I is in counts or intensity.
    :param WtPct: One based vector of length pb.MAXELEMENT with the wt % of each element in the absorber.
    :param rho: Density in g/cm3 of the absorber
    :param AbsorptionLength: Distance travelled through the absorber (in SEM corrections, this is not always the
    thickness of the sample...)
    :return: I after absorbing Iin.
    """

    AbsorptionCurve = GetAbsorptionCurve(E, WtPct, rho)

    # Beer's law.
    I = Iin*exp(-1.*AbsorptionLength/AbsorptionCurve)

    # Return the modified intensity after absorption.
    return I
    
def CorrectDetectorProperties(E0, E, Iin, DetectorC, DetectorO, DetectorWindowAbsorptionLength, DetectorSiAbsorptionLength, DetectorThickness, GoldThickness):
    
    # First the thin film window.
    WtPct = zeros(101);
    WtPct[pb.C] = DetectorC #75;
    WtPct[pb.O] = DetectorO #25;
    rho = 1;
    #AbsorptionLength = 0.05;
    I = DoAbsorption(E0, E, Iin, WtPct, rho, DetectorWindowAbsorptionLength);

#    # First the thin film window.
#    WtPct = zeros(101);
#    WtPct[pb.Al] = DetectorC #75;
#    WtPct[pb.N] = DetectorO #25;
#    rho = 4;
#    #AbsorptionLength = 0.05;
#    I = DoAbsorption(E0, E, Iin, WtPct, rho, DetectorWindowAbsorptionLength);

    # Now the Au coating.
    WtPct = zeros(101);
    WtPct[pb.Pt] = 100;
    WtPct[pb.Pd] = 100;
    rho = 19.3;
    #AbsorptionLength = 0.06;
    I = DoAbsorption(E0, E, I, WtPct, rho, GoldThickness);
    
    # Now the Si Detector.
    WtPct = zeros(101);
    WtPct[pb.Si] = 100;
    rho = 2.65;
    #AbsorptionLength = 0.06;
    I = DoAbsorption(E0, E, I, WtPct, rho, DetectorSiAbsorptionLength);

    # And account for the fact that the detector is not infinitely thick.
    Itrans = DoAbsorption(E0, E, I, WtPct, rho, DetectorThickness)
    I -= Itrans;
    
    return I

ListOfLoadedFiles = {'nofile':1}
def loadtxtcaching(FileName, skiprows=1):
    """loadtxtcaching(FileName, skiprows=1): Allows us to load the x-ray data for each element just once.  If its
    been used before, since the program loaded, then it is held in the variable ListOfLoadedFiles.  This is used for
    two column files.

    :param FileName: File name which is cached.  Don't use too much memory!
    :param skiprows: This is for loadtxt which may have a header.
    :return: The file.
    """
    global ListOfLoadedFiles

    # Already loaded this file?
    if FileName not in ListOfLoadedFiles:
        # Nope, so read it in.
        print 'Loading %s' % FileName
        ListOfLoadedFiles[FileName] = loadtxt(FileName, skiprows=skiprows)

    # Return the (previously or newly) cached file.
    return ListOfLoadedFiles[FileName]
    

