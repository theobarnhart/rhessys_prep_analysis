'''
Script to run RHESSys simulations within an optimizer using spotpy

'''

import numpy as np
import pandas as pd
import spotpy
import subprocess
import shutil
import os

class spotpy_setup():
    # the __init__ runs just once at the begining of the optimization
    def __init__(self):
        # define the parameters for the model
        self.params = [spotpy.parameter.Uniform('gw1',0.0001,0.4),
                    spotpy.parameter. Uniform('gw2',0.0001,1.),
                    spotpy.parameter. Uniform('m',0.01,15.),
                    spotpy.parameter. Uniform('ksat',0.0001,10.),
                    spotpy.parameter. Uniform('crd',2.,10.),
                    spotpy.parameter. Uniform('trd',0.1,2.),
                    spotpy.parameter. Uniform('po',0.1,2.),
                    spotpy.parameter. Uniform('pa',0.1,2.)]
        
        self.obspath = '/RHESSys/Como/obs/como_q_obs.pcl'
        self.outpath = '/RHESSys/Como/out/opt'
        
        self.start_date = '2010 10 1' # simulation spinup start (RHESSys format)
        self.end_date = '2012 10 5' # simulation end date (RHESSys format)
        self.a_start_date = '2011-10-1' # analysis start date, pandas format
        self.a_end_date = '2012-09-30' # analysis end date, pandas format
        
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
        
        
        #create the output directory
        diridx = '%s%s%s%s%s%s%s%s'%(gw1,gw2,m,ksat,crd,trd,po,pa) # unique folder indexer
        outdirpath = '%s/%s'%(self.outpath,diridx)
        os.makedirs(outdirpath) # create the output directory
        
        # run the simulation using the rhessys script
        subprocess.call('sh /RHESSys/Como/scripts/rhessys_opt_ullr.sh %s %s %s %s %s %s %s %s %s/%s %s %s'%(gw1,gw2,m,ksat,crd,trd,po,pa,outdirpath,diridx,self.start_date,self.end_date),shell=True)
        
        # load the output
        streamflow = pd.read_table('%s/%s_basin.daily'%(outdirpath,diridx),sep = ' ')['streamflow'].as_matrix() # load the output
        
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
        objectivefunction = spotpy.objectivefunctions.nse(evaluation,simulation)
        return objectivefunction
