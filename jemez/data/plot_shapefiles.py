def shapemap(valkey,cmapvalkey,valname,title,cmap,cmapname,outfl,outflcolorbar,savefig):
    shp = '/Users/barnhatb/Dropbox/virtual_share_win7/WSC_basins/HUC8_merged'
    norm = mpl.colors.Normalize(vmin=hucdat[cmapvalkey].min(),vmax=hucdat[cmapvalkey].max())
    cm = mpl.cm.ScalarMappable(norm=norm,cmap=cmap)
    fig = plt.figure(figsize=(8,12))
    ax = fig.add_subplot(111)

    m = basemap.Basemap(llcrnrlon=-107.5,llcrnrlat=37.75,urcrnrlon=-104.5,urcrnrlat=42.25, epsg=4326) # make a Basemap projection with
    m.arcgisimage(service='World_Shaded_Relief',xpixels=1000, verbose = False)

    patches = []
    huc8 = []
    m.readshapefile(shp,'HUC8_merged', drawbounds=False)

    for info,shape in zip(m.HUC8_merged_info,m.HUC8_merged):
        patches.append(Polygon(np.array(shape),True))
        huc = int(info['HUC_8'])
        huc8.append(int(info['HUC_8']))

    for huc,patch in zip(huc8,patches):
        patches2 = []
        val = hucdat.loc[hucdat.huc8==huc,valkey]
        patches2.append(patch)
        ax.add_collection(PatchCollection(patches2, facecolor=cm.to_rgba(val), edgecolor='none',alpha=0.6))

    m.readshapefile(shp,'HUC8_merged', drawbounds=True) # draw the shapefile over the patches
    m.readshapefile('/Users/barnhatb/Dropbox/virtual_share_win7/continental_divide_Project','continental_divide_Project',linewidth=4,color='w')
    m.readshapefile('/Users/barnhatb/Dropbox/virtual_share_win7/Transbasin','Transbasin')

    for pt in m.Transbasin:
        m.plot(pt[0],pt[1],'.g', markersize=15)

    m.drawmeridians(np.arange(-110,-100,2),linewidth=2, color='k',labels=[1,1,0,1],fontsize=18)
    m.drawparallels(np.arange(20,60,2), linewidth=2, color='k', labels=[1,1,0,1], fontsize=18)
    plt.title(title,fontsize=22)

    if savefig:
        plt.savefig(outfl,dpi=300,bbox_inches='tight')

    fig = plt.figure(figsize=(8,0.5))
    ax = fig.add_subplot(111)
    cb = mpl.colorbar.ColorbarBase(ax,cmap=cmapname,norm=norm, orientation='horizontal')
    cb.set_label(valname,fontsize=18)
    if savefig:
        plt.savefig(outflcolorbar,dpi=300,bbox_inches='tight')
		
		
        
        #plt.savefig('./figures/wsc_pi16_wflux_rr_p.png', dpi = 300, bbox_inches='tight')
#################### new thing

shps = glob.glob('/Users/barnhatb/Dropbox/virtual_share_win7/WSC_basins/HUC8/*.shp')
        
        plt.figure(figsize=(7,14))
        pcol = m.pcolormesh(X,Y,RR_p,vmin=0,vmax=0.1,alpha =1,rasterized=True,linewidth=0)
        pcol.set_edgecolor('face')
        cb = m.colorbar()
        m.drawstates(color='0.5', linewidth=2)
        for shp in shps:
            m.readshapefile(shp[0:-4],shp.split('/')[-1].split('.')[0], color='w', linewidth=3)

        cb.set_label('P-value',fontsize=24)
        cb.set_alpha(1)
        cb.ax.tick_params(labelsize=15) 
        cb.draw_all()
        m.drawmeridians(np.arange(-110,-100,2),linewidth=4, color='w',labels=[1,1,1,1],fontsize=18)
        m.drawparallels(np.arange(20,60,2), linewidth=4, color='w', labels=[1,0,0,0], fontsize=18)
