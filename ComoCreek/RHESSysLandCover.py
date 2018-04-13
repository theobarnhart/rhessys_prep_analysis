#### Package to help with processing and analysis of the RHESSys Land Cover project
# Theodore Barnhart
# theodore.barnhart@colorado.edu

# imports
import pandas as pd
import numpy as np
import datetime
import rhessys.utilities as rut

### Processing Functions
def parse_date(df):
    """Returns a YYYY-MM-DD string from a DataFrame with year, month, and day columns.
    """
    return '%i-%i-%i'%(df.year,df.month,df.day)
    
def readfile(fl):
    """Returns a DataFrame cropped to the hard coded start and end dates.
    """
    strt = '1993-10-1'
    nd = '2013-09-30'
    
    dat = pd.read_table(fl,sep=' ')
    dat['ET'] = dat.trans+dat.evap
    dat['datetime'] = dat.apply(parse_date,axis=1)
    dat.index = pd.DatetimeIndex(dat.datetime)
    dat['wateryear'] = dat.index.map(rut.wateryear)
    
    return dat[strt:nd]
    
class X:
    pass
    
class process:
    """Returns an object containing processed RHESSys output."""
    def __init__(self, fl):
        #fl = df['file']
        tail = fl.split('/')[-1]
        self.track = '%s_%s'%(tail.split('_')[0],tail.split('_')[1])
        self.scenario = int(tail.split('_')[2]) # pull scenario
        self.year = int(tail.split('_')[3]) # pull year
        self.decade = int(tail.split('_')[4]) # pull decade
    
        # pull the name of the simulation
        name1 = tail.split('_')[-5]
        name2 = tail.split('_')[-4]
        name3 = tail.split('_')[-3]
        self.name = '%s_%s_%s'%(name1,name2,name3)
    
        self.idx = int(tail.split('_')[-2]) # pull idx
        
        dat = readfile(fl)
        self.dat = dat
        
        # summarize by water year mean
        WY = dat.groupby(by='wateryear').mean()
        WY['R_P'] = WY.adj_streamflow/WY.precip
        
        # compute some dataset whole values
        summary = {'R_P':dat.adj_streamflow.sum()/dat.precip.sum(),
                'LAI':dat.lai.mean(),
                'ET':dat.ET.mean(),
                'leakage':dat.leakage.mean(),
                'R_Pmin': WY.R_P.min(),
                'R_Pmax': WY.R_P.max(),
                'P':WY.precip.mean(),
                'Q':WY.adj_streamflow.mean()
                'meanPeakSWE':dat.groupby(by='wateryear').max().snowpack.mean()}
        self.summary = summary
    
        # summarize by water year sum
        dat3 = dat.groupby(by='wateryear').sum()

        annualQ = dat3.adj_streamflow.as_matrix() # annual total Q
        annualP = dat3.precip.as_matrix() # annual total P
    
        #return [track,scenario,year,decade,name,idx,R_P,LAI,R_P_min,R_P_max,Q,L,P,SWE,ET,leakage,sfvals,etvals,
        #        transvals,subvals,snowfallvals,precipvals,evapvals,leakagevals,rzs,petvals,swe,snowmelt,annualQ,annualP]