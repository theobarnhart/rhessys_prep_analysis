%% Generate figure and statistics for 2-D rotated, wpl corrected fluxes over time 
% site - TVAN 
% program author - John Knowles (adapted from P Blanken)
% date - November 10, 2008
% last modified - March 18, 2011

%% Load Data
%flux = dlmread('2009_West.csv');
flux = dlmread('complete_threeyears_SEB.csv');
%flux = dlmread('complete_EC_dataset.csv');

%% Define Constants
Mw = 18.02; 
R = 8.3143e-3; % universal gas constant [kPa m^3/(K mol)]
RD = R/29; % gas constant dry air [kPa m^3/(K g)]
RV = R/18; % gas constant water vapor [kPa m^3/(K g)]
mu = 29/18; % mass dry air/water vapor

% Disable case sensitive inexact match warning
'off';'MATLAB:dispatcher:InexactMatch';

%% ID variables of interest

time = flux(:,1); % calendar DOY (GMT)
time = time-(7/24); % MST
DOY = flux(:,2); % cumulative DOY from January 1, 2007 (GMT)
DOY = DOY-(7/24); % MST

Fc = flux(:,5); % WPL corr, but not rotated - see below mg m^2 s^-1;
Fc = CLE_DATA(Fc,2,0.5); Fc = CLE_DATA(Fc,3,-0.5);

LE = flux(:,6); % WPL corr W m^-2
LE = CLE_DATA(LE,2,250); LE = CLE_DATA(LE,3,-100);

H = flux(:,7); % corr W m^-2
H = CLE_DATA(H,3,-200);

Ta = flux(:,35); % HMP air temp deg C 

Ts = flux(:,10); % sonic air temp deg C

P = flux(:,34); % kPa

U = flux(:,41); U = CLE_DATA(U,2,50); % wind speed (m/s)

u_star  = flux(:,9); % m s^-1

Rn = flux(:,64);% Wm-2
%Rn = Rn./69.4; % Remove incorrect sensitivity (14.4 Wm-2) written into loggernet code (If using E tower data only!!)
%Rn = Rn.*66.7; % Replace with correct sensitivity multiplier

shf1 = flux(:,65)*-1; % W m^-2
shf1 = CLE_DATA(shf1,3,-75);

shf2 = flux(:,66)*-1; % W m^-2
shf2 = CLE_DATA(shf2,3,-75);

G = (shf1+shf2)/2;

A = Rn-G;

rho_v = flux(:,36); % vapor density from HMP g^m-3
rho_v = CLE_DATA(rho_v,2,20); 
rho_c = flux(:,15); 
rho_c = CLE_DATA(rho_c,2,600); rho_c = CLE_DATA(rho_c,3,450); % CO2 density mg m^-3

ea = rho_v.*R.*(Ta+273.15)./Mw./1000;

es=SAT_VP(Ta);

ea_2=rho_v.*R.*1000.*(Ta+273.15)./Mw./1000; %kPa
vpd=es-ea_2;

RH = ea_2./SAT_VP(Ta);

u1 = flux(:,25); % mean u
v1 = flux(:,29); % mean v
w1 = flux(:,32); % mean w

u_T = flux(:,12); u_T = CLE_DATA(u_T ,2,1); u_T = CLE_DATA(u_T,3,-2); 
v_T = flux(:,13);
w_T = flux(:,14); w_T = CLE_DATA(w_T,3,-1);

u_c = flux(:,17); u_c = CLE_DATA(u_c,2,2); u_c = CLE_DATA(u_c,3,-2);
v_c = flux(:,18);
w_c = flux(:,19); w_c = CLE_DATA(w_c,2,0.5); w_c = CLE_DATA(w_c,3,-1);

u_q = flux(:,22); u_q = CLE_DATA(u_q,2,0.4); u_q = CLE_DATA(u_q,3,-0.4); 
v_q = flux(:,23);
w_q = flux(:,24); w_q = CLE_DATA(w_q,2,0.1); w_q = CLE_DATA(w_q,3,-0.1);

%% Begin Data Processing 
% 2-d coordinate rotation (note no WPL)
% Baldocchi et al, Ecology, 69:1331-1340 (pg 1335)

ubar2 = u1.^2; 
vbar2 = v1.^2; 
wbar2 = w1.^2;

cT = sqrt(ubar2 + vbar2)./sqrt(ubar2 + vbar2 + wbar2);
sT = w1./sqrt(ubar2 + vbar2 + wbar2);
cS = u1./sqrt(ubar2 + vbar2);
sS = v1./sqrt(ubar2 + vbar2);

w_q_rot = w_q.*cT - u_q.*sT.*cS - v_q.*sT.*sS;
w_T_rot = w_T.*cT - u_T.*sT.*cS - v_T.*sT.*sS;
w_c_rot = w_c.*cT - u_c.*sT.*cS - v_c.*sT.*sS;

% WPL - use the rotated covariances (right above) to produce rotated, wpl corrected fluxes
% replace w_T_E; w_q_E; w_c_E; with w_T_rot_E; w_q_rot_E; w_c_rot_E

h2o_hmp_mean = rho_v./((Ta + 273.15).*RV);
rho_d_mean = (P - ea)./((Ta + 273.15).*RD); %vapor density g m^-3
rho_a_mean = (rho_d_mean + h2o_hmp_mean)./1000;
sigma = h2o_hmp_mean./rho_d_mean;

% Webb terms for LE (eqn 25) using the rotated covariances

h2o_wpl_LE = mu.*sigma.*lambda(Ta)./1000.*w_q_rot;
h2o_wpl_H = (1+(mu.*sigma)).*h2o_hmp_mean./(Ta+273.15).*lambda(Ta)./1000.*w_T_rot;
LE_rot_wpl = lambda(Ta)./1000.*w_q_rot + h2o_wpl_LE + h2o_wpl_H;
LE_rot_wpl = CLE_DATA(LE_rot_wpl,3,-200); LE_rot_wpl = CLE_DATA(LE_rot_wpl,2,300);

% Webb terms for H using rotated w_T and LE_rot_wpl (corrected LE)

H_rot_wpl = ((rho_a_mean.*spe_heat(ea,P).*w_T_rot)-(rho_a_mean.*spe_heat(ea,P).*0.51.*RD.*(Ta+273.15).*LE_rot_wpl)./(P.*lambda(Ta))).*((Ta+273.15)./(Ts +273.15));
H_rot_wpl = CLE_DATA(H_rot_wpl,3,-200); H_rot_wpl = CLE_DATA(H_rot_wpl,2,400);

% Webb terms for CO2 (eqn 24)

co2_wpl_LE = mu.* rho_c./rho_d_mean.*w_q_rot;
co2_wpl_H  = (1+(mu.*sigma)).*rho_c./(Ta+273.15).*H_rot_wpl./(rho_a_mean.*spe_heat(ea,P));
Fc_rot_wpl = w_c_rot + co2_wpl_LE + co2_wpl_H;

%% Bulk canopy resistance
Ra = (U./(u_star.^2))+(2.75./u_star); %aerodynamic resistance from Blanken and Black 2004
S = DS_DT(Ta); %slope of the saturation vaopr pressure v. temp curve
gamma = PSY_CONS(Ta,ea_2,P);%psychrometric constant
rho_cp = spe_heat(ea_2,P);
%S=S(per);
%gamma=gamma(per);
%rho_cp=rho_cp(per);

Rc = ((Ra.*(S.*(A))-(LE_rot_wpl.*(S+gamma)))+(rho_cp.*vpd))./(gamma.*LE_rot_wpl); %canopy resistance from Blanken 2002 ecyclopedia of atm. sciences article
Rc = CLE_DATA(Rc,2,1000); Rc=CLE_DATA(Rc,3,-1000);