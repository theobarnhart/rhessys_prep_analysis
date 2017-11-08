import matplotlib.pyplot as plt
import numpy as np

def biomass2LAI(x,sla,leaf_stem):
    '''
    Convert biomass to lai based on the specific leaf area.
    
    x: array of biomass values in g/m2
    sla: specific leaf area m2/kg c
    leaf_stem: ratio of leaf mass to stem mass
    '''
    x /= 1000. # g/m2 > kg/m2
    leaf = (x*leaf_stem) / (1.+leaf_stem) # compute leaf wet biomass
    lai = leaf * sla # convert leaf dry biomass to leaf area

    return lai

import gdal
import glob
from mpl_toolkits.basemap import Basemap
import matplotlib
import matplotlib.animation as manimation
from IPython.display import clear_output

shp = '/Volumes/data/como_watershed_wgs84.shp'

def coord2dd(d,m,s): return d+(m/60.)+(s/60.)

FFMpegWriter = manimation.writers['ffmpeg']
metadata = dict(title='Movie Test', artist='Matplotlib',
                comment='Movie support!')
writer = FFMpegWriter(fps=10, metadata=metadata)

m = Basemap(llcrnrlon=-105.588055,llcrnrlat=40.028710,urcrnrlon=-105.537108,
            urcrnrlat=40.057246,resolution=None,projection='merc',
            lon_0=coord2dd(105,33,45.03),lat_0=coord2dd(40,2,4.58))

sla = 9.
leaf_stem = 0.0141 

offset = 2000
cmax = 5
cmin = 0

fig = plt.figure(figsize=(15,5))

with writer.saving(fig, "./figures/lai_test2.mp4", 11, bitrate=-1, codec = "libx264"):
    for i in range(11):
        clear_output()
        year = i * 10
        
        rastpth = './data/LANDIS_output/BDA+Fire_CC_1_2_110/output-leaf-biomass/TotalBiomass-%s_como.tiff'%(year)
        
        # change the model year to the actual year
        year -= 10
        year += offset
        
        ds = gdal.Open(rastpth)
        rast = np.array(ds.GetRasterBand(1).ReadAsArray(),dtype=float)
        rast[rast==0] = np.NaN
        
        lai = biomass2LAI(rast,sla,leaf_stem)
        
        m.imshow(np.flipud(lai),cmap='Greens',interpolation='none',vmin=cmin,vmax=cmax)
        m.readshapefile(shp[0:-4],shp.split('/')[-1].split('.')[0], color='k', linewidth=2);
        plt.xlim(-500,6000)
        plt.ylim(-500,4500)
        
	if i == 0:
		plt.colorbar(label='m$^2$/m$^2$')
        
	plt.title('Como Creek Year %s'%int(year), fontsize=16)
        writer.grab_frame()
	#print i

