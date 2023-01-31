{% extends "base.html" %}
{% block title %} 谭大狗 {% endblock %}

{% block content %}
<script language="javascript" type="text/javascript">
    const element = ["H","He","Li","Be","B","C","N","O","F","Ne","Na","Mg","Al","Si","P",
"S","Cl","Ar","K","Ca","Sc","Ti","V","Cr","Mn","Fe","Co","Ni","Cu","Zn","Ga","Ge","As","Se",
"Br","Kr","Rb","Sr","Y","Zr","Nb","Mo","Tc","Ru","Rh","Pd","Ag","Cd","In","Sn","Sb","Te","I",
"Xe","Cs","Ba","La","Ce","Pr","Nd","Pm","Sm","Eu","Gd","Tb","Dy","Ho","Er","Tm","Yb","Lu",
"Hf","Ta","W","Re","Os","Ir","Pt","Au","Hg","Tl","Pb","Bi","Po","At","Rn","Fr","Ra","Ac",
"Th","Pa","U","Np","Pu","Am","Cm","Bk","Cf","Es","Fm","Md","No","Lr","Rf","Db","Sg","Bh",
"Hs","Mt","Ds","Rg","Cn","Uut","Fl","Uup","Lv","Uus","Uuo"]

    document.write("<table>");
    document.write("<form>");
    document.write("<tr>");
    document.write("<th>Element</th> <th>Counts</th> <th>Charge</th>");
    document.write("</tr>");
    for (var a=0; a < element.length; a++) {
      document.write("<tr>");
      document.write("<td><label for=" + "name" + ">" + element[a]+ "</label></td>");
      document.write("<td><input type= \"number\" name= \"" + element[a] + "1" +"\" value=\"0\" /></td>");
      document.write("<td><input type= \"number\" name= \"" + element[a] + "2" +"\" /></td>");
      document.write("</tr>");
    }
    document.write("</form>");
    document.write("</table>");
    </script>
{% endblock %}


{% block content2 %}
<div>
<label for="phaseAnalysis">
    Phase Analysis: 
    <br>
    <input type="checkbox" id="phaseAnalysis" name="phaseAnalysis"> 
    <select name="phase" id="cars">
      <option value="Feldspar">Feldspar</option>
      <option value="QMin Algorithm">QMin Algorithm</option>
      <option value="Sulfide">Sulfide</option>
      <option value="Mole Fractions">Mole Fractions</option>
      <option value="Carbon">Carbon</option>
      <option value="Bulk Composition">Bulk Composition</option>
      <option value="Spinel">Spinel</option>
      <option value="Pyroxene ideal">Pyroxene ideal</option>
      <option value="Serpentine">Serpentine</option>
      <option value="Sheet Silicate Ternary">Sheet Silicate Ternary</option>
      <option value="Feldspathoid">Feldspathoid</option>
      <option value="GEMS Comparison">GEMS Comparison</option>
      <option value="Olivine">Olivine</option>
    </select>
</label>
</div>

<div>
    <label for="arbitraryAnalysis">Arbitrary Absorption:
<br>

<input type="checkbox" id="arbitraryAnalysis" name="arbitraryAnalysis">
<select name="arbitrary" id="cars">
  <option value="Titan Detector">Titan Detector Window</option>
</select>
</label>
</div>

<div>
    <label for="TEM">TEM Thickness Correction</label>
    <br>
    <input type="checkbox" id="TEM" name="TEM">
    <input name="density" type="text" value="<?php echo $density;?>">
    <!--
    <input type="text" name = "density"> -->
    <label for="cars">g/cm3 * nm</label>
    <input type="text" name = "degree" value="18">
    <label for="cars">takeoff in deg</label>
</div>

<div>
    <label for="k-factor">Apply k-factor for
    <br>
    <input type="checkbox" id="k-factor" name="k-factor">
    <select name="k-value" id="k-value">
        <option value="Titan 60 keV">Titan 60 keV</option>
        <option value="Titan 80 keV manual O">Titan 80 keV manual O</option>
        <option value="CM200 200keV">CM200 200keV</option>
        <option value="Titan 200keV">Titan 200keV</option>
        <option value="Titan 80keV">Titan 80keV</option>
        <option value="Titan 300keV">Titan 300keV</option>
      </select>
    </label>
</div>


<div>
    <label for="oxygen">Oxygen by Stoichiometry?
    <br>
    <input type="checkbox" id="oxygen" name="oxygen">
    <select name="k-value2" id="k-value2">
        <option value="Silicates">Silicates</option>
      </select>
    </label>
</div>


<div>
    <label for="IType"> Input Type:</label>
    <br>
    <input type="radio" id="html" name="Counts" value="Counts">
    <label for="html">Counts</label><br>
    <input type="radio" id="css" name="At" value="At %">
    <label for="css">At %</label><br>
    <input type="radio" id="javascript" name="Weight" value="Weight %">
    <label for="javascript">Wt %</label><br>
    <input type="radio" id="javascript" name="OxWeight" value="Ox Weight %">
    <label for="javascript">Ox Wt % %</label>
</div>

<div><?php
  echo "Hello World!";
  ?></div>


{% endblock %}

