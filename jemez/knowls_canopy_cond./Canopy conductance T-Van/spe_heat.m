function specific_heat = spe_heat(e,P);
%*****************************************************************%
% THIS MATLAB FUNCTION CALCULATES THE SPECIFIC HEAT OF MOIST AIR  %
% (J KG^-1 DEG C^-1)                                              %
%                                                                 %
%        function specific_heat = spe_heat(e,P)                   %
%                                                                 %
%        e = water vapour pressure in kPa                         %
%        P = barometric pressure in kPa                           %
%*****************************************************************%        

epsilon = 0.622;
specific_heat_dry_air = 1003;
specific_heat_water_vapour = 1810;
mixing_ratio = e.*epsilon./(P-e);
specific_heat = (specific_heat_dry_air + mixing_ratio.*specific_heat_water_vapour)./(1+mixing_ratio);
      
