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
	self.num = '39'
	self.maxflow = 20 # max streamflow [mm] needed for the leakage computation
#        # define the parameters for the model

	self.params = [spotpy.parameter.Uniform('gw1',0.0,1.0),
		    spotpy.parameter.Uniform('gw2',0.0,1.0),
		    spotpy.parameter.Uniform('sd',0.001,2.),
		    spotpy.parameter.Uniform('m',0.01,30.),
		    spotpy.parameter.Uniform('ksat',0.001,600.),
		    spotpy.parameter.Uniform('crd',0.01,2.0),
		    spotpy.parameter.Uniform('trd',0.01,0.5),
                    spotpy.parameter.Uniform('po',0.001,4.9),
		    spotpy.parameter.Uniform('pa',0.001,1000.),
		    spotpy.parameter.Uniform('snowtemp',0.,4.),
		    spotpy.parameter.Uniform('raintemp',-4.,0.),
		    spotpy.parameter.Uniform('smtc',0.001,0.6),
		    spotpy.parameter.Uniform('msed',-600,-0.001),
		    spotpy.parameter.Uniform('a',0.001,15),
		    spotpy.parameter.Uniform('b',0.001,25),
		    spotpy.parameter.Uniform('c',0.001,1)]

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
	sd = vector[2]
        m = vector[3]
        ksat = vector[4]
        crd = vector[5]
        trd = vector[6]
        po = vector[7]
        pa = vector[8]
	snowtemp = vector[9] 
	raintemp = vector[10]
	smtc = vector[11]
	msed = vector[12]
	a = vector[13] 
	b = vector[14]
	c = vector[15]
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
        scrpt = 'sh /RHESSys/Como/scripts/rhessys_opt_leakage.sh'
        args = '%s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s'%(gw1,gw2,sd,m,ksat,crd,trd,po,pa,snowtemp,raintemp,smtc,msed,a,b,c,self.maxflow,strtyear,strtmonth,strtday,endyear,endmonth,endday,idx)
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
        
        return sim.adj_streamflow.as_matrix() # return streamflow


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

sampler.sample(1500, ngs=17, kstop = 30, pcento=0.0025, peps=0.0025)

alert.send_alert('barnhatb@colorado.edu','RHESSys Como Optimization Finished','Your script has finished')
