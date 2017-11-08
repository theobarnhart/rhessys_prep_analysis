for scen in {1,2,5}; do

files=`ls /Volumes/data/LANDIS/climate_change/PGW_less_P/BDA+FIRE_+4C_minus15%precip_$scen/output-leaf-biomass/TotalBiomass-*.img` # get all the img files

outpth=./data/LANDIS_output/climate_change/watershed/PGW_less_P/BDA+FIRE_+4C_minus15%precip_${scen}

mkdir $outpth

for fl in $files; do
	
	basename="${fl%.*}"
	
	gdal_translate -of GTiff -a_ullr 397115.155 4539545.111 505565.155 4417645.111 -a_srs 'EPSG:26913' $fl ${basename}_proj.tiff

	gdalwarp -overwrite -s_srs 'EPSG:26913' -t_srs 'EPSG:26913' -tr 50 50 -cutline ./data/como_watershed.shp -crop_to_cutline ${basename}_proj.tiff ${basename}_como.tiff

	cp ${basename}_como.tiff $outpth
	rm ${basename}_proj.tiff
	rm ${basename}_como.tiff

done

done

# xmin: 445000
# ymin: 4430000
# xmax: 456000
# ymin: 4436000

# -cutline ./data/como_watershed.shp -crop_to_cutline
