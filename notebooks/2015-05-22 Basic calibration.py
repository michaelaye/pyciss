
# coding: utf-8

# In[1]:

import pandas as pd
import glob
folders = glob.glob('/Volumes/Data/ciss/opus/N*')


# In[2]:

len(folders)


# In[3]:

def process_folder(folder):
    import glob
    from pysis.exceptions import ProcessError
    from pyciss import pipeline as p
#     done = glob.glob(folder+'/*.map.cal.cub')
#     if done:
#         return folder,True
    img_name = glob.glob(folder+'/*.LBL')
    try:
        map_name = p.calibrate_ciss(img_name[0])
    except ProcessError:
        return folder,False
    return folder,True


# In[4]:

folders = pd.Series(folders)


# In[5]:

SOI = folders[folders.str.contains('N146734')]
SOI


# In[6]:

from IPython.parallel import Client
c = Client()


# In[7]:

lbview = c.load_balanced_view()


# In[8]:

results = lbview.map_async(process_folder, SOI[:2])


# In[9]:

from IPython.html.widgets import IntProgress
from IPython.display import display


# In[10]:

from time import sleep
prog = IntProgress(min=0, max=len(SOI)+1)
display(prog)
while not results.ready():
    prog.value = results.progress
    sleep(5)


# In[ ]:



