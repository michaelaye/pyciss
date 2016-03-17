
# coding: utf-8

# In[ ]:

get_ipython().magic('matplotlib nbagg')
import wavelets
from wavelets import WaveletAnalysis


# In[ ]:

def genSine(f0, fs, dur):
    t = np.arange(dur)
    sinusoid = 0.5*np.sin(2*np.pi*t*(f0/fs))
    return sinusoid

def genNoise(dur):
    noise = np.random.normal(0,1,dur)
    noise = normalise(noise)
    return noise


# In[ ]:

f0 = 2
fs = 160
dur = 2*fs

x1 = genSine(f0, fs, dur)
x2 = genSine(6, fs, dur)

x = x1+x2


# In[ ]:

import seaborn as sns
sns.set_style('white')
sns.set_context('notebook')


# In[ ]:

sr = 50 # sample_rate in samples per second
dur = 5 # duration in seconds
n_samples = dur * sr
x1 = genSine(1, sr, n_samples)
x2 = genSine(2, sr, n_samples)
x3 = genSine(3, sr, n_samples)
x = np.hstack([x1, x2, x1])
# x=x1+x2
dt = 1/sr
wa = WaveletAnalysis(x, dt=dt)
power = wa.wavelet_power
scales = wa.scales
t = wa.time
fig, ax = plt.subplots(nrows=2)
T, S = np.meshgrid(t, scales)
ax[0].contourf(T, S, power, 100, cmap='viridis')
ax[0].set_ylim(0,4)
ax[1].plot(t,x, label='x')
# ax[1].legend(loc=1)
for axis in ax:
    axis.set_xlabel("Time [s]")
fig.suptitle('1+2 Hz, 1+3 Hz')
# ax[0].set_yscale('log')


# In[ ]:

wa.scales


# In[ ]:



