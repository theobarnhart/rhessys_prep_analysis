
# coding: utf-8

# In[87]:

import spotpy
import numpy as np

# In[88]:

class spotpy_setup(object):
    def __init__(self,dim=30):
        self.dim=dim
        self.params = []
        for i in range(self.dim):
            self.params.append(spotpy.parameter.Uniform(str(i),-32.768,32.768))

    def parameters(self):
        return spotpy.parameter.generate(self.params)

    def simulation(self, vector):
        firstSum = 0.0
        secondSum = 0.0
        for c in vector:
            firstSum += c**2.0
            secondSum += np.cos(2.0*np.pi*c)
            n = float(len(vector))
        return [-20.0*np.exp(-0.2*np.sqrt(firstSum/n)) - np.exp(secondSum/n) + 20 + np.e]

    def evaluation(self):
        observations=[0]
        return observations

    def objectivefunction(self,simulation,evaluation):
        objectivefunction= spotpy.objectivefunctions.nashsutcliff(evaluation,simulation)
        return objectivefunction


# In[89]:

spotpy_setup = spotpy_setup()


# In[90]:

sampler=spotpy.algorithms.sceua(spotpy_setup,dbname='ackleySCEUA',dbformat='csv')


# In[85]:

sampler.sample(100000,ngs=30,kstop=1000, pcento = 0.001, peps=0.001)

