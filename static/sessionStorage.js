//TODO: Change to SessionStorage
for (var i = 0; i < element2.length; i++) {
    if (sessionStorage.getItem(element2[i] + "1") == null) {
      document.getElementById(element2[i] + "1").value = 0;
    } else {
      document.getElementById(element2[i] + "1").value = sessionStorage.getItem(element2[i] + "1");
    }
  }
  // Check or uncheck Phase Analysis checkbox if in sessionStorage.
  if (sessionStorage.getItem("phaseAnalysis") != null) {
    if (sessionStorage.getItem("phaseAnalysis") == 1) {
      document.getElementById("phaseAnalysis").checked = true;
    } else {
      document.getElementById("phaseAnalysis").checked = false;
    }
  }
  // Obtain and fill in the phase selection if in sessionStorage.
  if (sessionStorage.getItem("phase") != null) {
    document.getElementById("phase").value = sessionStorage.getItem("phase");
  }
  // Check or uncheck Arbitrary Absorption checkbox if in sessionStorage.
  if (sessionStorage.getItem("arbitraryAnalysis") != null) {
    if (sessionStorage.getItem("arbitraryAnalysis") == 1) {
      document.getElementById("arbitraryAnalysis").checked = true;
    } else {
      document.getElementById("arbitraryAnalysis").checked = false;
    }
  }
  // Obtain and fill in the DetectorFile selection if in sessionStorage.
  if (sessionStorage.getItem("arbitrary") != null) {
    document.getElementById("arbitrary").value = sessionStorage.getItem("arbitrary");
  }
  // Check or uncheck TEM correction checkbox if in sessionStorage.
  if (sessionStorage.getItem("TEM") != null) {
    if (sessionStorage.getItem("TEM") == 1) {
      document.getElementById("TEM").checked = true;
    } else {
      document.getElementById("TEM").checked = false;
    }
  }
  // Obtain and fill in the density value if in sessionStorage.
  if (sessionStorage.getItem("density") != null) {
    document.getElementById("density").value = sessionStorage.getItem("density");
  }
  // Obtain and fill in the degree value if in sessionStorage.
  if (sessionStorage.getItem("degree") != null) {
    document.getElementById("degree").value = sessionStorage.getItem("degree");
  }
  // Check if k-factors is disabled.
  if (sessionStorage.getItem("k-factor-box") != null) {
    if (sessionStorage.getItem("k-factor-box") == 0) {
      document.getElementById("k-factor").disabled = true;
    } else {
      document.getElementById("k-factor").disabled = false;
    }
  }
  // Obtain and fill in the k-value if in sessionStorage.
  if (sessionStorage.getItem("k-value") != null) {
    document.getElementById("k-value").value = sessionStorage.getItem("k-value");
  }
  // Check or uncheck k-factor checkbox if in sessionStorage.
  if (sessionStorage.getItem("k-factor") != null) {
    if (sessionStorage.getItem("k-factor") == 1) {
      document.getElementById("k-factor").checked = true;
    } else {
      document.getElementById("k-factor").checked = false;
    }
  }

  // Check or uncheck oxygen checkbox if in sessionStorage.
  if (sessionStorage.getItem("oxygen") != null) {
    if (sessionStorage.getItem("oxygen") == 1) {
      document.getElementById("oxygen").checked = true;
    } else {
      document.getElementById("oxygen").checked = false;
    }
  }

  // InputType Checkbox Selection.
  if (sessionStorage.getItem("WhichType") == null || sessionStorage.getItem("WhichType") == 1) {
    document.getElementById("Counts").checked = true;
  } else if (sessionStorage.getItem("WhichType") == 2) {
    document.getElementById("At").checked = true;
  } else if (sessionStorage.getItem("WhichType") == 3) {
    document.getElementById("Weight").checked = true;
  } else if (sessionStorage.getItem("WhichType") == 4) {
    document.getElementById("Ox").checked = true;
  } else {
    document.write("There is a error!");
  }

  // CLear the Storage
  // sessionStorage.clear();