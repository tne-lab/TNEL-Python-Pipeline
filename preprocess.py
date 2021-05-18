from oe_to_mne import load_OE_to_MNE
import mne
import numpy as np

def preprocess(raw):
    ## Input Variables ##############################
    trialLen = 1 # Number of seconds per trial
    #cutoff = 0.5 # Cut first/last .5 seconds from each 
    downsample_fs = 1500 # What frequency to downsample to
    ##################################################

    # Filter
    raw.filter(0.1, 200)

    # data resample
    raw.resample(downsample_fs)

    # Cut data into trials (epochs) mne.EpochsArray
    picks = mne.pick_types(raw.info, eeg=True)
    data, times = raw[:]
    events = mne.find_events(raw)

    # Make trial events
    trialSamps = downsample_fs * trialLen
    dataShape = data.shape
    overflow = dataShape[1] % trialSamps
    # MNE forces you to use events to set timing for trials
    # Create events with event_id=9 for trial start timings (after our 1-8 ttls)
    trialEvents = []
    n = int(raw.first_time) + 1
    while n <= dataShape[1] - overflow + 1:
        trialEvents.append([n, 0, 9]) # [timestamp, N/A, event_id]
        n += trialSamps
    
    raw.add_events(np.array(trialEvents), stim_channel='TTL') # adding our trial events
    events = mne.find_events(raw)

    # Split into trials based on trial events
    processedObj = mne.Epochs(raw, events, event_id=9, tmin = 0.0, tmax = trialLen, baseline = None, preload=True)

    scalings = {'eeg':2000}

    # Plot to look for bad trials/channesl
    processedObj.plot(scalings = scalings, n_epochs = 2, show=True, block=True)
    print(processedObj)
    
    # Bipolar ref
    bi1 = []
    bi2 = []
    for n in range(0,16, 2):
        if 'CH'+str(n) not in processedObj.info['bads']:
            bi1.append(processedObj.ch_names[n])
        if 'CH'+str(n+1) not in processedObj.info['bads']:
            bi2.append(processedObj.ch_names[n+1])
    print(bi1, bi2)

    if len(processedObj.info['bads']) > 0:
        print('Some bad channels')

    print(processedObj.ch_names)

    # Bipolar based upon channel names
    processedObj = mne.set_bipolar_reference(processedObj, bi1, bi2)

    return processedObj



if __name__ == "__main__":
    path = r'C:\Users\Mark\Documents\Open Ephys\test_data_2021-05-13_15-05-08'
    raw = load_OE_to_MNE(path)
    print(raw)

    pre = preprocess(raw)
    scalings = {'eeg':2000}
    pre.plot(scalings=scalings, show=True, block=True)

