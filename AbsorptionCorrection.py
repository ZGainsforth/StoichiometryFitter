import matplotlib
matplotlib.use('Qt4Agg')
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
    mu = zeros((pb.MAXELEMENT, len(E)))

    # Get mu for each element.
    for ElementIndex in arange(0, pb.MAXELEMENT, 1):
    
        # We only add a MAC term for those elements that have a non-zero abundance.
        if WtPct[ElementIndex] == 0:
            continue

        # Load the scattering data for this element
        try:
            ScatteringData = loadtxtcaching('CXRO Scattering Files/' + pb.ElementalSymbols[ElementIndex+1].lower() + '.nff', skiprows=1)
        except:
            # In case this an element for which we dont have attenuation data then the attenuation function "no
            # attenuation".
            # Use Si as the template for this, and set f2 to 0 (which leads to a practically infinite attenuation
            # length.)
            ScatteringData = loadtxtcaching('CXRO Scattering Files/si.nff', skiprows=1)
            ScatteringData[:,2] = sys.float_info.min # The TINIEST cross-section we can keep (without div/0)

        f2 = interp(E, ScatteringData[:,0], ScatteringData[:, 2])

        # mua, (f2 is implicitly measured in grams, so I have to unfold that...)
        mua = 2 * pb.r0 * pb.h*pb.c/E * f2/pb.ElementalWeights[ElementIndex+1]
    
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

def DoAbsorption(E, Iin, WtPct, rho, AbsorptionLength, Takeoff=90):
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
    murho = 1/AbsorptionCurve

    # Takeoff coefficient
    TakeoffCoeff = sin(Takeoff*pi/180)

    # Beer's law.
#    I = nan_to_num(Iin*exp(-1.*AbsorptionLength/AbsorptionCurve))
#    I = nan_to_num(Iin*exp(-1.*AbsorptionLength*TakeoffCoeff/AbsorptionCurve))
#    TakeoffCoeff = 1/sin(Takeoff*pi/180); I = nan_to_num(Iin*(1-exp(-AbsorptionLength*TakeoffCoeff/AbsorptionCurve))/(TakeoffCoeff/AbsorptionCurve))
    if AbsorptionLength >= 0:
        # If AbsorptionLength is positive, then it means we start with I0 and compute I after being absorbed by AbsorptionLength.
        I = nan_to_num(Iin*TakeoffCoeff/(murho*AbsorptionLength)*(1-exp(-murho*AbsorptionLength/TakeoffCoeff)))
    else:
        # If negative, it means we have I and want to figure out what I0 was before being absorbed.
        # Notice we minus AbsorptionLength since it was input as a negative value, but beers law want's positive values.
        I = nan_to_num((Iin*murho*(-AbsorptionLength)/TakeoffCoeff)/(1-exp(murho*AbsorptionLength/TakeoffCoeff)))

    """ These come from solving the integral:
    I = I0 * int(exp(-murho*t/sin(Takeoff)), dt for t=0 to AbsorptionLength)
    """

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

if __name__ == '__main__':
    ### DEBUG! ###
    Ev = arange(500,7000,10)
    Iv = ones(shape(Ev))
    WtPct = zeros(pb.MAXELEMENT)
    WtPct[pb.O-1]=37.158
    WtPct[pb.Mg-1]=14.112
    WtPct[pb.Fe-1]=32.424
    WtPct[pb.Si-1]=16.307
    AbsorptionCurve = GetAbsorptionCurve(Ev, WtPct, 1)
    TakeoffCoeff = sin(0.1*pi/180)
    AbsorptionCurve90 = AbsorptionCurve * sin(90*pi/180)
    AbsorptionCurve30 = AbsorptionCurve * sin(30*pi/180)
    AbsorptionCurve05 = AbsorptionCurve * sin(0.1*pi/180)
    Iv = nan_to_num(Iv*exp(-1/(AbsorptionCurve*TakeoffCoeff))*(AbsorptionCurve*TakeoffCoeff))
    loglog(Ev,AbsorptionCurve90, Ev,AbsorptionCurve30, Ev,AbsorptionCurve05, Ev, Iv)
    legend(['90$^{\circ}$', '30$^{\circ}$', '0.1$^{\circ}$', '$I_v$'], loc='best')
    show()
    #DoAbsorption(E, Iin, WtPct, rho, AbsorptionLength, Takeoff=90)
