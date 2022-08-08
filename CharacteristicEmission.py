__author__ = 'Zack Gainsforth'
__copyright__ = 'Copyright 2016, Zack Gainsforth'
__email__ = 'zsg@gainsforth.com'

import io
import numpy as np
import pickle
import itertools
#import PeakTypes
#from DetectorPhysics import *

ElamLoaded = False # We only want to load the Elam database once.  Keep track of if that has been done.  False = not yet loaded.
ElamData = []

# For debugging we sometimes want Elam to print out the lines it loaded.
ElamPrint = lambda s: None #print(s)

# Reading the Elam database is time consuming.  This caches the fluorescence data so it is only read once per program
#  load.
ElamFluorescenceLines = {'nodata':1}

def GetElamFluorescenceLines(ElementName, E=None, I=None):
    global ElamLoaded, ElamData, ElamFluorescenceLines

    # Already loaded fluorescence data for this element?
    if ElementName in ElamFluorescenceLines:
        # Return the (previously or newly) cached element info.
        return ElamFluorescenceLines[ElementName]

    # This is really time consuming, so we also cache it as a pickle file.
    try:
        ElementXRayLines = pickle.load(open('Elam/'+ ElementName.lower() +'.pickle', 'rb'))
        # It was pickled!  So cache it in memory and return it.
        ElamFluorescenceLines[ElementName] = ElementXRayLines
        return ElementXRayLines
    except:
        # It wasn't pickled, no matter.  We'll make it now and pickle it at the end of the function.
        pass

    # It's not already loaded, so continue with loading it.

    # Read the entire Elam database into memory.
    if ElamLoaded == False:
        fo = open('Elam/ElamDB12.txt', "r+")
        str = fo.read();
        fo.close()
        ElamData = io.StringIO(str)
        ElamLoaded = True

    # Initialize the lists that will contain the line information.
    LineNamesIUPAC = []
    LineNamesSiegbahn = []
    Geoms = []

    # Make sure we're at the start of the file
    ElamData.seek(0)

    # Zoom forward to the element we are looking for.
    for line in ElamData:
        if ('Element '+ElementName+' ') in line:
            break

    # Pull out the section with the fluorescence lines, which is first.
    for line in ElamData:
        # Ignore the lines that aren't the fluorescence info
        if ('Edge' in line) or ('Lines' in line) or ('CK' in line):
            continue
        # When we get to the Photoionization section we are done.
        if 'Photo' in line:
            break;
        # Otherwise, this is a fluorescence line.  Add it to our output if it is intense enough to improve the fit
        q = line.split()
        if (float(q[3]) > 0.01):
            LineNamesIUPAC.append(q[0])
            LineNamesSiegbahn.append(q[1])
            Geoms.append([float(q[2]), float(q[3])])
            ElamPrint('Added: ' + line)
        else:
            ElamPrint('Ignored (intensity < 1%): ' + line)

    Geoms = np.array(Geoms)

    # We are going to use the Siegbahn names, not IUPAC.
    # Make a dictionary where the key is the line name and the value is an (energy, intensity) tuple.
    Lines = dict(list(zip(LineNamesSiegbahn, Geoms)))

    ElementXRayLines = {}

    for Series in ['K', 'L', 'M', 'N', 'O']:

        #Obtain the name strings for only the lines that have names that start with K (or L, or M, whatever Series we are on).
        ThisSeries = dict([(k, v) for k, v in list(Lines.items()) if k.startswith(Series)])

        # If these series is not present, then don't keep it.
        if len(ThisSeries) == 0:
            continue

        # Make this edge in ElementXRayLines
        ElementXRayLines[Series] = ThisSeries

    # We've built the fluorescence data for this element.  Cache it and pickle it for next time.
    ElamFluorescenceLines[ElementName] = ElementXRayLines
    pickle.dump(ElementXRayLines, open('Elam/' + ElementName.lower() + '.pickle', 'wb'))

    # And return what we've got.
    return ElementXRayLines

def GetFluorescenceLineEnergy(ElementName, Series='K', Line=None):
    LineData = GetElamFluorescenceLines(ElementName)

    # If the user specifies a specific line, then we will return its energy.
    try:
        if Line is not None:
            return LineData[Series][Line][0]
        else:
            # The user doesn't specify a line which means he wants to know the energy of the main lines of the series.
            # Usually for absorption correction estimation.  We'll make a weighted energy which considers all the lines.
            ser = LineData[Series]
            # For each line, multiply the energy times the intensity, and then we average these to get the weighted energy.
            # Note this works since the intensities sum to 1.
            WeightedEnergy = sum([(line[0]*line[1]) for line in list(ser.values())])
            return WeightedEnergy
    except:
        # If the user asked for a series or line that's not in the database, then we return none.
        return None

# def MakeBasisSpectra(Config):
#
#     # Loop through all the elements
#     for Elname, ElLines in Config['XRayLines'].iteritems():
#
#         # Loop through each series in the elements
#         for SeriesName, Series in ElLines.iteritems():
#
#             # Remove variables pertaining to the whole series.  Everything except the line names is prefixed with Series
#             Series = dict([(k,v) for k,v in Series.iteritems() if not k.startswith('Series')])
#
#             # Make a Geoms for this series with a gaussian for every peak.
#             Geoms = np.reshape(np.concatenate(Series.values()), (-1,2))
#
#             # And make the basis spectrum
#             BasisSpectrum = MakeGaussianSpectrum(Config['E'], Geoms, Config['EnergyResolutionDetector'], Config['DeadTimeDecay'])
#
#             # Normalize the basis spectrum to the highest intensity is 1.  This way we can easily scale it to match the experimental spectrum.
#             BasisSpectrum /= max(BasisSpectrum)
#             Config['XRayLines'][Elname][SeriesName]['SeriesBasisSpectrum'] = BasisSpectrum
#
#             # Now we need to guess an amplitude.  For starters, just make the max in the basis match the height of that
#             # same energy in the experimental spectrum.
#             IMaxIndex = np.argmax(BasisSpectrum)
#             Amplitude = Config['I'][IMaxIndex]
#             Config['XRayLines'][Elname][SeriesName]['SeriesAmplitude'] = Amplitude
#
#     return True

if __name__ == '__main__':
    print(('Fe-K: %s' % GetFluorescenceLineEnergy('Fe')))
    print(('Al-K: %s' % GetFluorescenceLineEnergy('Al')))
    print(('Mg-K: %s' % GetFluorescenceLineEnergy('Mg')))
    print(('Fe-Q: %s' % GetFluorescenceLineEnergy('Fe', Series='Q')))
    print(('Fe-Ka2: %f' % GetFluorescenceLineEnergy('Fe', Series='K', Line='Ka2')))
    print(('Fe-Ka1: %f' % GetFluorescenceLineEnergy('Fe', Series='K', Line='Ka1')))
