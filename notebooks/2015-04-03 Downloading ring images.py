
# coding: utf-8

# In[4]:

df = pd.read_table("/Users/klay6683/data/ciss/coiss_ahires.015.list.txt", sep=' ', skipinitialspace=True, header=None)
df


# In[5]:

df.info()


# In[2]:

from pyciss import opusapi


# In[3]:

opus = opusapi.OPUS()


# In[4]:

opus.get_filename('N1467345444_2')


# In[5]:

opus.download_results()


# In[7]:

def download_ciss(file_id):
    import os
    from pyciss import opusapi
    opus = opusapi.OPUS()
    targetfolder = os.path.join(opusapi.savepath, file_id)
    try:
        os.mkdir(targetfolder)
    except FileExistsError:
        pass
    opus.get_filename(file_id)
    opus.download_results(targetfolder)


# In[8]:

from IPython.parallel import Client
c = Client()


# In[9]:

lbview = c.load_balanced_view()


# In[10]:

results = lbview.map_async(download_ciss, df[0])


# In[11]:

from time import sleep
while not results.ready():
    sleep(5)
print("Done.")


# In[ ]:



