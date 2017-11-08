#!/Users/barnhatb/anaconda/bin/python

import spotpy
import numpy as np
import pandas as pd
import subprocess
import shutil
import os
from pymail import alert
from rhessys import utilities as rut

class spotpy_setup():
    # the __init__ runs just once at the begining of the optimization
    def __init__(self):
        # define the parameters for the model
        self.params = [spotpy.parameter.Uniform('gw1',0.0001,0.5),
			spotpy.parameter.Uniform('trd',0.5,1.5),
			spotpy.parameter.Uniform('crd',1.0,5)]
#,
#		    spotpy.parameter.Uniform('alpsnowscale',0.001,0.3),
#		    spotpy.parameter.Uniform('forsnowscale',0.4,1.0),
#		    spotpy.parameter.Uniform('plapse',0.00001,0.0012)]

        #spotpy.parameter.Uniform('smtc',0.,6.),
		#            spotpy.parameter.Uniform('msed',-650.,0.),
		#            spotpy.parameter.Uniform('raintemp',-2.,5.),
		#            spotpy.parameter.Uniform('snowtemp',-6.,4.)
        
        self.obspath = '/RHESSys/Como/obs/como_q_obs.pcl'
        self.outpath = '/RHESSys/Como/out/opt'
        
        self.start_date = pd.datetime(2003,10,1) # simulation spinup start (RHESSys format)
        self.end_date = pd.datetime(2007,10,5) # simulation end date (RHESSys format)
        self.a_start_date = '2004-10-1' # analysis start date, pandas format
        self.a_end_date = '2007-09-30' # analysis end date, pandas format
        
        # read in the observations
        obs = pd.read_pickle(self.obspath)[self.a_start_date:self.a_end_date]
	del obs['q_liter_per_day']
	del obs['Unnamed: 3']
	obs['wateryear'] = obs.index.map(rut.wateryear) # add the water year
	obs['datetime'] = obs.index
	evaldates = obs.datetime # pull out the observation dates
	clean_indexer = np.isnan(obs.discharge.as_matrix()) # generate an indexer for the nan values
	obs.dropna(inplace=True) # remove NaN values	
	obs = obs.groupby(by='wateryear').sum() # compute water year totals	
        obs = obs.discharge.as_matrix() # pull out the observations
        evaldates = evaldates[clean_indexer==0] # remove the dates with nans
        self.obs = obs # add the cropped and clean obs to the self object
        self.evaldates = evaldates # add the cropped and clean dates to the self object
        self.clean_indexer = clean_indexer # add the index values of the non-nan obs to the object
	print 'Observations Length: %s'%len(self.obs)	


    def parameters(self):
        # generate the parameters
        return spotpy.parameter.generate(self.params)


    def simulation(self,vector):
        
        gw1 = vector[0]
	trd = vector[1]
	crd = vector[2]
        #alpsnowscale = vector[1]
	#forsnowscale = vector[2]
	#plapse = vector[3]
	#pmult = vector[5]
        
        #create the output directory
        idx = np.random.randint(1,high=100000,size=1)[0]
        outdirpath = '%s/%s'%(self.outpath,idx) # generate the path
        os.makedirs(outdirpath) # create the output directory
        
        # run the simulation using the rhessys script
        cmd = 'sh /RHESSys/Como/scripts/rhessys_opt_ullr_par_annual_grid.sh %s %s %s %s %s %s %s %s %s %s'%(gw1,trd,crd,self.start_date.year,
self.start_date.month,self.start_date.day,self.end_date.year,
        self.end_date.month, self.end_date.day, idx)
        
        print cmd
        
        subprocess.call(cmd,shell=True)
        
        # load the output
	sim = rut.readRHESSysBasin('/RHESSys/Como/out/opt/%s/%s_tmp_basin.daily'%(idx,idx))[self.a_start_date:self.a_end_date] # load the basin output
	sf = sim.streamflow.as_matrix() # extract the streamflow
	sf[self.clean_indexer==1] = np.NaN
	sim.streamflow = sf # add the streamflow back in
	sim.dropna(inplace=True)
	sim = sim.groupby(by='wateryear').sum() # compute water year totals
	simulations = sim.streamflow.as_matrix() 
        #streamflow = pd.read_table('/RHESSys/Como/out/opt/%s/%s_tmp_basin.daily'%(idx,idx),sep = ' ')['streamflow'].as_matrix() # load the output
        
        # remove the output directory
        shutil.rmtree(outdirpath)
	print 'Simulation length: %s'%len(simulations)
        return simulations


    def evaluation(self,evaldates=False):
        # function to return the evaluation data
        if evaldates==True:
            return self.evaldates
        
        if evaldates==False:
            return self.obs


    def objectivefunction(self,simulation,evaluation):
        # compute the objective function
        objectivefunction = spotpy.objectivefunctions.rmse(evaluation,simulation) # we want to maximize this function
        return objectivefunction

spotpy_setup = spotpy_setup()

sampler = spotpy.algorithms.sceua(spotpy_setup, dbname='Como_SCEUA_15', dbformat='csv', parallel='mpi')

sampler.sample(3500, ngs=4, kstop = 30, pcento=0.005, peps=0.001)

alert.send_alert('barnhatb@colorado.edu','RHESSys Como Optimization Finished','Your script has finished')
