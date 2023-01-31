//Using localStorage.
for (var i = 0; i < element2.length; i++) {
    if (localStorage.getItem(element2[i] + "1") == null) {
      document.getElementById(element2[i] + "1").value = 0;
    } else {
      document.getElementById(element2[i] + "1").value = localStorage.getItem(element2[i] + "1");
    }
  }
  // Check or uncheck Phase Analysis checkbox if in localStorage.
  if (localStorage.getItem("phaseAnalysis") != null) {
    if (localStorage.getItem("phaseAnalysis") == 1) {
      document.getElementById("phaseAnalysis").checked = true;
    } else {
      document.getElementById("phaseAnalysis").checked = false;
    }
  }
  // Obtain and fill in the phase selection if in localStorage.
  if (localStorage.getItem("phase") != null) {
    document.getElementById("phase").value = localStorage.getItem("phase");
  }
  // Check or uncheck Arbitrary Absorption checkbox if in localStorage.
  if (localStorage.getItem("arbitraryAnalysis") != null) {
    if (localStorage.getItem("arbitraryAnalysis") == 1) {
      document.getElementById("arbitraryAnalysis").checked = true;
    } else {
      document.getElementById("arbitraryAnalysis").checked = false;
    }
  }
  // Obtain and fill in the DetectorFile selection if in localStorage.
  if (localStorage.getItem("arbitrary") != null) {
    document.getElementById("arbitrary").value = localStorage.getItem("arbitrary");
  }
  // Check or uncheck TEM correction checkbox if in localStorage.
  if (localStorage.getItem("TEM") != null) {
    if (localStorage.getItem("TEM") == 1) {
      document.getElementById("TEM").checked = true;
    } else {
      document.getElementById("TEM").checked = false;
    }
  }
  // Obtain and fill in the density value if in localStorage.
  if (localStorage.getItem("density") != null) {
    document.getElementById("density").value = localStorage.getItem("density");
  }
  // Obtain and fill in the degree value if in localStorage.
  if (localStorage.getItem("degree") != null) {
    document.getElementById("degree").value = localStorage.getItem("degree");
  }
  // Check if k-factors is disabled.
  if (localStorage.getItem("k-factor-box") != null) {
    if (localStorage.getItem("k-factor-box") == 0) {
      document.getElementById("k-factor").disabled = true;
    } else {
      document.getElementById("k-factor").disabled = false;
    }
  }
  // Obtain and fill in the k-value if in localStorage.
  if (localStorage.getItem("k-value") != null) {
    document.getElementById("k-value").value = localStorage.getItem("k-value");
  }
  // Check or uncheck k-factor checkbox if in localStorage.
  if (localStorage.getItem("k-factor") != null) {
    if (localStorage.getItem("k-factor") == 1) {
      document.getElementById("k-factor").checked = true;
    } else {
      document.getElementById("k-factor").checked = false;
    }
  }

  // Check or uncheck oxygen checkbox if in localStorage.
  if (localStorage.getItem("oxygen") != null) {
    if (localStorage.getItem("oxygen") == 1) {
      document.getElementById("oxygen").checked = true;
    } else {
      document.getElementById("oxygen").checked = false;
    }
  }

  // InputType Checkbox Selection.
  if (localStorage.getItem("WhichType") == null || localStorage.getItem("WhichType") == 1) {
    document.getElementById("Counts").checked = true;
  } else if (localStorage.getItem("WhichType") == 2) {
    document.getElementById("At").checked = true;
  } else if (localStorage.getItem("WhichType") == 3) {
    document.getElementById("Weight").checked = true;
  } else if (localStorage.getItem("WhichType") == 4) {
    document.getElementById("Ox").checked = true;
  } else {
    document.write("There is a error!");
  }

  // CLear the Storage
  localStorage.clear();