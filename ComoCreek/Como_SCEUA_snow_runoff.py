#!/Users/barnhatb/anaconda/bin/python

import spotpy
import numpy as np
import pandas as pd
import subprocess
import shutil
import os
from pymail import alert

def parse_dates(df):
    return '%s-%s-%s'%(int(df.year),int(df.month),int(df.day))

class spotpy_setup():
    # the __init__ runs just once at the begining of the optimization
    def __init__(self):
	# define the run number
	self.num = '30'
#        # define the parameters for the model

# opt 26
#        self.params = [spotpy.parameter.Uniform('gw1',0.0,0.85),
#                    spotpy.parameter.Uniform('gw2',0.,1.0),
#                    spotpy.parameter.Uniform('m',0.01,30.),
#                    spotpy.parameter.Uniform('ksat',0.001,800.),
#                    spotpy.parameter.Uniform('crd',1.,10.),
#                    spotpy.parameter.Uniform('trd',0.1,3.),
#                    spotpy.parameter.Uniform('po',0.001,800.),
#                    spotpy.parameter.Uniform('pa',0.001,1000.)]

# opt 27
#	self.params = [spotpy.parameter.Uniform('gw1',0.0,0.8),
#                    spotpy.parameter.Uniform('gw2',0.0,0.0),
#                    spotpy.parameter.Uniform('m',5.,18),
#                    spotpy.parameter.Uniform('ksat',300,700.),
#                    spotpy.parameter.Uniform('crd',5,15.),
#                    spotpy.parameter.Uniform('trd',2,4.),
#                    spotpy.parameter.Uniform('po',5,20),
#                    spotpy.parameter.Uniform('pa',650,950.)]

# opt 28
	self.params = [spotpy.parameter.Uniform('gw1',0.0,1.0),
                    spotpy.parameter.Uniform('gw2',0.0,1.0),
                    spotpy.parameter.Uniform('po',0.,40.),
		    spotpy.parameter.Uniform('snowtemp',0.,4.),
		    spotpy.parameter.Uniform('raintemp',-4.,0.),
		    spotpy.parameter.Uniform('smtc',0.00000001,0.6),
		    spotpy.parameter.Uniform('msed',-600,-0.00001)]

        self.obspath = '/RHESSys/Como/obs/como_q_obs.pcl'
        self.outpath = '/RHESSys/Como/out/opt'
        
        self.start_date = pd.datetime(2003,10,1) # simulation spinup start (RHESSys format)
        self.end_date = pd.datetime(2007,10,5) # simulation end date (RHESSys format)
        self.a_start_date = '2004-10-1' # analysis start date, pandas format
        self.a_end_date = '2007-09-30' # analysis end date, pandas format
        
        # read in the observations
        obs = pd.read_pickle(self.obspath)[self.a_start_date:self.a_end_date]
        obs.interpolate(inplace=True,limit=100,limit_direction='both') # interpolate out nans
        
	# read in the runoff dates
	runoff = pd.read_pickle('/projects/RHESSys/ComoCreek/data/como_runoff_periods.pcl')
	
	for wy in runoff.wy.unique(): # remove baseflow periods from the discharge data
		
		if wy == runoff.wy.unique()[0]: # if this is the first wateryear, remove the initial chunk of baseflow
			strt = runoff.loc[runoff.wy==wy,'strt'][0] # start of runoff period
			obs.loc[self.a_start_date:strt,'discharge'] = np.NaN
		
		elif (wy>runoff.wy.unique()[0]) & (wy<runoff.wy.unique()[-1]): # remove the baseflow period for the middle water years
			nd = runoff.loc[runoff.wy==wy,'nd'][0] # start of the baseflow period
			strt = runoff.loc[runoff.wy==wy+1,'strt'][0] # end of the baseflow period
			obs.loc[nd:strt,'discharge'] = np.NaN

		elif wy == runoff.wy.unique()[-1]: # for the last year, remove the tail baseflow period
			nd = runoff.loc[runoff.wy==wy,'nd'][0]
			obs.loc[nd:self.a_end_date,'discharge'] = np.NaN
			
	del obs['q_liter_per_day']
	del obs['Unnamed: 3']	

	obs.dropna(inplace=True) # drop NAs from the discharge column
        self.obs = obs.discharge.as_matrix() # add the cleaned obs to the self object
        self.evaldates = obs.index # add the dates to the self object

    def parameters(self):
        # generate the parameters
        return spotpy.parameter.generate(self.params)

    def simulation(self,vector):
        
        gw1 = vector[0]
        gw2 = vector[1]
        #m = vector[2]
        #ksat = vector[3]
        #crd = vector[4]
        #trd = vector[5]
        po = vector[2]
        #pa = vector[7]
	snowtemp = vector[3] 
	raintemp = vector[4]
	smtc = vector[5]
	msed = vector[6]

	m = 12
	ksat = 450
	crd = 2.0
	trd = 0.5
	pa = 800.0

        strtyear = self.start_date.year
        strtmonth = self.start_date.month
        strtday = self.start_date.day
        
        endyear = self.end_date.year
        endmonth = self.end_date.month
        endday = self.end_date.day
        
        #create the output directory
        idx = np.random.randint(1,high=100000,size=1)[0]
        outdirpath = '%s/%s'%(self.outpath,idx) # generate the path
        os.makedirs(outdirpath) # create the output directory
        
        # construct the command line command
        scrpt = 'sh /RHESSys/Como/scripts/rhessys_opt_ullr_par_grid_noSnowDist.sh'
        args = '%s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s'%(gw1,gw2,m,ksat,crd,trd,po,pa,snowtemp,raintemp,smtc,msed,strtyear,strtmonth,strtday,endyear,endmonth,endday,idx)
        cmd =  '%s %s'%(scrpt,args)
        print cmd
        subprocess.call(cmd,shell=True) # run the simulation using the rhessys script
        
        # load the output
        sim = pd.read_table('/RHESSys/Como/out/opt/%s/%s_tmp_basin.daily'%(idx,idx),sep = ' ') # load the streamflow data into the optimizer
        sim['datetime'] = sim.apply(parse_dates,axis=1) # parse dates
        sim.index = pd.DatetimeIndex(sim.datetime) # make datetime index
        sim = sim[self.a_start_date:self.a_end_date] # crop to the analysis time period to match obs
        sim = sim['streamflow'] # convert into a single series data frame
	
	for wy in runoff.wy.unique(): # remove baseflow periods from the model data

        	if wy == runoff.wy.unique()[0]: # if this is the first wateryear, remove the initial chunk of baseflow
                        strt = runoff.loc[runoff.wy==wy,'strt'][0] # start of runoff period
                        sim.loc[self.a_start_date:strt,'streamflow'] = np.NaN

                elif (wy>runoff.wy.unique()[0]) & (wy<runoff.wy.unique()[-1]): # remove the baseflow period for the middle water years
                        nd = runoff.loc[runoff.wy==wy,'nd'][0] # start of the baseflow period
                        strt = runoff.loc[runoff.wy==wy+1,'strt'][0] # end of the baseflow period
                        sim.loc[nd:strt,'streamflow'] = np.NaN

                elif wy == runoff.wy.unique()[-1]: # for the last year, remove the tail baseflow period
                        nd = runoff.loc[runoff.wy==wy,'nd'][0]
                        sim.loc[nd:self.a_end_date,'streamflow'] = np.NaN

	
        # remove the output directory
        shutil.rmtree(outdirpath)
        
	sim.dropna(inplace=True) # drop the baseflow periods from the model output
        return sim.streamflow.as_matrix() # return streamflow


    def evaluation(self,evaldates=False):
        # function to return the evaluation data
        if evaldates==True:
            return self.evaldates
        
        if evaldates==False:
            return self.obs

    def objectivefunction(self,simulation,evaluation):
        # compute the objective function
        objectivefunction = spotpy.objectivefunctions.nashsutcliff(evaluation,simulation) # we want to maximize this function
        return objectivefunction

spotpy_setup = spotpy_setup()

sampler = spotpy.algorithms.sceua(spotpy_setup, dbname='Como_SCEUA_%s'%(spotpy_setup.num), dbformat='csv', parallel='mpi')

sampler.sample(3000, ngs=9, kstop = 30, pcento=0.0000025, peps=0.0000025)

alert.send_alert('barnhatb@colorado.edu','RHESSys Como Optimization Finished','Your script has finished')
