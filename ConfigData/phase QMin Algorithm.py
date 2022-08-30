__author1__ = 'Michael Ofengenden'
__copyright1__ = 'Copyright 2022, Michael Ofengenden'
__email1__ = 'michaelofengend@gmail.com'
__author2__ = 'Zhenbang Yu'
__copyright2__ = 'Copyright 2022, Zhenbang Yu'
__email2__ = 'roger_yu@berkeley.edu'
import csv
import pandas as pd
#import openpyxl
from numpy import *
from collections import *
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import time
import chromedriver_autoinstaller
if __name__ != '__main__':
    import PhysicsBasics as pb

def AnalyzePhase(AtPct=None, WtPct=None, OxWtPct=None, OByStoich=None):
    global OutStr
    OutStr = '--- QMin Mineral Analysis ---\n\n'
    #KnownElements = ['O', 'Na', 'Mg', 'Al', 'Si', 'P', 'S', 'K', 'Ca', 'Ti', 'V', 'Cr', 'Mn', 'Fe', 'Ni']
    Known2lements = ['Si', 'Ti', 'Al', 'Fe', 'Mn', 'Mg', 'Ca', 'Ba', 'Sr', 'Pb', 'Na', 'K', 'Rb']
    E = dict()
    frstRow = ['Point', 'SiO2', 'TiO2', 'Al2O3', 'FeOT', 'MnO', 'MgO', 'CaO', 'BaO', 'SrO', 'PbO', 'Na2O', 'K2O', 'Rb2O', 'Total']
    print(frstRow)
    scndRow = ['1']
    OutStr += "INPUT DATA:\n"
    for Element in Known2lements:
        x = round(eval('OxWtPct[pb.%s-1]'%(Element)), 4)
        E[Element] = x
        OutStr += f"{Element}, {x} \n"
        scndRow.append(f'{x}')
    summmm = 0
    for x in list(E.values()):
        summmm += x
    scndRow.append(f'{summmm}')
    print(scndRow)
    with open('qminFormat.csv', 'w') as csvfile:
        wr = csv.writer(csvfile)
        wr.writerow(frstRow)
        wr.writerow(scndRow)
    QminAlgo()
    return(OutStr)
   
def QminAlgo():
    global OutStr
    try:
        chromedriver_autoinstaller.install()
        chrome_options = Options()
        chrome_options.add_experimental_option("detach", True)
        driver = webdriver.Chrome(chrome_options=chrome_options)
    except:
        OutStr = "\n\nUser must install Chrome to use this method of QMin Analysis."
        return
    driver.get('https://apps.cprm.gov.br/qmin/')
    for i in range(30):
        time.sleep(1)
        try:
            element = driver.find_element(By.ID, "upload-data")
            break
        except:
            pass
    if element == None:
        print("User's connection is unstable")
    files = os.getcwd()+"/qminFormat.csv"
    JS_DROP_FILES = "var k=arguments,d=k[0],g=k[1],c=k[2],m=d.ownerDocument||document;for(var e=0;;){var f=d.getBoundingClientRect(),b=f.left+(g||(f.width/2)),a=f.top+(c||(f.height/2)),h=m.elementFromPoint(b,a);if(h&&d.contains(h)){break}if(++e>1){var j=new Error('Element not interactable');j.code=15;throw j}d.scrollIntoView({behavior:'instant',block:'center',inline:'center'})}var l=m.createElement('INPUT');l.setAttribute('type','file');l.setAttribute('multiple','');l.setAttribute('style','position:fixed;z-index:2147483647;left:0;top:0;');l.onchange=function(q){l.parentElement.removeChild(l);q.stopPropagation();var r={constructor:DataTransfer,effectAllowed:'all',dropEffect:'none',types:['Files'],files:l.files,setData:function u(){},getData:function o(){},clearData:function s(){},setDragImage:function i(){}};if(window.DataTransferItemList){r.items=Object.setPrototypeOf(Array.prototype.map.call(l.files,function(x){return{constructor:DataTransferItem,kind:'file',type:x.type,getAsFile:function v(){return x},getAsString:function y(A){var z=new FileReader();z.onload=function(B){A(B.target.result)};z.readAsText(x)},webkitGetAsEntry:function w(){return{constructor:FileSystemFileEntry,name:x.name,fullPath:'/'+x.name,isFile:true,isDirectory:false,file:function z(A){A(x)}}}}}),{constructor:DataTransferItemList,add:function t(){},clear:function p(){},remove:function n(){}})}['dragenter','dragover','drop'].forEach(function(v){var w=m.createEvent('DragEvent');w.initMouseEvent(v,true,true,m.defaultView,0,0,0,b,a,false,false,false,false,0,null);Object.setPrototypeOf(w,null);w.dataTransfer=r;Object.setPrototypeOf(w,DragEvent.prototype);h.dispatchEvent(w)})};m.documentElement.appendChild(l);l.getBoundingClientRect();return l"
    input = driver.execute_script(JS_DROP_FILES, element)
    input._execute('sendKeysToElement', {'value': [files], 'text': files})
    for i in range(30):
        time.sleep(1)
        try:
            resultGroup = driver.find_element(By.CLASS_NAME, "cell-table")
            break
        except:
            pass
    fullTable = driver.find_element(By.XPATH, '/html/body/div/div/div/div[2]/div/div[2]/div[1]/div/div[2]/div[1]/div/div/div[2]/div/div[2]/div[2]')
    info = fullTable.text.splitlines()[-1]
    ress  = resultGroup.text.splitlines()[-1]
    OutStr += "\n\nRESULTS:\n"
    OutStr += f"Predicted Group:          {ress.split()[0]}\n"
    OutStr += f"Quality Control:          {ress.split()[1]} {ress.split()[2]}\n"
    OutStr += f"Predicted Mineral:        {info.split()[0]}\n"
    OutStr += f"Quality Control:          {info.split()[1]} {info.split()[2]}\n"
    OutStr += f"Second Predicted Mineral: {info.split()[3]}"
    OutStr += f"\n\n\n\n\nRef: QMin Algorithm is used from https://apps.cprm.gov.br/qmin/. Authors of algorithm and paper are from Geological Survey of Brazil; Guilherme Ferreira, Marcos Ferreira, Iago Costa, Renato Bernardes, and Carlos Mota.\n\nOfficial Citation: \nSilva, Guilherme & Ferreira, Marcos & Costa, Iago & Bernardes, Renato & Mota, Carlos & Jiménez, Federico. (2021). Qmin – A machine learning-based application for processing and analysis of mineral chemistry data. Computers & Geosciences. 157. 10.1016/j.cageo.2021.104949. "



if __name__ == '__main__':
    import imp
    pb = imp.load_source('PhysicsBasics', '../PhysicsBasics.py')
    AnalyzePhase()
    
    
