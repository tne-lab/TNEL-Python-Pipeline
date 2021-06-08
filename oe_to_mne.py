from open_ephys.analysis import Session
import mne
import numpy as np

def load_OE_to_MNE(path):
    # Load OE data
    session = Session(path)

    # Pull out recordNode of interest
    recordNodeIndex = 1 # funciton var
    recordnode = session.recordnodes[recordNodeIndex]

    # Pull out rec/exp of interest
    recordingNum = 0 # function var
    experimentNum = 0 # function var
    data = recordnode.recordings[recordingNum].continuous[experimentNum]
    events = recordnode.recordings[recordingNum].events
    # Create MNE Info
    nChans = data.samples.shape[1]

    # If metadata doesn't have names
    if data.metadata['names'] == []:
        data.metadata['names'] = ['CH'+str(i) for i in range(nChans)] #CH0 , CH1 ....
    # Add stim channel namess
    data.metadata['names'].extend(['TTL'])
    # Create channel type and extract fs
    chanTypes = (['eeg'] * nChans)
    chanTypes.extend(['stim'])
    fs = data.metadata['sample_rate']

    print(chanTypes)
    print(data.metadata['names'])
    print(fs)

    # Add stim channels (blank channels for our trial events)
    dataMatrix = data.samples.transpose()
    numSamps = len(data.timestamps) 
    dataMatrix = np.append(dataMatrix, [[0]*numSamps], axis=0)

    # Create info
    info = mne.create_info(ch_names=data.metadata['names'], sfreq=fs, ch_types=chanTypes)
    # Create mne object
    rawObj = mne.io.RawArray(dataMatrix, info, data.timestamps[0])
    
    # Add events
    if not events.empty:
        trueEvents = events[events['state'] == 1]
        rawObj.add_events(trueEvents[['timestamp','state','channel']].to_numpy(), stim_channel='TTL') # Events in form [ts, n/a, stim channel]


    return rawObj

if __name__ == '__main__':
    path = r'C:\Users\Mark\Documents\Open Ephys\2021-04-30_07-57-25'
    path = r'C:\Users\Mark\Documents\Open Ephys\test_data_2021-05-13_15-05-08'
    path = r'G:\Shared drives\TNEL - UMN\Project related material\Eric S\CLOSED_LOOP_2021-05-20_13-18-12'
    raw = load_OE_to_MNE(path)

    picks = mne.pick_types(raw.info, eeg=True)
    #data, times = raw[picks]
    
    #print('data: ', data.shape)
    print('events:' , mne.find_events(raw))

    scalings = {'eeg':2000}
    raw.plot(scalings=scalings, show=True, block=True, duration= 120, start = 7*60)
    
