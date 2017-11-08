#!/Users/barnhatb/anaconda/bin/python

import spotpy
import numpy as np
import pandas as pd
import subprocess
import shutil
import os

class spotpy_setup():
    # the __init__ runs just once at the begining of the optimization
    def __init__(self):
        # define the parameters for the model
        self.params = [spotpy.parameter.Uniform('gw1',0.0001,0.4),
                    spotpy.parameter.Uniform('gw2',0.0001,1.),
                    spotpy.parameter.Uniform('m',0.01,200.),
                    spotpy.parameter.Uniform('ksat',0.0001,300.),
                    spotpy.parameter.Uniform('crd',2.,10.),
                    spotpy.parameter.Uniform('trd',0.1,2.),
                    spotpy.parameter.Uniform('po',0.1,60.),
                    spotpy.parameter.Uniform('pa',0.1,60.),
		            spotpy.parameter.Uniform('plapse',0.000509,0.001011)]
        
        #spotpy.parameter.Uniform('smtc',0.,6.),
		#            spotpy.parameter.Uniform('msed',-650.,0.),
		#            spotpy.parameter.Uniform('raintemp',-2.,5.),
		#            spotpy.parameter.Uniform('snowtemp',-6.,4.)
        
        self.obspath = '/RHESSys/Como/obs/como_q_obs.pcl'
        self.outpath = '/RHESSys/Como/out/opt'
        
        self.start_date = pd.datetime(2006,10,1) # simulation spinup start (RHESSys format)
        self.end_date = pd.datetime(2009,10,5) # simulation end date (RHESSys format)
        self.a_start_date = '2007-10-1' # analysis start date, pandas format
        self.a_end_date = '2009-09-30' # analysis end date, pandas format
        
        # read in the observations
        obs = pd.read_pickle(self.obspath)[self.a_start_date:self.a_end_date]
        obs['datetime'] = obs.index
        evaldates = obs.datetime # pull out the observation dates
        obs = obs.discharge.as_matrix() # pull out the observations
        # generate the clean indexer, 1 = nan, 0 = data
        clean_indexer = np.isnan(obs) # generate an indexer for the nan values
        obs = obs[clean_indexer==0] # remove the nan values
        evaldates = evaldates[clean_indexer==0] # remove the dates with nans
        self.obs = obs # add the cropped and clean obs to the self object
        self.evaldates = evaldates # add the cropped and clean dates to the self object
        self.clean_indexer = clean_indexer # add the index values of the non-nan obs to the object


    def parameters(self):
        # generate the parameters
        return spotpy.parameter.generate(self.params)


    def simulation(self,vector):
        
        gw1 = vector[0]
        gw2 = vector[1]
        m = vector[2]
        ksat = vector[3]
        crd = vector[4]
        trd = vector[5]
        po = vector[6]
        pa = vector[7]
        plapse = vector[8]
	#smtc = vector[8]
	#msed = vector[9]
	#raintemp = vector[10]
	#snowtemp = vector[11]
        
        #create the output directory
        idx = np.random.randint(1,high=100000,size=1)[0]
        outdirpath = '%s/%s'%(self.outpath,idx) # generate the path
        os.makedirs(outdirpath) # create the output directory
        
        # run the simulation using the rhessys script
        cmd = 'sh /RHESSys/Como/scripts/rhessys_opt_ullr_par.sh %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s'%(gw1,
        gw2,m,ksat,crd,trd,po,pa,self.start_date.year,self.start_date.month,self.start_date.day,self.end_date.year,
        self.end_date.month, self.end_date.day, idx, plapse)
        
        print cmd
        
        subprocess.call(cmd,shell=True)
        
        # load the output
        streamflow = pd.read_table('/RHESSys/Como/out/opt/%s/%s_tmp_basin.daily'%(idx,idx),sep = ' ')['streamflow'].as_matrix() # load the output
        
        # load the streamflow data into the optimizer
        simulations = streamflow[self.clean_indexer==0] # clean out the nan values
        
        # remove the output directory
        shutil.rmtree(outdirpath)
        return simulations


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

sampler = spotpy.algorithms.sceua(spotpy_setup, dbname='testSCEUA_par2', dbformat='csv', parallel='mpi')

sampler.sample(1000, ngs=12, kstop = 30, pcento=0.005, peps=0.001)
