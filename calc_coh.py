import mne
from mne.connectivity import spectral_connectivity
from oe_to_mne import load_OE_to_MNE
from preprocess import preprocess
import numpy as np
import matplotlib.pyplot as plt

def calc_coh(processed):
    ######## Input values #####
    fmin = 1
    fmax = 30
    tmin = 0.1
    tmax = 0.9
    ###########################

    data = np.array(processed[:])
    only_data = data[:,0:8,:]

    # Not possible to do full length TFR here...
    [coh, freqs, times, n_epochs, n_tapers] = spectral_connectivity(only_data, fmin = fmin, fmax = fmax, sfreq = 1500, tmin = 0.1, tmax = 0.9)

    nrows, ncols = coh.shape[:2]
    fig, axes = plt.subplots(nrows, ncols, sharex=True, sharey=True)
    for i in range(nrows):
        for j in range(i+1):
            axes[i,j].plot(freqs, coh[i,j,:])
            axes[j,i].plot(freqs, coh[i,j,:])
            axes[i, j].set(xlim=[fmin, fmax], ylim=[-0.2, 1])
            axes[j, i].set(xlim=[fmin, fmax], ylim=[-0.2, 1])
    
    fig.suptitle('Coherence across chan combinations')
    plt.tight_layout()
    plt.show()

    #plt.imshow(coh)

if __name__ == "__main__":
    path = r'C:\Users\Mark\Documents\Open Ephys\test_data_2021-05-13_15-05-08'
    raw = load_OE_to_MNE(path)
    print(raw)

    processed = preprocess(raw)

    calc_coh(processed)