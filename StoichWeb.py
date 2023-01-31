__author__ = 'Zhenbang Yu'
__copyright__ = 'Copyright 2022, Zhenbang Yu'
__email__ = 'roger_yu@berkeley.edu'


# TODO: Implement Save Input
# TODO: Implement Save Results
# TODO: Implement Save All
# TODO: Implement Open Input

# import flask relevant packages.
from flask import Flask, url_for, render_template, redirect, request

# import useful packages
import json
import pickle
import numpy as np
import os
from collections import OrderedDict
import pandas as pd
from matplotlib.figure import Figure
import mpld3

# import useful packages in original StoichiometryFitter
import ReportResults
import imp
import PhysicsBasics as pb
import CountsToQuantWeb
import PhaseFit

from ternary_diagram import TernaryDiagram

# Stoich = pd.read_csv("ConfigData/stoich Silicates.csv")
Stoich = np.genfromtxt('ConfigData/stoich Silicates.csv', dtype=None, comments='#', delimiter=',', skip_header=1, converters={1: lambda s: float(s)})

# initiate flask app
app = Flask(__name__)

# Everything in here.
@app.route('/', methods = ["POST","GET"])
def login():
    if request.method == "POST":
        # Detect not identified POST requests.
        if 'GO' not in request.form:
            return "<h1>There is a unidentified POST request!!</h1>"

        # Detect if the user click the submit button.
        if request.form['GO'] == "Go!":
            # Use to store matplotlib figures in html string, initiate as empty string.
            Fig1 = ""
            Fig2 = ""

            Counts = np.zeros(118)
            # Obtain InputType
            inputType = request.form["IType"]

            # Read in ElementsList
            element = ["H","He","Li","Be","B","C","N","O","F","Ne","Na","Mg","Al","Si","P","S","Cl","Ar","K","Ca","Sc","Ti","V","Cr","Mn","Fe","Co","Ni","Cu","Zn","Ga","Ge","As","Se","Br","Kr","Rb","Sr","Y","Zr","Nb","Mo","Tc","Ru","Rh","Pd","Ag","Cd","In","Sn","Sb","Te","I","Xe","Cs","Ba","La","Ce","Pr","Nd","Pm","Sm","Eu","Gd","Tb","Dy","Ho","Er","Tm","Yb","Lu","Hf","Ta","W","Re","Os","Ir","Pt","Au","Hg","Tl","Pb","Bi","Po","At","Rn","Fr","Ra","Ac","Th","Pa","U","Np","Pu","Am","Cm","Bk","Cf","Es","Fm","Md","No","Lr","Rf","Db","Sg","Bh","Hs","Mt","Ds","Rg","Cn","Uut","Fl","Uup","Lv","Uus","Uuo"]
            for i in range(len(element)):
                Counts[i] = request.form[element[i]+"1"]

            # Make the input human readable.
            InputDat = OrderedDict(list(zip(element, Counts)))
            ReportStr1 = ReportResults.FormatInputResults(InputDat, inputType)

            # Find out if there is a k-factor file to use.
            # TODO Add feature --- Allow user to upload their own k-factors file.
            if request.form.get("k-factor"):
                kfacsfile = request.form["k-value"]
            else:
                kfacsfile = None

            # Find out if there is an absorption correction to use.
            if request.form.get("arbitraryAnalysis"):
                DetectorFile = request.form["arbitrary"]
            else:
                DetectorFile = None

            # Find out if there is an absorption correction to do.
            AbsorptionCorrection = 0
            if request.form.get("TEM"):
                try:
                    # The text box uses nm.  Absorption path lengths are in microns, convert.
                    AbsorptionCorrection = float(request.form["density"])/1000
                    Takeoff = np.clip(float(request.form["degree"]), 0.1, 90) # Allow angles between 0.1 and 90 degrees.
                    # AbsorptionCorrection = request.form["density"]
                    # Takeoff = request.form["degree"]
                except:
                    # Error Message
                    print("Error")
                    return render_template('login.html')
            else:
                AbsorptionCorrection = 0
                Takeoff = 18

            # Find out if we are using oxygen by stoichiometry
            # TODO Implement new Feature: Allow user to upload their own Stoichiometry.
            if request.form.get("oxygen"):
                # Stoich is a list of tuples.  We want an array of atom charges from the 1 index of the tuples.  So unzip
                # the list into two tuples,
                # choose the tuple which corresponds to the charges not the atom names and feed it to numpy to make a vector.
                OByStoich = np.array(list(zip(*Stoich))[1])
                # OByStoich = request.form["k-value2"]
            else:
                OByStoich = None

            # Stuff the user entered data into a black box and get out At%, Wt% results.
            Quant = CountsToQuantWeb.GetAbundancesFromCounts(Counts, kfacsfile=kfacsfile, InputType= inputType, ArbitraryAbsorptionCorrection=DetectorFile, AbsorptionCorrection=AbsorptionCorrection, Takeoff=Takeoff, OByStoichiometry=OByStoich)
                                                            
            QuantNumbers = [a[1] for a in list(Quant.items())]
            AtPct, WtPct, OxWtPct, kfactors = list(zip(*QuantNumbers))

            # Make it human readable.
            ReportStr2 = ReportResults.FormatQuantResults(Quant, ArbitraryAbsorptionCorrection=DetectorFile, AbsorptionCorrection=AbsorptionCorrection,Takeoff=Takeoff,OByStoichiometry=OByStoich,kFactors=kfacsfile)

            # TODO: Error Handling

            """ DO CUSTOM PHASE ANALYSES """
            if request.form.get("phaseAnalysis"):
                # Construct the name of the py file containing the analysis function.
                PhaseFile = request.form["phase"]
                PhaseFile = 'ConfigData/phase ' + PhaseFile + '.py'
                # import it and run it.
                a = imp.load_source('AnalyzePhase', PhaseFile)
                # Pass in different parameters based on the input.
                if PhaseFile == "ConfigData/phase GEMS Comparison.py":
                    ReportStr3, Fig1, Fig2 = a.AnalyzePhase(AtPct, WtPct, OxWtPct, OByStoich)
                elif PhaseFile == "ConfigData/phase Sheet Silicate Ternary.py":
                    ReportStr3, Fig1, Fig2 = a.AnalyzePhase(AtPct, WtPct, OxWtPct, OByStoich)
                else:
                    ReportStr3 = a.AnalyzePhase(AtPct, WtPct, OxWtPct, OByStoich)
            else:
                ReportStr3 = ""
            
            # Generate final String
            FinalReport = ReportStr1 + ReportStr2 + ReportStr3
            # Change all the python new line to html new line.
            FinalReport = FinalReport.replace("\n", "<br>")
            # Change all the python space to html space
            FinalReport = FinalReport.replace(" ", "&nbsp;")
            
            # Generate webpage.
            # To see if there is any plot generated by Phase Analysis
            if Fig1 and Fig2:
                return render_template('result.html', Result = FinalReport, fig1 = Fig1, fig2 = Fig2)
            else:
                return render_template('result.html', Result = FinalReport)
    else:
        # Reload if no POST request received.
        return render_template('login.html')

# Run
if __name__ == '__main__':
    app.run(debug = True)