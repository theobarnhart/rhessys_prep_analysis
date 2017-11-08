files=`ls /Volumes/data/LANDIS/climate_change/PGW_more_P/BDA+FIRE_+4C_+15%precip_3/output-leaf-biomass/TotalBiomass-*.img` # get all the img files

outpth=./data/LANDIS_output/climate_change/PGW_more_P/BDA+FIRE_+4C_+15%precip_3

mkdir $outpth

for fl in $files; do
	
	basename="${fl%.*}"
	
	gdal_translate -of GTiff -a_ullr 397115.155 4539545.111 505565.155 4417645.111 -a_srs 'EPSG:26913' $fl ${basename}_proj.tiff

	gdalwarp -overwrite -s_srs 'EPSG:26913' -t_srs 'EPSG:26913' -tr 50 50 -te 445000 4430000 456000 4436000 ${basename}_proj.tiff ${basename}_como.tiff

	cp ${basename}_como.tiff $outpth
	rm ${basename}_proj.tiff
	rm ${basename}_como.tiff

done


# xmin: 445000
# ymin: 4430000
# xmax: 456000
# ymin: 4436000

# -cutline ./data/como_watershed.shp -crop_to_cutline
