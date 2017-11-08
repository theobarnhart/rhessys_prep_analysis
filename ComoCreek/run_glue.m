crit = load('/Volumes/Users/Theo/projects/RHESSys/ComoCreek/data/glue_obfx.csv'); % load the objective function criteria
pars = load('/Volumes/Users/Theo/projects/RHESSys/ComoCreek/data/glue_params.csv'); % load the parameters
sims = load('/Volumes/Users/Theo/projects/RHESSys/ComoCreek/data/glue_simulations.csv'); % load the simulations
obs = load('/Volumes/Users/Theo/projects/RHESSys/ComoCreek/data/glue_obs.csv');

paramnames = str2mat('crd','gw1','gw2','ksat','m','pa','po','trd');
obfxnames = str2mat('pe','nse','log_nse');

mcat(pars,crit,[],sims,[],obs,'RHESSys',paramnames,obfxnames,[],[],[])