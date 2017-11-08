function slope_satvp_temp = ds_dt(T);
%*****************************************************************%
% THIS MATLAB FUNCTION CALCULATES THE SLOPE OF THE SATURATION     %
% VAPOUR PRESSURE VS. TEMPERATURE CURVE (BUCK, 1981 ?)(kPa C^-1)  %
%                                                                 %
%        slope_satvp_temp = ds_dt(T)                              %
%                                                                 %
%        T = air temperature in Celcius                           %
%                                                                 %
%*****************************************************************%        

slope_satvp_temp = 0.61121*((17.368*238.88)./(T+238.88).^2).*exp((T.*17.368)./(T+238.88));
