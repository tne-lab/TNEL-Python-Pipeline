import tnellibs
from tkinter.filedialog import askopenfilename,asksaveasfile, askdirectory
from glob import glob

'''
loadOpenEphys()
Loads OE data

Inputs:
    procID = ID of processor that you want to return data for
    path = path to data (if no path given will open prompt to choose a folder)
    events = true/false. Loads in all_channels.events or events from binary file
    recording = if using binary format can have multiple recordings within the same folder. ie pressing start and stop record without changing path/restarting OE will create new recording
    channelMaps = channels to return (list form ie [1,2,3,4] to load first 4 channels)

Outputs:
    Con data structure - see below for details
    Event data structure - if events = True

    Con data Structure
    Conatins 
        con.data  # Volatage data
        
        con.fs  # Sample Rate
        con.ts # timestamps
        
        can call con.lowPass() to lowpass filter the data
        can call con.getPhase() to get phase of data

    Event data structure
        event.eventId # Event id holds info about the event. TTL event: 1 = On, 0 = Off
        event.nodeId  # What node (Plugin) did this event come from?
        event.eventType # type of event
        event.channel # ttl channel
        event.ts = [] # timestamp of event

Usage:
    path = r'G:\Shared drives\TNEL - UMN\Project related material\Phase locked Stim Open loop\Closed Loop\Recordings\torte_standard\CLOSED_LOOP_2021-03-16_15-00-32'
    [con, event] = loadOpenEphys(115, path, True)
'''


def loadOpenEphys(procID, path = None, events = False, recording = 0, channelMap = []):
    path = path
    if path == None:
        root = Tk.Tk()
        root.withdraw()
        path = askdirectory()
    
    channel = 1
    index = 0 
    conData = []
    events = []
    oePaths = sorted(glob(path + '/*.continuous'))
    if len(oePaths > 1):
        for oePath in oePaths:
            if channel in channelMap:
                conData[index] = loadConOE(oePath)

        if events:
            events = loadEventsOE(path + '/all_channels.events')
    ''' Work in progress (working with OE team on big overhaul)
    # Binary Format
    else:
        Data, Rate = Binary.Load(path, processor=procId, )
    '''

    return conData, events



