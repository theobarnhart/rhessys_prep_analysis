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
	self.num = '28'
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
                    spotpy.parameter.Uniform('po',0.,40.)]

        self.obspath = '/RHESSys/Como/obs/como_q_obs.pcl'
        self.outpath = '/RHESSys/Como/out/opt'
        
        self.start_date = pd.datetime(2003,10,1) # simulation spinup start (RHESSys format)
        self.end_date = pd.datetime(2007,10,5) # simulation end date (RHESSys format)
        self.a_start_date = '2004-10-1' # analysis start date, pandas format
        self.a_end_date = '2007-09-30' # analysis end date, pandas format
        
        # read in the observations
        obs = pd.read_pickle(self.obspath)[self.a_start_date:self.a_end_date]
        obs.interpolate(inplace=True,limit=100,limit_direction='both') # interpolate out nans
        
        self.obs = obs.discharge.as_matrix() # add the interpolated obs to the self object
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
        
	m = 12
	ksat = 450
	crd = 12.0
	trd = 3.0
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
        scrpt = 'sh /RHESSys/Como/scripts/rhessys_opt_ullr_par_grid.sh'
        args = '%s %s %s %s %s %s %s %s %s %s %s %s %s %s %s'%(gw1,gw2,m,ksat,crd,trd,po,pa,strtyear,strtmonth,strtday,endyear,endmonth,endday,idx)
        cmd =  '%s %s'%(scrpt,args)
        print cmd
        subprocess.call(cmd,shell=True) # run the simulation using the rhessys script
        
        # load the output
        sim = pd.read_table('/RHESSys/Como/out/opt/%s/%s_tmp_basin.daily'%(idx,idx),sep = ' ') # load the streamflow data into the optimizer
        sim['datetime'] = sim.apply(parse_dates,axis=1) # parse dates
        sim.index = pd.DatetimeIndex(sim.datetime) # make datetime index
        sim = sim[self.a_start_date:self.a_end_date] # crop to the analysis time period to match obs
        
        # remove the output directory
        shutil.rmtree(outdirpath)
        
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
