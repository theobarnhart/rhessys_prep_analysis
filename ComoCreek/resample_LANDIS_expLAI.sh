files=`ls -1 ./data/RHESSys_scenarios/LANDIS_LAI_*.tiff` # grab all the LAI files

xmin=449655
ymin=4430855
xmax=454645
ymax=4434575

for fl in $files; do
filename="${fl%.*}"
outfl=${filename}_60m.tiff

gdalwarp -overwrite -te $xmin $ymin $xmax $ymax -tr 60 60 -r average $fl $outfl
done
