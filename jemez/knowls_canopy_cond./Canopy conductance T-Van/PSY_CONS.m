function psychrometer_constant = psy_cons(T,e,P);
%*****************************************************************%
% THIS MATLAB FUNCTION CALCULATES THE PSYCHROMETRIC CONSTANT      %
% (kPa C^-1)                                                      %
%                                                                 %
%        psychrometer_constant = psy_cons(T,e,P)                  %
%                                                                 %
%        T = air temperature (dry bulb) in deg C                  %
%        e = water vapour pressure in kPa                         %
%        P = barometric pressure in kPa                           %
%*****************************************************************%        

epsilon = 0.622;
specific_heat_dry_air = 1003;
specific_heat_water_vapour = 1810;
mixing_ratio = e.*epsilon./(P-e);
specific_heat = (specific_heat_dry_air + mixing_ratio.*specific_heat_water_vapour)./(1+mixing_ratio);
lamda = (2501 - 2.38.*T).*1000;
psychrometer_constant = P.*specific_heat./(epsilon.*lamda);      
