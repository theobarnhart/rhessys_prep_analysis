xmin=449655
ymin=4430855
xmax=454645
ymax=4434575

for year in {1996..2007}; do
	
	cp /Volumes/hydroData/JepsenData/jepsen_usgspostdoc/D_drive/2010_sem1/swerecon_runs/GLV/${year}/swe.mdl /Volumes/data/jepsen_GLV/swe_${year}.mdl

cp /Volumes/hydroData/JepsenData/jepsen_usgspostdoc/D_drive/2010_sem1/swerecon_runs/GLV/${year}/swe.mdl.hdr /Volumes/data/jepsen_GLV/swe_${year}.mdl.hdr
	
	infl=/Volumes/data/jepsen_GLV/swe_${year}.mdl
	outlf=./data/jepsen_swe_como/swe_${year}_como.tiff
	
	gdalwarp -tr 30 30 -te $xmin $ymin $xmax $ymax $infl $outlf
done
