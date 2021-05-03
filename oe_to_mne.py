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
        data.metadata['names'] = ['CH'+str(i) for i in range(nChans)]
    # Add stim channel namess
    data.metadata['names'].extend(['TTL'+str(i+1) for i in range(8)])
    # Create channel type and extract fs
    chanTypes = (['eeg'] * nChans)
    chanTypes.extend(['stim'] * 8)
    fs = data.metadata['sample_rate']

    print(chanTypes)
    print(data.metadata['names'])
    print(fs)

    # Add stim channels
    dataMatrix = data.samples.transpose()
    numSamps = len(data.timestamps)
    for i in range(8):
        dataMatrix = np.append(dataMatrix, [[0]*numSamps], axis=0)

    # Create info
    info = mne.create_info(ch_names=data.metadata['names'], sfreq=fs, ch_types=chanTypes)
    # Create mne object
    rawObj = mne.io.RawArray(dataMatrix, info, data.timestamps[0])
    
    # Add events
    for chan in events.channel.unique():
        curChannel = events[events['channel'] == chan]
        #print(curChannel[['timestamp','channel','state']].to_numpy())
        rawObj.add_events(curChannel[['timestamp','channel','state']].to_numpy(), stim_channel='TTL'+str(chan))


    return rawObj

if __name__ == '__main__':
    path = r'C:\Users\Mark\Documents\Open Ephys\2021-04-30_07-57-25'
    path = r'C:\Users\Mark\Documents\Open Ephys\2021-05-03_10-33-14'
    rawObj = load_OE_to_MNE(path)
    print(rawObj)

    scalings = {'eeg':2000}
    rawObj.plot(scalings=scalings, show=True, block=True)
    
