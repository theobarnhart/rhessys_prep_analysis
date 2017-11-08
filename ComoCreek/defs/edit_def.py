#!/usr/bin/python

import sys
import ntpath
import os

#defpth = "/RHESSys/defs2/zone.def"
#edkey = "lapse_rate_precip_default"
#newval = 0.003

defpth = sys.argv[1]
edkey = sys.argv[2]
newval = sys.argv[3]

path,basename = ntpath.split(defpth) # split out the basename

comps = basename.split('.') # split off the extension

# read in the definition file as a dictionary
d = {}
with open(defpth) as f:
    for line in f:
        (val,key) = line.split(None)
        d[key]=val

# edit the parameter

d[edkey] = newval

# print the new text file
with open(path+comps[0]+'.tmp',"w") as newfile:
    for key in d:
        newfile.write(str(d[key])+'\t'+key+'\n')

# remove the old file
os.system("rm "+defpth)
os.system("mv "+path+comps[0]+'.tmp '+defpth)