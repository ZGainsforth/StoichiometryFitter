// This is the old version, using localstorage.
function saveAll() {
    /*
    * This function save all the data at the moment the web page is refreshed or submitted.
    */
    if (document.getElementById("phaseAnalysis").checked) { // Record whether the User check Phase Analysis.
      localStorage.setItem("phaseAnalysis", 1); // 1 represent true (checkbox selected)
    } else {
      localStorage.setItem("phaseAnalysis", 0); // 0 represent false (checkbox not selected)
    }
    localStorage.setItem("phase", document.getElementById("phase").value); // Store phase selection.
    if (document.getElementById("arbitraryAnalysis").checked) { // Record whether the User check Arbitrary Absorption.
      localStorage.setItem("arbitraryAnalysis", 1); // 1 represent true (checkbox selected)
    } else {
      localStorage.setItem("arbitraryAnalysis", 0); // 0 represent false (checkbox not selected)
    }
    localStorage.setItem("arbitrary", document.getElementById("arbitrary").value); // Store DetectorFile selection.
    if (document.getElementById("TEM").checked) { // Record whether the User check TEM Correction.
      localStorage.setItem("TEM", 1); // 1 represent true (checkbox selected)
    } else {
      localStorage.setItem("TEM", 0); // 0 represent false (checkbox not selected)
    }
    localStorage.setItem("density", document.getElementById("density").value); // Store density input.
    localStorage.setItem("degree", document.getElementById("degree").value); // Store degree input.
    localStorage.setItem("k-value", document.getElementById("k-value").value); // Store k-value selection.

    for (var i = 0; i < element2.length; i++) {
      localStorage.setItem(element2[i]+"1", document.getElementById(element2[i]+"1").value);
    }
    if (document.getElementById("k-factor").checked) { // Record whether the User check k-factors.
      localStorage.setItem("k-factor", 1); // 1 represent true (checkbox selected)
    } else {
      localStorage.setItem("k-factor", 0); // 0 represent false (checkbox not selected)
    }
    if (document.getElementById("oxygen").checked) { // Record whether the User check Oxygen.
      localStorage.setItem("oxygen", 1); // 1 represent true (checkbox selected)
    } else {
      localStorage.setItem("oxygen", 0); // 0 represent false (checkbox not selected)
    }
    
    // location.reload();
    return false;
    //return true;
}

// Function when you select "Counts" Input Type
function Countsss() {
  var input = document.getElementById("Counts").value;
  localStorage.setItem("inputType", input);
  localStorage.setItem("WhichType", 1);
  localStorage.setItem("k-factor-box", 1); // Un-Disable
  saveAll();
  location.reload();
}

// Function when you select "At %" Input Type
function Att() {
  var input = document.getElementById("At").value;
  localStorage.setItem("inputType", input)
  localStorage.setItem("WhichType", 2);
  localStorage.setItem("k-factor-box", 0); // Disable
  saveAll();
  location.reload();
}

// Function when you select "Wt %" Input Type
function Wt() {
  var input = document.getElementById("Weight").value;
  localStorage.setItem("inputType", input)
  localStorage.setItem("WhichType", 3);
  localStorage.setItem("k-factor-box", 0); // Disable
  saveAll();
  location.reload();
}

// Function when you select "Ox Weight %" Input Type
function OxWt() {
  var input = document.getElementById("Ox").value;
  localStorage.setItem("inputType", input)
  localStorage.setItem("WhichType", 4);
  localStorage.setItem("k-factor-box", 0); // Disable
  saveAll();
  location.reload();
}

// Elementary table.
const element2 = ["H","He","Li","Be","B","C","N","O","F","Ne","Na","Mg","Al","Si","P",
"S","Cl","Ar","K","Ca","Sc","Ti","V","Cr","Mn","Fe","Co","Ni","Cu","Zn","Ga","Ge","As","Se",
"Br","Kr","Rb","Sr","Y","Zr","Nb","Mo","Tc","Ru","Rh","Pd","Ag","Cd","In","Sn","Sb","Te","I",
"Xe","Cs","Ba","La","Ce","Pr","Nd","Pm","Sm","Eu","Gd","Tb","Dy","Ho","Er","Tm","Yb","Lu",
"Hf","Ta","W","Re","Os","Ir","Pt","Au","Hg","Tl","Pb","Bi","Po","At","Rn","Fr","Ra","Ac",
"Th","Pa","U","Np","Pu","Am","Cm","Bk","Cf","Es","Fm","Md","No","Lr","Rf","Db","Sg","Bh",
"Hs","Mt","Ds","Rg","Cn","Uut","Fl","Uup","Lv","Uus","Uuo"];

// Charge List.
const Stoich = [1.0, 0.0, 1.0, 2.0, 3.0, 4.0, -3.0, -2.0, -1.0, 0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 
  -2.0, -1.0, 0.0, 1.0, 2.0, 3.0, 4.0, 3.0, 3.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 0.0, 0.0, 
  0.0, -2.0, -1.0, 0.0, 1.0, 2.0, 3.0, 4.0, 0.0, 0.0, 0.0, 2.0, 0.0, 0.0, 0.0, 0.0, 0.0, 
  0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 
  0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
   0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 
   0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0];