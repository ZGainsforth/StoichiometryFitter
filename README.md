#StoichiometryFitter
====================

Read the [paper](https://github.com/ZGainsforth/StoichiometryFitter/blob/master/2016%20-%20M%26M%20-%20Stoichiometry%20Fitter.pdf) describing the software.


1) Interconvert X-ray counts into elemental abundances.

2) Use elemental abundances to determine mineral compositions and solid solutions.

3) Do application specific processing for phases such as computing site occupancies from stoichiometry, or determining Fo#.

For a quick overview of what the program does, download [the video](https://www.youtube.com/watch?v=OrgHYjvGTHI) to your machine and view it.

Is there a feature that would be very useful to you?  Contact me at xraysoftware@ssl.berkeley.edu.

## K-Factor Data

The K-factors in `ConfigData/kfacs Titan 80 keV.csv` are **dimensionless** relative sensitivity factors calibrated against Silicon (Si K = 1.0). Values represent the ratio of counts expected per unit weight percent for each element, relative to Silicon.

- **K, L, M** columns correspond to K-shell, L-shell, and M-shell fluorescence lines.
- Elements with **K = 0.0** have K-shell excitation cross-sections near zero at 80 keV.
- The CSV is ordered by atomic number (H = 1 through Uuo = 118).

## Elemental Weights

`PhysicsBasics.py` `ElementalWeights` uses natural abundance atomic weights (IUPAC standard, dimensionless).
Source: https://physics.nist.gov/cgi-bin/Compositions/standard_asp.cgi

##Todo:
====================

1) Add command line functionality to open an input file, set the processing steps and go.

2) If the counts are saved for an input file, then autosave the output file.

3) Pass output file root to phase analyzer so it can autosave auxiliary files.


