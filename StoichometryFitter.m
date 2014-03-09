function varargout = StoichometryFitter(varargin)
% STOICHOMETRYFITTER M-file for StoichometryFitter.fig
%      STOICHOMETRYFITTER, by itself, creates a new STOICHOMETRYFITTER or raises the existing
%      singleton*.
%
%      H = STOICHOMETRYFITTER returns the handle to a new STOICHOMETRYFITTER or the handle to
%      the existing singleton*.
%
%      STOICHOMETRYFITTER('CALLBACK',hObject,eventData,handles,...) calls the local
%      function named CALLBACK in STOICHOMETRYFITTER.M with the given input arguments.
%
%      STOICHOMETRYFITTER('Property','Value',...) creates a new STOICHOMETRYFITTER or raises the
%      existing singleton*.  Starting from the left, property value pairs are
%      applied to the GUI before StoichometryFitter_OpeningFcn gets called.  An
%      unrecognized property name or invalid value makes property application
%      stop.  All inputs are passed to StoichometryFitter_OpeningFcn via varargin.
%
%      *See GUI Options on GUIDE's Tools menu.  Choose "GUI allows only one
%      instance to run (singleton)".
%
% See also: GUIDE, GUIDATA, GUIHANDLES

% Edit the above text to modify the response to help StoichometryFitter

% Last Modified by GUIDE v2.5 22-Aug-2013 12:52:58

% Begin initialization code - DO NOT EDIT
gui_Singleton = 1;
gui_State = struct('gui_Name',       mfilename, ...
                   'gui_Singleton',  gui_Singleton, ...
                   'gui_OpeningFcn', @StoichometryFitter_OpeningFcn, ...
                   'gui_OutputFcn',  @StoichometryFitter_OutputFcn, ...
                   'gui_LayoutFcn',  [] , ...
                   'gui_Callback',   []);
if nargin && ischar(varargin{1})
    gui_State.gui_Callback = str2func(varargin{1});
end

if nargout
    [varargout{1:nargout}] = gui_mainfcn(gui_State, varargin{:});
else
    gui_mainfcn(gui_State, varargin{:});
end
% End initialization code - DO NOT EDIT


% --- Executes just before StoichometryFitter is made visible.
function StoichometryFitter_OpeningFcn(hObject, eventdata, handles, varargin)
    % This function has no output args, see OutputFcn.
    % hObject    handle to figure
    % eventdata  reserved - to be defined in a future version of MATLAB
    % handles    structure with handles and user data (see GUIDATA)
    % varargin   command line arguments to StoichometryFitter (see VARARGIN)

    % Choose default command line output for StoichometryFitter
    handles.output = hObject;

    % Update handles structure
    guidata(hObject, handles);

    % UIWAIT makes StoichometryFitter wait for user response (see UIRESUME)
    % uiwait(handles.figure1);

    % When the GUI first loads, we need to load all the minerals we know
    % about.
    InitializeMinerals(handles);


% --- Outputs from this function are returned to the command line.
function varargout = StoichometryFitter_OutputFcn(hObject, eventdata, handles) 
    % varargout  cell array for returning output args (see VARARGOUT);
    % hObject    handle to figure
    % eventdata  reserved - to be defined in a future version of MATLAB
    % handles    structure with handles and user data (see GUIDATA)

    % Get default command line output from handles structure
    varargout{1} = handles.output;


% --- Executes on selection change in listboxMinerals.
function listboxMinerals_Callback(hObject, eventdata, handles)
function listboxMinerals_CreateFcn(hObject, eventdata, handles)
    if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
        set(hObject,'BackgroundColor','white');
    end


function editC_Callback(hObject, eventdata, handles)
function editC_CreateFcn(hObject, eventdata, handles)
    if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
        set(hObject,'BackgroundColor','white');
    end

function editN_Callback(hObject, eventdata, handles)
function editN_CreateFcn(hObject, eventdata, handles)
    if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
        set(hObject,'BackgroundColor','white');
    end

function editO_Callback(hObject, eventdata, handles)
function editO_CreateFcn(hObject, eventdata, handles)
    if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
        set(hObject,'BackgroundColor','white');
    end

function editNa_Callback(hObject, eventdata, handles)
function editNa_CreateFcn(hObject, eventdata, handles)
    if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
        set(hObject,'BackgroundColor','white');
    end

function editMg_Callback(hObject, eventdata, handles)
function editMg_CreateFcn(hObject, eventdata, handles)
    if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
        set(hObject,'BackgroundColor','white');
    end

function editAl_Callback(hObject, eventdata, handles)
function editAl_CreateFcn(hObject, eventdata, handles)
    if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
        set(hObject,'BackgroundColor','white');
    end

function editSi_Callback(hObject, eventdata, handles)
function editSi_CreateFcn(hObject, eventdata, handles)
    if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
        set(hObject,'BackgroundColor','white');
    end

function editP_Callback(hObject, eventdata, handles)
function editP_CreateFcn(hObject, eventdata, handles)
    if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
        set(hObject,'BackgroundColor','white');
    end

function editS_Callback(hObject, eventdata, handles)
function editS_CreateFcn(hObject, eventdata, handles)
    if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
        set(hObject,'BackgroundColor','white');
    end

function editK_Callback(hObject, eventdata, handles)
function editK_CreateFcn(hObject, eventdata, handles)
    if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
        set(hObject,'BackgroundColor','white');
    end

function editCa_Callback(hObject, eventdata, handles)
function editCa_CreateFcn(hObject, eventdata, handles)
    if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
        set(hObject,'BackgroundColor','white');
    end

function editTi_Callback(hObject, eventdata, handles)
function editTi_CreateFcn(hObject, eventdata, handles)
    if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
        set(hObject,'BackgroundColor','white');
    end

function editCr_Callback(hObject, eventdata, handles)
function editCr_CreateFcn(hObject, eventdata, handles)
    if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
        set(hObject,'BackgroundColor','white');
    end

function editFe_Callback(hObject, eventdata, handles)
function editFe_CreateFcn(hObject, eventdata, handles)
    if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
        set(hObject,'BackgroundColor','white');
    end

function editNi_Callback(hObject, eventdata, handles)
function editNi_CreateFcn(hObject, eventdata, handles)
    if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
        set(hObject,'BackgroundColor','white');
    end

% --- Executes on button press in btnCompute.
function btnCompute_Callback(hObject, eventdata, handles)
    ComputeMinerals(handles);

% Set up the data structures which are used throughout the program.
function InitializeMinerals(handles)

    % Elements is the At % of the elements from the experimental data (usually
    % EDS).
    global Elements;
    global M1;
    % Minerals is of the form n = # minerals, and m = 30 (elements from H to
    % Zn).  Each element holds a stoichiometry value.  For example, SiO2 has 1
    % in Si and 2 in O.
    global Minerals;
    % Minerals is a cell array with m = # minerals.  Each cell contains the
    % mineral name for the mineral described in Minerals.
    global MineralNames;
    global C N O Na Mg Al Si P S K Ca Ti Cr Mn Fe Ni



    % We don't care about elements with Z above 30 right now.
    Elements = zeros(30,1);
    C  = 6; N = 7; O = 8; Na = 11; Mg = 12; Al = 13; Si = 14; P = 15; S = 16; Cl = 17; Ar = 18; K = 19; Ca = 20; Ti = 22; Cr = 24; Mn = 25; Fe = 26; Ni = 28; Zn = 30;
    M1 = Elements;


    % We populate an mxn matrix Minerals: m = 1:30 for each element up to
    % Zn.  n is the number of minerals in the database.  MineralNames is an
    % n cell array.  Each position contains the name of the nth mineral in
    % Minerals.
    
    % Elemental contituents of the minerals
    Minerals = [];
    % Forsterite Mg2 Si O4
    Minerals = [Minerals zeros(30,1)]; i = size(Minerals, 2); MineralNames = {'Forsterite (Mg2SiO4)'}; Minerals(Mg,i) = 2;  Minerals(Si,i) = 1; Minerals(O,i) = 4;
    % Fayalite Fe2 Si O4
    Minerals = [Minerals zeros(30,1)]; i = size(Minerals, 2); MineralNames{i} = 'Fayalite (Fe2SiO4)'; Minerals(Fe,i) = 2;  Minerals(Si,i) = 1; Minerals(O,i) = 4;
    % Tephroite Mn2 Si O4
    Minerals = [Minerals zeros(30,1)]; i = size(Minerals, 2); MineralNames{i} = 'Tephroite (Mn2SiO4)'; Minerals(Mn,i) = 2;  Minerals(Si,i) = 1; Minerals(O,i) = 4;
    % Troilite
    Minerals = [Minerals zeros(30,1)]; i = size(Minerals, 2); MineralNames{i} = 'Troilite (FeS)'; Minerals(Fe,i) = 1;  Minerals(S,i) = 1; 
    % Greigite
    Minerals = [Minerals zeros(30,1)]; i = size(Minerals, 2); MineralNames{i} = 'Greigite (Fe3S4)'; Minerals(Fe,i) = 3;  Minerals(S,i) = 4; 
    % Pentlandite
    Minerals = [Minerals zeros(30,1)]; i = size(Minerals, 2); MineralNames{i} = 'Pentlandite (Fe4.5Ni4.5S8)'; Minerals(Fe,i) = 4.5;  Minerals(Ni,i) = 4.5;  Minerals(S,i) = 8; 
    % Enstatite Mg2 Si2 O6
    Minerals = [Minerals zeros(30,1)]; i = size(Minerals, 2); MineralNames{i} = 'Enstatite (Mg2Si2O6)'; Minerals(Mg,i) = 2;  Minerals(Si,i) = 2; Minerals(O,i) = 6;
    % Ferrosilite Fe2 Si2 O6
    Minerals = [Minerals zeros(30,1)]; i = size(Minerals, 2); MineralNames{i} = 'Ferrosilite (Fe2Si2O6)'; Minerals(Fe,i) = 2;  Minerals(Si,i) = 2; Minerals(O,i) = 6;
    % Wollastonite Ca2 Si2 O6
    Minerals = [Minerals zeros(30,1)]; i = size(Minerals, 2); MineralNames{i} = 'Wollastonite (Ca2Si2O6)'; Minerals(Ca,i) = 2;  Minerals(Si,i) = 2; Minerals(O,i) = 6;
    % Diopside Mg Ca Si2 O6
    Minerals = [Minerals zeros(30,1)]; i = size(Minerals, 2); MineralNames{i} = 'Diopside (MgCaSi2O6)'; Minerals(Mg,i) = 1;  Minerals(Ca,i) = 1; Minerals(Si,i) = 2; Minerals(O,i) = 6;
    % Kosmochlor Na Cr Si2 O6
    Minerals = [Minerals zeros(30,1)]; i = size(Minerals, 2); MineralNames{i} = 'Kosmochlor (NaCrSi2O6)'; Minerals(Na,i) = 1;  Minerals(Cr,i) = 1; Minerals(Si,i) = 2; Minerals(O,i) = 6;
    % Hedenbergite Fe Ca Si2 O6
    Minerals = [Minerals zeros(30,1)]; i = size(Minerals, 2); MineralNames{i} = 'Hedenbergite (FeCaSi2O6'; Minerals(Fe,i) = 1;  Minerals(Ca,i) = 1; Minerals(Si,i) = 2; Minerals(O,i) = 6;
    % Jadeite Na Al Si2 O6
    Minerals = [Minerals zeros(30,1)]; i = size(Minerals, 2); MineralNames{i} = 'Jadeite (NaAlSi2O6)'; Minerals(Na,i) = 1;  Minerals(Al,i) = 1; Minerals(Si,i) = 2; Minerals(O,i) = 6;
    % Aegirine Na Fe Si2 O6
    Minerals = [Minerals zeros(30,1)]; i = size(Minerals, 2); MineralNames{i} = 'Aegirine (NaFe3+Si2O6)'; Minerals(Na,i) = 1;  Minerals(Fe,i) = 1; Minerals(Si,i) = 2; Minerals(O,i) = 6;
    % Kosmochlor Na Cr Si2 O6
    Minerals = [Minerals zeros(30,1)]; i = size(Minerals, 2); MineralNames{i} = 'Kosmochlor (NaCr3+Si2O6)'; Minerals(Na,i) = 1;  Minerals(Cr,i) = 1; Minerals(Si,i) = 2; Minerals(O,i) = 6;
    % Johannsenite Ca Mn Si2 O6
    Minerals = [Minerals zeros(30,1)]; i = size(Minerals, 2); MineralNames{i} = 'Johannsenite (CaMnSi2O6)'; Minerals(Ca,i) = 1;  Minerals(Mn,i) = 1; Minerals(Si,i) = 2; Minerals(O,i) = 6;
    % Aluminopyroxene Mg2 Al2 Si3 O12
    Minerals = [Minerals zeros(30,1)]; i = size(Minerals, 2); MineralNames{i} = 'Aluminopyroxene (Mg2Al2Si3O12)'; Minerals(Mg,i) = 2;  Minerals(Al,i) = 2; Minerals(Si,i) = 3; Minerals(O,i) = 12;
    % Buffonite Ca Ti0.5 Mg Fe3+ Si O6
    Minerals = [Minerals zeros(30,1)]; i = size(Minerals, 2); MineralNames{i} = 'Buffonite (CaTi0.5MgFeSiO6)'; Minerals(Ca,i) = 1;  Minerals(Ti,i) = 0.5; Minerals(Mg,i) = 1; Minerals(Fe,i) = 1; Minerals(Si,i) = 1; Minerals(O,i) = 6;
    % Alumino-buffonite Ca Ti0.5 Mg0.5 Al Si O6
    Minerals = [Minerals zeros(30,1)]; i = size(Minerals, 2); MineralNames{i} = 'Alumno-Buffonite (CaTi0.5Mg0.5AlSiO6)'; Minerals(Ca,i) = 1;  Minerals(Ti,i) = 0.5; Minerals(Mg,i) = 0.5; Minerals(Al,i) = 1; Minerals(Si,i) = 1; Minerals(O,i) = 6;
    % Gehlenite Ca2 Al2 Si O7
    Minerals = [Minerals zeros(30,1)]; i = size(Minerals, 2); MineralNames{i} = 'Gehlenite'; Minerals(Ca,i) = 2; Minerals(Al,i) = 2; Minerals(Si,i) = 1; Minerals(O,i) = 7;
    % Anorthite (Plag) Ca Al2 Si2 O8
    Minerals = [Minerals zeros(30,1)]; i = size(Minerals, 2); MineralNames{i} = 'Anorthite (Ca-feldspar, CaAl2Si2O8)'; Minerals(Ca,i) = 1; Minerals(Al,i) = 2; Minerals(Si,i) = 2; Minerals(O,i) = 8;
    % Albite (plag) Na Al Si3 O8
    Minerals = [Minerals zeros(30,1)]; i = size(Minerals, 2); MineralNames{i} = 'Albite (Na-feldspar, NaAlSi3O8)'; Minerals(Na,i) = 1; Minerals(Al,i) = 1; Minerals(Si,i) = 3; Minerals(O,i) = 8;
    % Orthoclase: Alkali Feldspar K Al Si3 O8
    Minerals = [Minerals zeros(30,1)]; i = size(Minerals, 2); MineralNames{i} = 'Orthoclase (K-feldspar, KAlSi3O8)'; Minerals(K,i) = 1; Minerals(Al,i) = 1; Minerals(Si,i) = 3; Minerals(O,i) = 8;
    % Nepheline Na Al Si O4
    Minerals = [Minerals zeros(30,1)]; i = size(Minerals, 2); MineralNames{i} = 'Nepheline (NaAlSiO4)'; Minerals(Na,i) = 1; Minerals(Al,i) = 1; Minerals(Si,i) = 1; Minerals(O,i) = 4;
    % SiO2 SiO2
    Minerals = [Minerals zeros(30,1)]; i = size(Minerals, 2); MineralNames{i} = 'SiO2'; Minerals(Si,i) = 1; Minerals(O,i) = 2;
    % Chromite FeCr2O4
    Minerals = [Minerals zeros(30,1)]; i = size(Minerals, 2); MineralNames{i} = 'Chromite (FeCr2O4)'; Minerals(Fe,i) = 1; Minerals(Cr,i) = 2; Minerals(O,i) = 4;
    % Hercynite FeAl2O4
    Minerals = [Minerals zeros(30,1)]; i = size(Minerals, 2); MineralNames{i} = 'Hercynite (FeAl2O4'; Minerals(Fe,i) = 1; Minerals(Al,i) = 2; Minerals(O,i) = 4;
    % Magnetite Fe3O4
    Minerals = [Minerals zeros(30,1)]; i = size(Minerals, 2); MineralNames{i} = 'Magnetite (Fe3O4)'; Minerals(Fe,i) = 3; Minerals(O,i) = 4;
    % Spinel MgAl2O4
    Minerals = [Minerals zeros(30,1)]; i = size(Minerals, 2); MineralNames{i} = 'Spinel (MgAl2O4)'; Minerals(Mg,i) = 1; Minerals(Al,i) = 2; Minerals(O,i) = 4;
    % Ulvospinel TiFe2O4
    Minerals = [Minerals zeros(30,1)]; i = size(Minerals, 2); MineralNames{i} = 'UlvospinelTiFe2O4'; Minerals(Ti,i) = 1; Minerals(Fe,i) = 2; Minerals(O,i) = 4;
    % Fo82 Smithsonian standard
    Minerals = [Minerals zeros(30,1)]; i = size(Minerals, 2); MineralNames{i} = 'Fo82 Springwater standard from Smithsonian'; Minerals(Fe,i) = 7*0.0505;  Minerals(Mg,i) = 7*0.2361;  Minerals(Si,i) = 7*0.1416; Minerals(O,i) = 7*0.5708;
    % Fe Schreibersite
    Minerals = [Minerals zeros(30,1)]; i = size(Minerals, 2); MineralNames{i} = 'Fe Schreibersite Fe3P'; Minerals(Fe,i) = 3;  Minerals(P,i) = 1;
    % Ni Schreibersite
    Minerals = [Minerals zeros(30,1)]; i = size(Minerals, 2); MineralNames{i} = 'Ni Schreibersite Ni3P'; Minerals(Ni,i) = 3;  Minerals(P,i) = 1;
    % Fe Barringerite
    Minerals = [Minerals zeros(30,1)]; i = size(Minerals, 2); MineralNames{i} = 'Fe Barringerite Fe2P'; Minerals(Fe,i) = 2;  Minerals(P,i) = 1;
    % Ni Barringerite
    Minerals = [Minerals zeros(30,1)]; i = size(Minerals, 2); MineralNames{i} = 'Ni Barringerite Fe2P'; Minerals(Ni,i) = 2;  Minerals(P,i) = 1;
    % Cronstedtite (Fe serpentine)
    Minerals = [Minerals zeros(30,1)]; i = size(Minerals, 2); MineralNames{i} = 'Cronstedtite (Fe3+)2(Fe2+)2SiO5(OH)4'; Minerals(Fe,i) = 4;  Minerals(Si,i) = 1;  Minerals(O,i) = 9;
    % Chrysotile
    Minerals = [Minerals zeros(30,1)]; i = size(Minerals, 2); MineralNames{i} = 'Chrysotile Mg3Si2O5(OH)4'; Minerals(Mg,i) = 3;  Minerals(Si,i) = 2;  Minerals(O,i) = 9;
    % Fe Clinochlore
    Minerals = [Minerals zeros(30,1)]; i = size(Minerals, 2); MineralNames{i} = 'Fe Clinochlore Fe5Al2Si3O18H8'; Minerals(Fe,i) = 5;  Minerals(Al,i) = 2;  Minerals(Si,i) = 3;  Minerals(O,i) = 18;
    % Mg Clinochlore
    Minerals = [Minerals zeros(30,1)]; i = size(Minerals, 2); MineralNames{i} = 'Mg Clinochlore Mg5Al2Si3O18H8'; Minerals(Mg,i) = 5;  Minerals(Al,i) = 2;  Minerals(Si,i) = 3;  Minerals(O,i) = 18;

    % Remember MineralNames is 1xn.
    MineralNames = MineralNames';
    
    % Add all the minerals to the mineral list box.
    set(handles.listboxMinerals, 'String', MineralNames);
    % Enable multiselection.
    set(handles.listboxMinerals, 'Max', length(MineralNames));
    set(handles.listboxMinerals, 'Min', 1);
    set(handles.listboxMinerals, 'FontSize', 10);


function ComputeMinerals(handles)
    % Elements is the At % of the elements from the experimental data (usually
    % EDS).
    global Elements;
    % Minerals is of the form n = # minerals, and m = 30 (elements from H to
    % Zn).  Each element holds a stoichiometry value.  For example, SiO2 has 1
    % in Si and 2 in O.
    global Minerals;
    % Minerals is a cell array with m = # minerals.  Each cell contains the
    % mineral name for the mineral described in Minerals.
    global MineralNames;
    global C N O Na Mg Al Si P S K Ca Ti Cr Mn Fe Ni
    
    ElementNames = {'H', 'He', 'Li', 'Be', 'B', 'C', 'N', 'O', 'F', 'Ne', 'Na', 'Mg', 'Al', 'Si', 'P', 'S', 'Cl', 'Ar', 'K', 'Ca', 'Sc', 'Ti', 'V', 'Cr', 'Mn', 'Fe', 'Co', 'Ni', 'Cu', 'Zn'};
    
    
    disp('Computing...')

    % First populate the elements array from the experimental values entered in
    % by the user.
    Elements(:) = 0;
    Elements(C) = str2num(get(findobj(gcf,'Tag','editC'), 'string'));
    Elements(N) = str2num(get(findobj(gcf,'Tag','editN'), 'string'));
    Elements(O) = str2num(get(findobj(gcf,'Tag','editO'), 'string'));
    Elements(Na) = str2num(get(findobj(gcf,'Tag','editNa'), 'string'));
    Elements(Mg) = str2num(get(findobj(gcf,'Tag','editMg'), 'string'));
    Elements(Al) = str2num(get(findobj(gcf,'Tag','editAl'), 'string'));
    Elements(Si) = str2num(get(findobj(gcf,'Tag','editSi'), 'string'));
    Elements(P) = str2num(get(findobj(gcf,'Tag','editP'), 'string'));
    Elements(S) = str2num(get(findobj(gcf,'Tag','editS'), 'string'));
    Elements(K) = str2num(get(findobj(gcf,'Tag','editK'), 'string'));
    Elements(Ca) = str2num(get(findobj(gcf,'Tag','editCa'), 'string'));
    Elements(Ti) = str2num(get(findobj(gcf,'Tag','editTi'), 'string'));
    Elements(Cr) = str2num(get(findobj(gcf,'Tag','editCr'), 'string'));
    Elements(Mn) = str2num(get(findobj(gcf,'Tag','editMn'), 'string'));
    Elements(Fe) = str2num(get(findobj(gcf,'Tag','editFe'), 'string'));
    Elements(Ni) = str2num(get(findobj(gcf,'Tag','editNi'), 'string'));

    % Now populate the minerals list. Start with everything available.
    MineralsBasis = Minerals;
    % And delete anything not selected.
    %set(handles.listboxMinerals,'Max',2); 
    SelectedMinerals = get(findobj(gcf,'Tag','listboxMinerals'),'Value');

    MineralsAbundance = ones(length(MineralsBasis), 1);

    % Exclude oxygen from the computation if desired.
    ElementsCalc = Elements;
    MineralsBasisCalc = MineralsBasis;
%     if(ExcludeOxygen == 1)
%         ElementsCalc(O) = 0;
%         MineralsBasisCalc(O,:) = 0;
%     end

    % Exclude minerals that are not selected in the list.
    for i=1:size(MineralsBasisCalc,2)
        % If this was not a selected elements per SelectedMinerals, then
        % zero out it's stoichiometry.  Then it can't fit anything.
        if(isempty(find(SelectedMinerals == i, 1)))
            MineralsBasisCalc(:,i) = 0;
        end
    end
    %MineralsBasisCalc(:,3) = 0;
    
    % Do we use measured Oxygen or get it from stoichiometry?
    if(get(handles.chkStoich, 'Value') == get(handles.chkStoich, 'Max'))
        OxygenByStoichiometry = 1;
        % Start off by ignoring any entered O number and calculate stoich
        % to start.
        ElementsCalc = CalculateOxygenByStoichiometry(ElementsCalc);
    else
        OxygenByStoichiometry = 0;
    end
    
    % Choose a thickness of carbon and sample
    if(get(handles.chkCarbonCorr, 'Value') == get(handles.chkCarbonCorr, 'Max'))
        % Value == max means the checkbox is checked.  We don't know
        % thickness, of the C contamination coat, but we will fit it.
        CarbonThickness = 10;
        DoCarbonCorr = 1;
    else
        % -1 means we don't do a carbon coating/contamination correction.
        CarbonThickness = 0;
        DoCarbonCorr=0;
    end
    if(get(handles.chkThicknessCorr, 'Value') == get(handles.chkThicknessCorr, 'Max'))
        % ThicknessCorr = 0 means no thickness correction
        % 1 means compute the best fit thickness.
        % 2 means use the specified number in the text box.
        SpecimenThickness = str2num(get(handles.editThickness, 'String'));
        SpecimenThickness = sqrt(SpecimenThickness);
        if(SpecimenThickness == 0)
            % Since no user specified thickness was entered, yet we are
            % supposed to fit it, give it an initial guess (about 25 nm).
            SpecimenThickness = 5;
            DoThicknessCorr = 1;
        else
            DoThicknessCorr = 2;
        end
    else
        SpecimenThickness = 0;
        DoThicknessCorr = 0;
    end

    % Get a first good guess of the mineral abundance.
    MineralsAbundanceFit = lsqnonneg(MineralsBasisCalc, ElementsCalc);
    
    % Now do the refined version which also does the Carbon and thickness
    % corrections.
    options = optimset('MaxIter', 1e12, 'TolFun', 1, 'Display', 'final', 'TolX', 1e-3);
    FittedParameters = abs(fminsearch(@ComputeResidual, [MineralsAbundanceFit', CarbonThickness, SpecimenThickness]', options, MineralsBasisCalc, ElementsCalc, DoCarbonCorr, DoThicknessCorr, SpecimenThickness, OxygenByStoichiometry));
   
    OutText = ['Residual = ' num2str(ComputeResidual(FittedParameters, MineralsBasisCalc, ElementsCalc, DoCarbonCorr, DoThicknessCorr, SpecimenThickness, OxygenByStoichiometry))];
    
    MineralsAbundanceFit = FittedParameters(1:length(FittedParameters)-2);
    CarbonThickness = FittedParameters(length(FittedParameters)-1);
    % If we were fitting the specimen thickness, then pull it from the fit.  Otherwise, we know it from the input. 
    if(DoThicknessCorr == 1)
        SpecimenThickness = FittedParameters(length(FittedParameters)); 
    end

    ElementsSimulated = MineralsBasisCalc*MineralsAbundanceFit;

    % O by stoichiometry (done before thickness corrections so the O's
    % absorption can be included -- at least to first order.
%     if(OxygenByStoichiometry==1)
%         ElementsCalc = CalculateOxygenByStoichiometry(ElementsCalc);
%     end
    % Do Carbon and thickness corrections.
    if(DoCarbonCorr==1)
        ElementsCalc = DoCarbonCorrection(ElementsCalc, CarbonThickness);
    end
    if(DoThicknessCorr~=0)
        ElementsCalc = DoThicknessCorrection(ElementsCalc, SpecimenThickness);
    end
    % And redo O stoichiometry now that we've corrected all the cations.
    if(OxygenByStoichiometry==1)
        ElementsCalc = CalculateOxygenByStoichiometry(ElementsCalc);
    end

    % And we have to normalize ElementsSimulated and ElementCalc so we can
    % compare them.
    ElementsCalc = ElementsCalc/sum(ElementsCalc)*100;
    ElementsSimulated = ElementsSimulated/sum(ElementsSimulated)*100;

    CurrentFigure = gcf;    % current figure is the dialog.  Remember it for later.
    h = figure(2);
    pos = get(h,'Position');
    pos(3:4) = [700 450];
    set(h,'Position',pos);
%     set(0,'Units','pixels');
%     set(h, 'Outerposition', [500, 500, 200, 200]);
    subplot(1,4, [1, 2, 3])
    x = 1:30;
    % As a bar graph
    bar(x, [ElementsCalc,ElementsSimulated], 'LineWidth', 0.1);
    colormap cool
    % Or as a line graph
%     plot(x, ElementsCalc, 'LineWidth', 1.5);
%     hold on
%     plot(x, ElementsSimulated, 'LineWidth', 1, 'Color', [0 1 0]);
%     hold off 
    set(gca,'XTick',x)
    set(gca,'XTickLabel',ElementNames)
    legend('Experimental', 'Fit');
    axis([0 30 0 100])

    % Normalize MineralsAbundanceFit
    MineralsAbundanceFit = MineralsAbundanceFit/sum(MineralsAbundanceFit);
    
%     % Print out the sum abundances:
%     OutText = [OutText char(10) 'Total atomic %: ' num2str(sum(Elements(:)))];

    % Print out the percent minerals.

    for i=1:length(MineralNames)
        % Only display minerals that were selected.
        if(~isempty(find(SelectedMinerals == i, 1)))
            OutText = [OutText char(10) MineralNames{i} ' = ' num2str(MineralsAbundanceFit(i))];
        end
    end
    
    % If both forsterite and fayalite were selected, print a Fo #.
    FoIndex = find(strncmp(MineralNames, 'Forsterite', length('Forsterite')));
    FaIndex = find(strncmp(MineralNames, 'Fayalite', length('Fayalite')));
    if sum(SelectedMinerals == FoIndex) && sum(SelectedMinerals == FaIndex)
        OutText = [OutText char(10) 'Fo # = ' num2str(MineralsAbundanceFit(FoIndex)/(MineralsAbundanceFit(FoIndex)+MineralsAbundanceFit(FaIndex)))];
    end
%     % If both Enstatite and Ferrosilite were selected, print an En #.
%     EnIndex = find(strncmp(MineralNames, 'Enstatite', length('Enstatite')));
%     FsIndex = find(strncmp(MineralNames, 'Ferrosilite', length('Ferrosilite')));
%     if sum(SelectedMinerals == EnIndex) && sum(SelectedMinerals == FsIndex)
%         OutText = [OutText char(10) 'En # = ' num2str(MineralsAbundanceFit(EnIndex)/(MineralsAbundanceFit(EnIndex)+MineralsAbundanceFit(FsIndex)))];
%     end
    % If multiple pyroxenes were selected, print an En # and Wo#.
    EnIndex = find(strncmp(MineralNames, 'Enstatite', length('Enstatite')));
    FsIndex = find(strncmp(MineralNames, 'Ferrosilite', length('Ferrosilite')));
    WoIndex = find(strncmp(MineralNames, 'Wollastonite', length('Wollastonite')));
    if sum(SelectedMinerals == EnIndex) && sum(SelectedMinerals == FsIndex) && sum(SelectedMinerals == WoIndex)
        OutText = [OutText char(10) 'En # = ' num2str(MineralsAbundanceFit(EnIndex)/(MineralsAbundanceFit(EnIndex)+MineralsAbundanceFit(FsIndex)+MineralsAbundanceFit(WoIndex)))];
        OutText = [OutText char(10) 'Wo # = ' num2str(MineralsAbundanceFit(WoIndex)/(MineralsAbundanceFit(EnIndex)+MineralsAbundanceFit(FsIndex)+MineralsAbundanceFit(WoIndex)))];
    elseif sum(SelectedMinerals == EnIndex) && sum(SelectedMinerals == FsIndex)
        OutText = [OutText char(10) 'En # = ' num2str(MineralsAbundanceFit(EnIndex)/(MineralsAbundanceFit(EnIndex)+MineralsAbundanceFit(FsIndex)))];
    end
    % If both Anorthite and Albite were selected, print an An #.
    AnIndex = find(strncmp(MineralNames, 'Anorthite', length('Anorthite')));
    AlIndex = find(strncmp(MineralNames, 'Albite', length('Albite')));
    if sum(SelectedMinerals == AnIndex) && sum(SelectedMinerals == AlIndex)
        OutText = [OutText char(10) 'An # = ' num2str(MineralsAbundanceFit(AnIndex)/(MineralsAbundanceFit(AnIndex)+MineralsAbundanceFit(AlIndex)))];
    end
    % If both Alkali Fedlspar and Albite were selected, print an An #.
    KIndex = find(strncmp(MineralNames, 'Orthoclase', length('Orthoclase')));
    AlIndex = find(strncmp(MineralNames, 'Albite', length('Albite')));
    if sum(SelectedMinerals == KIndex) && sum(SelectedMinerals == AlIndex)
        OutText = [OutText char(10) 'Or # = ' num2str(MineralsAbundanceFit(KIndex)/(MineralsAbundanceFit(KIndex)+MineralsAbundanceFit(AlIndex)))];
    end
    
    if(OxygenByStoichiometry==1)
        OutText = [OutText char(10) 'Oxygen by stoichiometry'];
    end
    if(DoCarbonCorr==1)
        OutText = [OutText char(10) 'Carbon thickness = ' num2str(CarbonThickness) ' nm'];
    end
    if(DoThicknessCorr==1)
        % Remember specimen thickness is passed around as it's sqrt.
        OutText = [OutText char(10) 'Specimen thickness fit = ' num2str(SpecimenThickness^2) ' nm' char(10) '       (Assuming 100 atoms/nm)'];
    end
    if(DoThicknessCorr==2)
        % Remember specimen thickness is passed around as it's sqrt.
        OutText = [OutText char(10) 'Specimen thickness = ' num2str(SpecimenThickness^2) ' nm (input)' char(10) '       (Assuming 100 atoms/nm)'];
    end
   
    %text(30,40, OutText);
    %disp(OutText);
    
    % Finally, output the new At%'s to the command window.
    %disp('Composition from mineral fit:')
    OutText = [OutText char(10) 'Composition from mineral fit:'];
    for i=1:30
        if ElementsSimulated(i) > 0
            OutText = [OutText char(10) sprintf('%s: %2.02f At%%', ElementNames{i}, ElementsSimulated(i))];
            fprintf(1, 'Element %g: %2.02f At%%\n', i, ElementsSimulated(i));
            %num2str(i) ': ' num2str(ElementsSimulated(i)) ' At%']);
        end
    end
    disp('');
    
    %disp('Composition with just k-facs and thickness correction:');
    OutText = [OutText char(10) 'Composition with just k-facs' char(10) '       and thickness correction:'];
    for i=1:30
        if ElementsCalc(i) > 0
            OutText = [OutText char(10) sprintf('%s: %2.02f At%%', ElementNames{i}, ElementsCalc(i))];
            fprintf(1, 'Element %g: %2.02f At%%\n', i, ElementsCalc(i));
          %disp(['Element ' num2str(i) ': ' num2str(ElementsCalc(i)) ' At%']);
        end
    end
   
    subplot(1, 4, 4)
    hold off
    plot(NaN)
    axis([0 10 0 10])
    axis off
    text(0.2,5, OutText);
    disp(OutText);

    % Now that we are done drawing things in the figure, switch gcf back to
    % our current dialog box.
    figure(CurrentFigure);
    
    disp('Done');
    disp(' ');


function Residual = ComputeResidual(MineralsAbundanceFit, MineralsBasisCalc, ElementsCalc, DoCarbonCorr, DoThicknessCorr, UserSpecifiedSpecimenThickness, OxygenByStoichiometry)

    global C N O Na Mg Al Si P S K Ca Ti Cr Mn Fe Ni

    % If the fit goes bad, then we'll make the residual a little worse so
    % the optimizer steers away from that parameter space.  (This happens
    % for example when the thickness correction gets too thick -- microns).
    persistent LastResidual;
    if(isempty(LastResidual))
        LastResidual = 1;
    end
    
    % Make sure all values are positive.  We can't have a negative
    % abundance of material.
    MineralsAbundanceFit(MineralsAbundanceFit<0) = 0;
        
    % Break out the carbon and thickness correction numbers
    SpecimenThickness = MineralsAbundanceFit(length(MineralsAbundanceFit));
    MineralsAbundanceFit(length(MineralsAbundanceFit)) = [];
    CarbonThickness = MineralsAbundanceFit(length(MineralsAbundanceFit));
    MineralsAbundanceFit(length(MineralsAbundanceFit)) = [];
    
    % For DoThicknessCorr=2, then we are not supposed to fit the thickness
    % but use the value input by the user.  This will be a thickness
    % measured by CBED, or EELS or STXM or something.
    if(DoThicknessCorr == 2)
        SpecimenThickness = UserSpecifiedSpecimenThickness;
    end
    
    
    ElementsSimulated = MineralsBasisCalc*MineralsAbundanceFit;
    
%     % If O by stoichiometry, then we need to calculate the abundance of O
%     % before we do thickness corrections, etc.
%     if(OxygenByStoichiometry==1)
%         ElementsCalc = CalculateOxygenByStoichiometry(ElementsCalc);
%     end

    % Do Carbon and thickness corrections.
    if(DoCarbonCorr==1)
        ElementsCalc = DoCarbonCorrection(ElementsCalc, CarbonThickness);
    end
    % Catch if the carbon correction died.
    if(ElementsCalc(1) == 1)
        LastResidual = LastResidual*1.1;
        return;
    end
    if(DoThicknessCorr~=0)
        ElementsCalc = DoThicknessCorrection(ElementsCalc, SpecimenThickness);
    end
    % Catch if the thickness correction died.
    if(ElementsCalc(1) == 1)
        LastResidual = LastResidual*1.1;
        Residual = LastResidual;
        return;
    end
    
    % And we also have to do O stoichiometry after the thickness
    % corrections because they will alter the number of cations and hence
    % the O atoms.
    if(OxygenByStoichiometry==1)
        ElementsCalc = CalculateOxygenByStoichiometry(ElementsCalc);
    end

    
    % And we have to normalize ElementsSimulated and ElementCalc so we can
    % compare them.
    ElementsCalc = ElementsCalc/sum(ElementsCalc)*100;
    ElementsSimulated = ElementsSimulated/sum(ElementsSimulated)*100;
    
    % Since not all the minerals were included in a fit, if the user has
    % entered in minor elements (such as Mn in olivine) these will always
    % not fit.  Therefore, we want to exclude these from the residual.  It
    % is up to the user to include the right minerals.
    ElementMask = logical(sum(MineralsBasisCalc,2));
    ElementsCalc = ElementsCalc.*ElementMask;
        
    % We want the error to be based on fraction difference, not absolute
    % difference.  This is because O is always by far the most abundant,
    % and if you have e.g. 5% of Fe, it will eliminate all the iron to make
    % the O fit.

    % Compute the residual
    Residuals = abs(ElementsSimulated-ElementsCalc)./ElementsCalc;
    Residuals(isnan(Residuals)) = 0;
    Residuals(isinf(Residuals)) = 1;
    %Residuals = (ElementsSimulated-ElementsCalc).^0.01;
    
    Residual = sum(Residuals);
    
    % Note this residual for next time.
    LastResidual = Residual;
        
%     % Show the quality of the fit.
%     x = 1:30;
%     plot(x, ElementsCalc, 'LineWidth', 1.5);
%     hold on
%     plot(x, ElementsSimulated, 'LineWidth', 1, 'Color', [0 1 0]);
%     hold off 
%     legend('Experimental', 'Fit');
%     Residual
%     
%     pause(0.01)


function btnNormalize_Callback(hObject, eventdata, handles)
    
    global Elements;
    global C N O Na Mg Al Si P S K Ca Ti Cr Mn Fe Ni

    % First populate the elements array from the experimental values entered in
    % by the user.
    Elements(:) = 0;
    Elements(C) = str2num(get(handles.editC, 'string'));
    Elements(N) = str2num(get(handles.editN, 'string'));
    Elements(O) = str2num(get(handles.editO, 'string'));
    Elements(Na) = str2num(get(handles.editNa, 'string'));
    Elements(Mg) = str2num(get(handles.editMg, 'string'));
    Elements(Al) = str2num(get(handles.editAl, 'string'));
    Elements(Si) = str2num(get(handles.editSi, 'string'));
    Elements(P) = str2num(get(handles.editP, 'string'));
    Elements(S) = str2num(get(handles.editS, 'string'));
    Elements(K) = str2num(get(handles.editK, 'string'));
    Elements(Ca) = str2num(get(handles.editCa, 'string'));
    Elements(Ti) = str2num(get(handles.editTi, 'string'));
    Elements(Cr) = str2num(get(handles.editCr, 'string'));
    Elements(Mn) = str2num(get(handles.editMn, 'string'));
    Elements(Fe) = str2num(get(handles.editFe, 'string'));
    Elements(Ni) = str2num(get(handles.editNi, 'string'));
    
    % Now get the total elemental abundances.
    SumAbundance = sum(Elements);
    
    % Normalize to 100% now.
    Elements = Elements./SumAbundance.*100;
    
    % And populate the dialog with the new values.
    set(handles.editC, 'String', num2str(Elements(C)));
    set(handles.editN, 'String', num2str(Elements(N)));
    set(handles.editO, 'String', num2str(Elements(O)));
    set(handles.editNa, 'String', num2str(Elements(Na)));
    set(handles.editMg, 'String', num2str(Elements(Mg)));
    set(handles.editAl, 'String', num2str(Elements(Al)));
    set(handles.editSi, 'String', num2str(Elements(Si)));
    set(handles.editP, 'String', num2str(Elements(P)));
    set(handles.editS, 'String', num2str(Elements(S)));
    set(handles.editK, 'String', num2str(Elements(K)));
    set(handles.editCa, 'String', num2str(Elements(Ca)));
    set(handles.editTi, 'String', num2str(Elements(Ti)));
    set(handles.editCr, 'String', num2str(Elements(Cr)));
    set(handles.editMn, 'String', num2str(Elements(Mn)));
    set(handles.editFe, 'String', num2str(Elements(Fe)));
    set(handles.editNi, 'String', num2str(Elements(Ni)));
    



function btnZero_Callback(hObject, eventdata, handles)

    global Elements;
    
    % Zero out the elements.
    Elements(:) = 0;

    % Zero out the dialog.
    set(handles.editC, 'String', 0);
    set(handles.editN, 'String', 0);
    set(handles.editO, 'String', 0);
    set(handles.editNa, 'String', 0);
    set(handles.editMg, 'String', 0);
    set(handles.editAl, 'String', 0);
    set(handles.editSi, 'String', 0);
    set(handles.editP, 'String', 0);
    set(handles.editS, 'String', 0);
    set(handles.editK, 'String', 0);
    set(handles.editCa, 'String', 0);
    set(handles.editTi, 'String', 0);
    set(handles.editCr, 'String', 0);
    set(handles.editMn, 'String', 0);
    set(handles.editFe, 'String', 0);
    set(handles.editNi, 'String', 0);


% --- Executes on button press in chkCarbonCorr.
function chkCarbonCorr_Callback(hObject, eventdata, handles)
% hObject    handle to chkCarbonCorr (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hint: get(hObject,'Value') returns toggle state of chkCarbonCorr


% --- Executes on button press in chkThicknessCorr.
function chkThicknessCorr_Callback(hObject, eventdata, handles)
% hObject    handle to chkThicknessCorr (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hint: get(hObject,'Value') returns toggle state of chkThicknessCorr

% Oxygen is notorious for giving bad measurements.  We can do better
% analyses if we keep the oxygen measurements, but only within one well defined
% mineral system.  If we have multimodes or are unsure which mineral system
% we are dealing with, then the O measurments will kill us.  Use
% stoichiometry instead.
function Elements = CalculateOxygenByStoichiometry(Elements)
    global C N O Na Mg Al Si P S Cl Ar K Ca Ti Cr Mn Fe Ni Zn

    OxStates = zeros(30,1);
    
    OxStates(Na) = 1;
    OxStates(Mg) = 2;
    OxStates(Al) = 3;
    OxStates(Si) = 4;
    OxStates(P) = 5;
    OxStates(K) = 4;
    OxStates(Ca) = 2;
    OxStates(Ti) = 4;
    OxStates(Cr) = 3;
    OxStates(Mn) = 2;
    OxStates(Fe) = 2;
    OxStates(Ni) = 2;
    OxStates(Zn) = 2;
    
    Oxygens = sum(Elements.*OxStates)/2;
    Elements(O) = Oxygens;

% Do a carbon contamination correction.
function ElementsSimulated = DoCarbonCorrection(ElementsSimulated, CarbonThickness)

    % The optimizer may try really thick thicknesses.  At some point the
    % math breaks down and we start producing NaN's and Inf's which then
    % make the residual look low even though it isn't.  So let's max out at
    % 5 microns.
    if(CarbonThickness > 5000)
        ElementsSimulated(1) = 1;  % Populating hydrogen is an error code for something went wrong.
        return;
    end
    
    NumRecognizedElements = 17;
    
    % Relative attenuation lengths for the various photons in C.  (See
    % "Absorption Lengths.numbers"
    k = 100000;
    A = [   k;k;k;k;k;
            1438.7
            146.4
            299.9
            k;k;
            1885.8
            3199.4
            5217.4
            8229.5
            12556.3
            18918.3
            k;k
            55989.1
            77862.3
            k;
            144247.9
            k;
            254222.2
            332597.1
            430755.4
            k;
            703278.4
            886239.0;
            k];
        
    % 0.69875 is the value for all the constants of mu when this is carbon
    % at a density of 2 g/cm3.
    ElementsSimulated = ElementsSimulated.*exp(0.69875*CarbonThickness./A);
    
    
function ElementsSimulated = DoThicknessCorrection(ElementsSimulated, SpecimenThickness)

    % To increase the search range for Specimen Thickness, it is passed to
    % fminsearch as the sqrt of the actual value.  We need the actual value
    % now.
    SpecimenThickness = SpecimenThickness^2;
    
    % The optimizer may try really thick thicknesses.  At some point the
    % math breaks down and we start producing NaN's and Inf's which then
    % make the residual look low even though it isn't.  So let's max out at
    % 5 microns.
    if(SpecimenThickness > 1000)
        ElementsSimulated(1) = 1;  % Populating hydrogen is an error code for something went wrong.
        return;
    end

    NumRecognizedElements = 17;
    
    % Relative absorption lengths from "Absorption Lengths.numbers"
    % These constants are f'' from Hephaestus
    % T = exp(-n mu t), n is #atoms/vol, mu is area, t is thickness.
    % At E= 
    A = [   1438.7      811.8       490.5       119.8	82.9	59.6	45.2	34.6	27.4	194.6	163.8	125.3	85.6	71.2	62.5	46.0	38.9;
            146.4       1824.1      1119.7      274.9	188.5	133.5	97.8	74.0	57.7	30.4	28.5	223.0	157.0	133.0	115.2	85.2	71.2;
            299.9       181.4       2241.5      568.8	389.1	272.2	198.2	147.1	113.7	57.6	48.1	39.2	270.9	233.2	201.5	149.3	125.8;
            1885.8      1055.1      660.4       3385.4	2299.6	1572.3	1131.8	833.8	631.9	305.1	248.8	172.1	124.1	107.4	93.7	72.3	71.1;
            3199.4      1767.2      1090.2      360.6	3796.5	2588.9	1859.3	1367.8	1034.7	495.4	402.1	276.2	197.6	170.0	147.1	112.6	98.8;
            5217.4      2846.8      1734.6      562.4	418.3	4082.8	2933.6	2155.9	1628.2	775.7	627.3	428.0	304.5	261.1	225.1	170.9	149.8;
            8229.5      4449.4      2679.7      844.6	629.8	479.9	4470.1	3290.7	2481.9	1178.6	950.5	644.6	456.5	390.3	335.8	253.6	221.9;
            12556.3     6739.1      4017.3      1235.9	914.7	698.6	544.1	4856.7	3665.2	1736.0	1397.9	943.9	665.5	567.7	487.4	366.5	320.2;
            18918.3     10082.1     5963.8      1795.5	1318.3	1000.2	779.6	616.8	5336.6	2525.8	2031.1	1367.1	960.3	817.4	700.5	525.0	457.8;
            55989.1     29308.7     17035.1     4880.6	3524.4	2625.5	2013.5	1581.0	1268.7	6788.0	5446.6	3645.3	2545.5	2156.6	1839.9	1367.0	1188.2;
            77862.3     40556.5     23456.0     6629.4	4767.5	3536.7	2696.1	2108.0	1685.2	943.9	7341.2	4910.6	3424.5	2898.7	2470.8	1831.5	1589.6;
            144247.9	74446.7     42670.0     11774.2	8404.3	6187.9	4687.3	3629.6	2878.5	1585.8	1338.5	8551.2	5954.1	5032.3	4284.0	3165.4	2744.1;
            254222.2	130091.7	73970.7     20032.7	14182.5	10373.6	7813.0	6018.1	4739.1	2564.3	2151.3	1566.2	9874.3	8339.4	7092.6	5232.2	4531.2;
            332597.1	169405.0	95971.1     25768.1	18187.6	13257.3	9958.2	7651.7	6010.8	3224.7	2698.5	1953.6	12414.2	10579.9	8997.6	6633.1	5742.7;
            430755.4	218488.2	123347.7	32846.1	23128.1	16800.7	12587.6	9649.4	7562.5	4025.9	3360.9	2420.8	1815.3	13219.9	11308.0	8334.1	7213.4;
            703278.4	354216.2	198688.8	52088.6	36513.2	26392.7	19670.2	15013.0	11714.9	6154.6	5113.8	3652.7	2711.3	2368.2	2085.9	12841.5	11113.1;
            886239.0	445114.9	248905.6	64776.1	45311.5	32684.8	24305.4	18512.7	14416.3	7531.5	6243.8	4442.4	3284.8	2862.0	2511.1	15706.8	13625.8];

    % We don't have numbers for elements not in our element list.  So we
    % fill those with rediculously long attenuation lengths.  1 million =
    % essentially not attenuated, so it won't affect the calculation.
    k = 100000;
    A = [   ones(5, NumRecognizedElements)*k;	% H-B
            A(1:3, 1:NumRecognizedElements);    % CNO
            ones(2, NumRecognizedElements)*k;   % F, Ne
            A(4:9, 1:NumRecognizedElements);    % Na-S
            ones(2, NumRecognizedElements)*k;   % Cl, Ar
            A(10:11, 1:NumRecognizedElements);  % K, Ca
            ones(1, NumRecognizedElements)*k;   % Sc
            A(12, 1:NumRecognizedElements);     % Ti
            ones(1, NumRecognizedElements)*k;   % V
            A(13:15, 1:NumRecognizedElements);  % Cr-Fe
            ones(1, NumRecognizedElements)*k;   % Co
            A(16:17, 1:NumRecognizedElements);  % Ni, Cu
            ones(1, NumRecognizedElements)*k];  % Zn
    A = [   ones(30, 5)*k, A(1:30, 1:3), ones(30, 2)*k, A(1:30, 4:9), ones(30, 2)*k, A(1:30, 10:11), ones(30, 1)*k, A(1:30, 12), ones(30, 1)*k, A(1:30, 13:15), ones(30, 1)*k, A(1:30, 16:17), ones(30, 1)*k];            
            
    takeoff = 20;
    tvec = (SpecimenThickness/10:SpecimenThickness/10:SpecimenThickness)/sind(takeoff);
    if(SpecimenThickness == 0)
        tvec = 0;
    end
    ElementsCorrected = ElementsSimulated;
    for i=1:30
        nmu = 1./A(i,:).*ElementsSimulated'/100;
        
        for j = 1:length(tvec)
        	Isum(j, :) = exp(sum(nmu*tvec(j)*6.9875e-3*100));  % Here we assume 100 atoms/nm which is fairly typical.
            % Here the constant 6.9875e-3 comes from mu=2*r0*lambda*f'' =
            % 2*r0*hc * f''/E and f''/E = 1/A.  See the CXRO intro page.  This
            % constant was computed for units of nm so we could assume 100
            % atoms/nm and then get a thickness in nm.
        end
        Isum = sum(Isum, 1)/size(Isum,1);
        ElementsCorrected(i) = ElementsSimulated(i)*Isum;

        
%         ElementsCorrected(i) = ElementsSimulated(i)*exp(sum(nmu*SpecimenThickness*6.9875e-3*100));  % Here we assume 100 atoms/nm which is fairly typical.
%         % Here the constant 6.9875e-3 comes from mu=2*r0*lambda*f'' =
%         % 2*r0*hc * f''/E and f''/E = 1/A.  See the CXRO intro page.  This
%         % constant was computed for units of nm so we could assume 100
%         % atoms/nm and then get a thickness in nm.


    end
    ElementsSimulated = ElementsCorrected;

% --- Executes on button press in btnKFactor.
function btnKFactor_Callback(hObject, eventdata, handles)
    global Elements;
    global C N O Na Mg Al Si P S Cl Ar K Ca Ti Cr Mn Fe Ni Zn

    % First populate the elements array from the experimental values entered in
    % by the user.
    Elements(:) = 0;
    Elements(C) = str2num(get(handles.editC, 'string'));
    Elements(N) = str2num(get(handles.editN, 'string'));
    Elements(O) = str2num(get(handles.editO, 'string'));
    Elements(Na) = str2num(get(handles.editNa, 'string'));
    Elements(Mg) = str2num(get(handles.editMg, 'string'));
    Elements(Al) = str2num(get(handles.editAl, 'string'));
    Elements(Si) = str2num(get(handles.editSi, 'string'));
    Elements(P) = str2num(get(handles.editP, 'string'));
    Elements(S) = str2num(get(handles.editS, 'string'));
    Elements(K) = str2num(get(handles.editK, 'string'));
    Elements(Ca) = str2num(get(handles.editCa, 'string'));
    Elements(Ti) = str2num(get(handles.editTi, 'string'));
    Elements(Cr) = str2num(get(handles.editCr, 'string'));
    Elements(Mn) = str2num(get(handles.editMn, 'string'));
    Elements(Fe) = str2num(get(handles.editFe, 'string'));
    Elements(Ni) = str2num(get(handles.editNi, 'string'));
    

%     %CM200 STANDARD BASED K FACTORS   
%     %Make a k-factor vector
%     k = zeros(30,1);    
%     % Start with the standardless k-factors.
%     % A 4th order polynomial fit to the standardless k-factors we know gets
%     % a value for all the elements.
%     for Z = 1:30
%         k(Z) = (1.3781e-05)*Z^4 + (-0.0012841)*Z^3 + (0.046689)*Z^2 + (-0.74694)*Z + 5.3103;
%     end
%     % Now we refine it with the standardless values for the elements we specifically know.
%     k(C) = 2.208;
%     k(O) = 1.810;
%     k(Na) = 1.237;
%     k(Mg) = 1.085;
%     k(Al) = 1.044;
%     k(Si) = 1;
%     k(S) = 0.940;
%     k(Cl) = 0.964;
%     k(Ar) = 1.023;
%     k(K) = 0.952;
%     k(Ca) = 0.935;
%     k(Ti) = 1.050;
%     k(Cr) = 1.100;
%     k(Mn) = 1.153;
%     k(Fe) = 1.170;
%     k(Ni) = 1.245;  
%     k(Zn) = 1.434;
% %     % And overwrite those that we have standardized k-factors for
% %     % Fo82 (6 spectra version)
% %     k(O) = 1.8993;
% %     k(Mg) = 1.1128;
% %     k(Si) = 1;
% %     k(Fe) = 1.5716;
%     % And overwrite those that we have standardized k-factors for.
%     % See CM200 k-factors.key
%     % These come from Fo82, miyakejima anorthite, and stillwater chromite.
%     kstd = zeros(30,1);
%     kstd(O) = 1.6299;
%     kstd(Mg) = 1.1069;
%     kstd(Al) = 1.0718;
%     kstd(Si) = 1;
%     kstd(Ca) = 1.1772;
%     kstd(Cr) = 1.3872;
%     kstd(Fe) = 1.4975;
%     k = InferFullkfactorList(kstd, [O, Mg, Si Fe], Si, 0);

%     % TITAN STANDARDLESS K-FACTORS
%     %Make a k-factor vector
%     k = zeros(30,1);    
%     % Start with the standardless k-factors.
%     % A 4th order polynomial fit to the standardless k-factors we know gets
%     % a value for all the elements.
%     for Z = 1:30
%         k(Z) = (5.9852e-05)*Z^4 + (-0.0049411)*Z^3 + (0.14847)*Z^2 + (-1.8512)*Z + 8.9360;
%     end
%     % Now we refine it with specific elements from the cliff-lorimer table in the Bruker software.
%     k(C) = 2.500;
%     k(O) = 1.130;
%     k(Na) = 0.849;
%     k(Mg) = 0.919;
%     k(Al) = 0.990;
%     k(Si) = 1;
%     k(S) = 1.062;
%     k(Cl) = 1.127;
%     k(Ar) = 1.237;
%     k(K) = 1.177;
%     k(Ca) = 1.274;
%     k(Ti) = 1.353;
%     k(Cr) = 1.450;
%     k(Mn) = 1.555;
%     k(Fe) = 1.618;
%     k(Ni) = 1.817;  
%     k(Zn) = 2.209;
% 
%     kStandardless = k;
    
    
%     kstd = zeros(30,1);
%     kstd(O) = 1.81;
%     kstd(Mg) = 1.1512;
%     kstd(Al) = 1.0349;
%     kstd(Si) = 1;
%     kstd(Ca) = 1.0915;
%     kstd(Cr) = 1.2035;
%     kstd(Fe) = 1.3914;
%     k = InferFullkfactorList(kstd, [O, Mg, Si Fe], Si, 0);

%     %Extrapolated.
%     k(Cr) = k(Fe)*kStandardless(Cr)/kStandardless(Fe);
%     k(Mn) = k(Fe)*kStandardless(Mn)/kStandardless(Fe);
%     k(Ca) = k(Fe)*kStandardless(Ca)/kStandardless(Fe);
%     k(K) = k(Fe)*kStandardless(K)/kStandardless(Fe);
%     k(Ti) = k(Fe)*kStandardless(Ti)/kStandardless(Fe);
%     k(Al) = k(Mg)*kStandardless(Al)/kStandardless(Mg);
    
    % Get our k factor list
    Instrument = get(handles.editInstrument, 'string')
    k = InferFullkfactorList(Instrument, Si, 0)

    % Now we convert the k-factors to At% k-factors.
    k = WtToAt(k);
    % And renormlize to Si
    k = k/k(Si);

    % Now apply these k-factors to the Elements
    Elements = Elements.*k;
    
    % And populate the dialog with the new values.
    set(handles.editC, 'String', num2str(Elements(C)));
    set(handles.editN, 'String', num2str(Elements(N)));
    set(handles.editO, 'String', num2str(Elements(O)));
    set(handles.editNa, 'String', num2str(Elements(Na)));
    set(handles.editMg, 'String', num2str(Elements(Mg)));
    set(handles.editAl, 'String', num2str(Elements(Al)));
    set(handles.editSi, 'String', num2str(Elements(Si)));
    set(handles.editP, 'String', num2str(Elements(P)));
    set(handles.editS, 'String', num2str(Elements(S)));
    set(handles.editK, 'String', num2str(Elements(K)));
    set(handles.editCa, 'String', num2str(Elements(Ca)));
    set(handles.editTi, 'String', num2str(Elements(Ti)));
    set(handles.editCr, 'String', num2str(Elements(Cr)));
    set(handles.editMn, 'String', num2str(Elements(Mn)));
    set(handles.editFe, 'String', num2str(Elements(Fe)));
    set(handles.editNi, 'String', num2str(Elements(Ni)));
    

function k = InferFullkfactorList(Instrument, Ratio, OxygenByStoichiometry)
    global C N O Na Mg Al Si P S Cl Ar K Ca Ti Cr Mn Fe Ni Zn

    % First we'll make a standardless k-factor curve.
    
    %Make a k-factor vector
    k = zeros(30,1);
    switch upper(Instrument)
        case 'CM200'
            % CM200 STANDARDLESS CURVE
            % A 4th order polynomial fit to the standardless k-factors we know gets
            % a value for all the elements.
            for Z = 1:30
                k(Z) = (1.3781e-05)*Z^4 + (-0.0012841)*Z^3 + (0.046689)*Z^2 + (-0.74694)*Z + 5.3103;
            end
            % Now we refine it with the standardless values for the elements we specifically know.
            k(C) = 2.208;
            k(O) = 1.810;
            k(Na) = 1.237;
            k(Mg) = 1.085;
            k(Al) = 1.044;
            k(Si) = 1;
            k(S) = 0.940;
            k(Cl) = 0.964;
            k(Ar) = 1.023;
            k(K) = 0.952;
            k(Ca) = 0.935;
            k(Ti) = 1.050;
            k(Cr) = 1.100;
            k(Mn) = 1.153;
            k(Fe) = 1.170;
            k(Ni) = 1.245;  
            k(Zn) = 1.434;    
            % CM200 STANDARD BASED ELEMENTS
            % See CM200 k-factors.key
            % These come from Fo82, miyakejima anorthite, and stillwater chromite.
            kstd = zeros(30,1);
            kstd(O) = 1.6299;
            kstd(Mg) = 1.1069;
            %kstd(Al) = 1.0718;
            kstd(Si) = 1;
            %kstd(Ca) = 1.1772;
            %kstd(Cr) = 1.3872;
            kstd(Fe) = 1.4975;
            ElementList = [O, Mg, Si, Fe]
        case 'TITAN'
            % TITAN STANDARDLESS CURVE
            % A 4th order polynomial fit to the standardless k-factors we know gets
            % a value for all the elements.
            for Z = 1:30
                k(Z) = (5.9852e-05)*Z^4 + (-0.0049411)*Z^3 + (0.14847)*Z^2 + (-1.8512)*Z + 8.9360;
            end
            % Now we refine it with specific elements from the cliff-lorimer table in the Bruker software.
            k(C) = 2.500;
            k(O) = 1.130;
            k(Na) = 0.849;
            k(Mg) = 0.919;
            k(Al) = 0.990;
            k(Si) = 1;
            k(S) = 1.062;
            k(Cl) = 1.127;
            k(Ar) = 1.237;
            k(K) = 1.177;
            k(Ca) = 1.274;
            k(Ti) = 1.353;
            k(Cr) = 1.450;
            k(Mn) = 1.555;
            k(Fe) = 1.618;
            k(Ni) = 1.817;  
            k(Zn) = 2.209;
            % TITAN STANDARD BASED ELEMENTS
            % See CM200 k-factors.key
            % These come from Fo82, miyakejima anorthite, and stillwater chromite.
            kstd = zeros(30,1);
            ElementList = []
        otherwise
            print 'Valid instruments are CM200 or Titan, defaulting to CM200'
            k = InferFullkfactorList('CM200', Ratio, OxygenByStoichiometry)
            return
    end
            
    % Renormalize the curve to whatever our ratio element is.  (The default
    % was Si.)
    k = k/k(Ratio);
    
    % An empty ElementList means we are totally standardless, and thus we
    % are done.
    if length(ElementList)==0
        return
    end
    
    % And that gives us our standardless curve.
    kStandardless = k;
    
    k = zeros(30,1); 
    
    % ElementList is the list of elements we calibrated.
    % If we are using stoichiometric oxygen, then remove it from the list.
    if(OxygenByStoichiometry==1)
        ElementList(find(ElementList==8)) = [];
    end
    ElementList(find(ElementList==Ratio)) = [];
    
    % Now we'll put in the standard based k-factors we have.
    for i=1:length(ElementList)
        k(ElementList(i)) = kstd(ElementList(i));
    end
    
    % Infer the rest by assuming they ratio to nearby calibrated elements using the
    % standardless curve.
    
    for i=1:30
        % Only process elements that we haven't measured.
        if(k(i) ~= 0)
            continue;
        end
        
        % Find the nearest calibrated element
        NearestElement = ElementList(max(find(abs(i - ElementList) == min(abs(i-ElementList)))));
        
        k(i) = k(NearestElement)*kStandardless(i)/kStandardless(NearestElement);
    end
    

    

function editMn_Callback(hObject, eventdata, handles)
% hObject    handle to editMn (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of editMn as text
%        str2double(get(hObject,'String')) returns contents of editMn as a double


% --- Executes during object creation, after setting all properties.
function editMn_CreateFcn(hObject, eventdata, handles)
% hObject    handle to editMn (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end

function Elements = AtToWt(Elements)
    % So we can get between Wt% and At%
    ElementWeights = [  1.0079
                        4.00
                        6.941
                        9.01218
                        10.81
                        12.011
                        14.0067
                        15.9994
                        19.00
                        20.17
                        22.98977
                        24.305
                        26.98154
                        28.0855
                        30.97376
                        32.06
                        35.453
                        39.95
                        39.0983
                        40.08
                        44.9559
                        47.88
                        50.9415
                        51.996
                        54.938
                        55.847
                        58.9332
                        58.69
                        63.546
                        65.38];
    

    Elements = Elements.*ElementWeights;
    % Renormalize
    Elements = Elements/sum(Elements)*100;

function Elements = WtToAt(Elements)
    % So we can get between Wt% and At%
    ElementWeights = [  1.0079
                        4.00
                        6.941
                        9.01218
                        10.81
                        12.011
                        14.0067
                        15.9994
                        19.00
                        20.17
                        22.98977
                        24.305
                        26.98154
                        28.0855
                        30.97376
                        32.06
                        35.453
                        39.95
                        39.0983
                        40.08
                        44.9559
                        47.88
                        50.9415
                        51.996
                        54.938
                        55.847
                        58.9332
                        58.69
                        63.546
                        65.38];
    

    Elements = Elements./ElementWeights;
    % Renormalize
    Elements = Elements/sum(Elements)*100;


% --- Executes on button press in btnSetM1.
function btnSetM1_Callback(hObject, eventdata, handles)
% hObject    handle to btnSetM1 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

    global M1;
    global C N O Na Mg Al Si P S Cl Ar K Ca Ti Cr Mn Fe Ni Zn

    % First populate the elements array from the experimental values entered in
    % by the user.
    M1(:) = 0;
    M1(C) = str2num(get(handles.editC, 'string'));
    M1(N) = str2num(get(handles.editN, 'string'));
    M1(O) = str2num(get(handles.editO, 'string'));
    M1(Na) = str2num(get(handles.editNa, 'string'));
    M1(Mg) = str2num(get(handles.editMg, 'string'));
    M1(Al) = str2num(get(handles.editAl, 'string'));
    M1(Si) = str2num(get(handles.editSi, 'string'));
    M1(P) = str2num(get(handles.editP, 'string'));
    M1(S) = str2num(get(handles.editS, 'string'));
    M1(K) = str2num(get(handles.editK, 'string'));
    M1(Ca) = str2num(get(handles.editCa, 'string'));
    M1(Ti) = str2num(get(handles.editTi, 'string'));
    M1(Cr) = str2num(get(handles.editCr, 'string'));
    M1(Mn) = str2num(get(handles.editMn, 'string'));
    M1(Fe) = str2num(get(handles.editFe, 'string'));
    M1(Ni) = str2num(get(handles.editNi, 'string'));


% --- Executes on button press in btnReadM1.
function btnReadM1_Callback(hObject, eventdata, handles)
% hObject    handle to btnReadM1 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

    global M1;
    global C N O Na Mg Al Si P S Cl Ar K Ca Ti Cr Mn Fe Ni Zn
    % And populate the dialog with the new values.
    set(handles.editC, 'String', num2str(M1(C)));
    set(handles.editN, 'String', num2str(M1(N)));
    set(handles.editO, 'String', num2str(M1(O)));
    set(handles.editNa, 'String', num2str(M1(Na)));
    set(handles.editMg, 'String', num2str(M1(Mg)));
    set(handles.editAl, 'String', num2str(M1(Al)));
    set(handles.editSi, 'String', num2str(M1(Si)));
    set(handles.editP, 'String', num2str(M1(P)));
    set(handles.editS, 'String', num2str(M1(S)));
    set(handles.editK, 'String', num2str(M1(K)));
    set(handles.editCa, 'String', num2str(M1(Ca)));
    set(handles.editTi, 'String', num2str(M1(Ti)));
    set(handles.editCr, 'String', num2str(M1(Cr)));
    set(handles.editMn, 'String', num2str(M1(Mn)));
    set(handles.editFe, 'String', num2str(M1(Fe)));
    set(handles.editNi, 'String', num2str(M1(Ni)));


% --- Executes on button press in chkStoich.
function chkStoich_Callback(hObject, eventdata, handles)
% hObject    handle to chkStoich (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hint: get(hObject,'Value') returns toggle state of chkStoich



function editThickness_Callback(hObject, eventdata, handles)
% hObject    handle to editThickness (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of editThickness as text
%        str2double(get(hObject,'String')) returns contents of editThickness as a double


% --- Executes during object creation, after setting all properties.
function editThickness_CreateFcn(hObject, eventdata, handles)
% hObject    handle to editThickness (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end


% --- If Enable == 'on', executes on mouse press in 5 pixel border.
% --- Otherwise, executes on mouse press in 5 pixel border or over btnCompute.
function btnCompute_ButtonDownFcn(hObject, eventdata, handles)
% hObject    handle to btnCompute (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)



function editInstrument_Callback(hObject, eventdata, handles)
% hObject    handle to editInstrument (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of editInstrument as text
%        str2double(get(hObject,'String')) returns contents of editInstrument as a double


% --- Executes during object creation, after setting all properties.
function editInstrument_CreateFcn(hObject, eventdata, handles)
% hObject    handle to editInstrument (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end
