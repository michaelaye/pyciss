
# coding: utf-8

# In[ ]:

import wavelets
from wavelets import WaveletAnalysis


# In[ ]:

def do_wavelet(x):
    dt = 1
    wa = WaveletAnalysis(x, dt=dt)
    power = wa.wavelet_power
    scales = wa.scales
    t = wa.time
    T, S = np.meshgrid(t, scales)
    return T, S, power, t

def plot_wavelet(x1, x2):
    T, S, power, t = do_wavelet(x1)
    print(power.max())
    fig, ax = plt.subplots(nrows=2, sharex=True, figsize=(4.5,6))
    im = ax[0].contourf(T, S, power*1000, 100, cmap='viridis', vmax=1.5)
    plt.colorbar(im, ax=ax[0])
    T, S, power, t = do_wavelet(x2)
    print(power.max())
    im2 = ax[1].contourf(T, S, power*1000, 100, cmap='viridis', vmax=1.5)
    plt.colorbar(im2, ax=ax[1])
    for axis in ax:
        axis.set_yscale('log')
        axis.set_ylabel("Arbitrary power in 1/distance")
    ax[0].set_title("Maximum dispersion row")
    ax[1].set_title("Minimum dispersion row")
    ax[1].set_xlabel("Along Azimuth [pixel]")


# In[ ]:



