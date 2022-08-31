---
title: 'Stoichiometry Fitter, a GUI for quantifying TEM/EDS and XRF results and analyzing mineral phases'
tags:
  - Python
  - geology
  - EDS
  - WDS
  - SEM
  - EPMA
  - TEM
authors:
  - name: Zack Gainsforth
    orcid: 0000-0001-8180-3507
    affiliation: "1" # (Multiple affiliations must be quoted)
    corresponding: true # (This is how to denote the corresponding author)
  - name: Michael Ofengenden
    affiliation: 1
  - name: Zhenbang  Yu 
    affiliation: 1
affiliations:
 - name: Space Sciences Laboratory, University of California at Berkeley, Berkeley, CA, 94720 USA
   index: 1
date: 30 August 2022
bibliography: paper.bib

# Summary

We have developed a software tool for analysis of materials characterized by techniques such as X-ray fluorescence (XRF) in a synchrotron and energy dispersive spectroscopy (EDS) in a transmission electron microscope (TEM). 
Quantifications from various techniques can be input as atomic %, elemental weight %, oxide weight % (with cation oxidation states) or as raw counts in the case of TEM or XRF measurements. 
In the latter cases it is possible to apply a set of k-factors, a thickness correction and a detector correction. 
The thickness correction is based on scattering factors from the Center for X-ray Optics (CXRO) [1,2] and is found to be surprisingly accurate. 
On a troilite FIB section which was FIBed to 500 nm thickness, the optimal thickness correction resulting in perfect stoichiometry between Fe and S was 508 nm. 
Generally, CXRO tabulated absorption values are accurate better than 10%. 
The detector correction includes the Si dead layer, conductor coating, thin window, and finally accounts for incomplete absorption of photons at higher energies that pass through the detector entirely.

Regardless of how the elemental quantification is entered, it is then possible to fit the quantification as a linear combination of phases. A simple example would be to fit a pyroxene composition against a linear combination of enstatite, ferrosilite, and wollastonite. Another example would be to improve the iron quantification in an olivine containing nanophase troilite. One could fit forsterite- fayalite-FeS and obtain an improved Fo#. It is possible to fit any phases you wish, including phases defined by the user, e.g. “chondritic solids” which has a solar abundance of every element except oxygen which is computed by stoichiometry.
However, it is important to fit fewer phases than there are elements, and avoid fitting phases with overlapping elements. For example, a spectrum containing Mg, Ca, Fe, Si and O cannot be fit against a series: forsterite, fayalite, monticellite, enstatite and ferrosilite. Such a fit would always produce “perfect” results but would produce Mg#s which were not reliable.
For more sophisticated analyses, python scripts (named phase analyses) can be run on the quantification to extract information specific to an analytic workflow. These can be very simple — as few as four lines of code — or they can be very complex. For example, iron sulfides have a number of superlattices which are a function of the cation/S ratio. An analysis script named “sulfide” calculates the cation/S ratio and then suggests the superlattice structure along with the reference on which the suggestion is based [3]. An analysis script named “spinel” tests for the correct stoichiometry and warns in case errors are found. If not, it computes octahedral and tetrahedral occupancies and charges [4]. This is both more robust and more flexible than the spreadsheet approach commonly used in the geological sciences.
Since the scripts are in a generic language (python) they can be used to produce production quality plots, compare values against databases, compare against web sites, and do any sort of analysis the science requires.
Since both the input data and the output analyses are saved by the program, reproducibility is aided since you can see exactly what was done at a later date.
The software has been in use internally for two years and is robust for the workflow of the authors. In order to make the software broadly accessible and extensible by the community, we have made the software open source and hosted it on Github [5]. A short video showing the software in use is also hosted. The software is dependent on numpy[7], matplotlib[8] and wxPython[9]. We hope you will find Stoichiometry Fitter useful, enjoyable to use, and that it will increase your productivity.

# Statement of need

`Gala` is an Astropy-affiliated Python package for galactic dynamics. Python
enables wrapping low-level languages (e.g., C) for speed without losing
flexibility or ease-of-use in the user-interface. The API for `Gala` was
designed to provide a class-based and user-friendly interface to fast (C or
Cython-optimized) implementations of common operations such as gravitational
potential and force evaluation, orbit integration, dynamical transformations,
and chaos indicators for nonlinear dynamics. `Gala` also relies heavily on and
interfaces well with the implementations of physical units and astronomical
coordinate systems in the `Astropy` package [@astropy] (`astropy.units` and
`astropy.coordinates`).

`Gala` was designed to be used by both astronomical researchers and by
students in courses on gravitational dynamics or astronomy. It has already been
used in a number of scientific publications [@Pearson:2017] and has also been
used in graduate courses on Galactic dynamics to, e.g., provide interactive
visualizations of textbook material [@Binney:2008]. The combination of speed,
design, and support for Astropy functionality in `Gala` will enable exciting
scientific explorations of forthcoming data releases from the *Gaia* mission
[@gaia] by students and experts alike.

# Mathematics

Single dollars ($) are required for inline mathematics e.g. $f(x) = e^{\pi/x}$

Double dollars make self-standing equations:

$$\Theta(x) = \left\{\begin{array}{l}
0\textrm{ if } x < 0\cr
1\textrm{ else}
\end{array}\right.$$

You can also use plain \LaTeX for equations
\begin{equation}\label{eq:fourier}
\hat f(\omega) = \int_{-\infty}^{\infty} f(x) e^{i\omega x} dx
\end{equation}
and refer to \autoref{eq:fourier} from text.

# Citations

Citations to entries in paper.bib should be in
[rMarkdown](http://rmarkdown.rstudio.com/authoring_bibliographies_and_citations.html)
format.

If you want to cite a software repository URL (e.g. something on GitHub without a preferred
citation) then you can do it with the example BibTeX entry below for @fidgit.

For a quick reference, the following citation commands can be used:
- `@author:2001`  ->  "Author et al. (2001)"
- `[@author:2001]` -> "(Author et al., 2001)"
- `[@author1:2001; @author2:2001]` -> "(Author1 et al., 2001; Author2 et al., 2002)"

# Figures

Figures can be included like this:
![Caption for example figure.\label{fig:example}](figure.png)
and referenced from text using \autoref{fig:example}.

Figure sizes can be customized by adding an optional second parameter:
![Caption for example figure.](figure.png){ width=20% }

# Acknowledgements

We acknowledge contributions from Brigitta Sipocz, Syrtis Major, and Semyeong
Oh, and support from Kathryn Johnston during the genesis of this project.

# References
