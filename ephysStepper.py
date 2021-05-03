import ephysHelper
import matplotlib.pyplot as plt
import numpy as np
from scipy import signal

class ephysStepper():
    def __init__(self, path):
        self.curr_pos = 0
        self.dataIntoBuffers = []
        self.filterDataIntoBuffers = []
        self.path = path
        self.filter = False
        self.magnitude = False
        self.psd = False


    def key_event(self, e):

        if e.key == "right":
            self.curr_pos = self.curr_pos + 1
        elif e.key == "left":
            self.curr_pos = self.curr_pos - 1
        else:
            return
        self.curr_pos = self.curr_pos % len(self.dataIntoBuffers)
        print(self.curr_pos)
        print(len(self.dataIntoBuffers[self.curr_pos]))
        self.ax[0].cla()
        self.ax[0].plot(self.dataIntoBuffers[self.curr_pos])
        self.ax[0].set_ylim(-2000,2000)
        self.ax[0].set_title('Raw Data (5 minute)')
        self.ax[0].set_xlabel('Sample')
        self.ax[0].set_ylabel('Voltage(uVolts)')
        
        ### Create psd of data
        if self.psd:
            f, pxx_den = signal.welch(self.dataIntoBuffers[self.curr_pos],fs = self.fs)
            self.ax[1].cla()
            self.ax[1].semilogy(f[1:25 * self.bufferSize], pxx_den[1:25 * self.bufferSize])
            self.ax[1].set_title('Power Spectral Density of Buffer')
            self.ax[1].set_xlabel('Frequency')
            self.ax[1].set_ylabel('Power Spectral Density')
        

        
        ### Plot filtered data
        if self.filter and not self.magnitude:
            self.ax[1].cla()
            self.ax[1].plot(self.filterDataIntoBuffers[self.curr_pos])
            self.ax[1].set_ylim(-500,500)
            self.ax[1].set_title('Filtered Data (1 second)')
            self.ax[1].set_xlabel('Sample')
            self.ax[1].set_ylabel('Voltage(uVolts)')
        

        ### plot filtered magnitude
        if self.magnitude:
            self.ax[1].cla()
            self.ax[1].plot(self.filterDataIntoBuffers[self.curr_pos])
            self.ax[1].set_ylim(-500,500)
            self.ax[1].set_title('Filtered Data (1 second)')
            self.ax[1].set_xlabel('Sample')
            self.ax[1].set_ylabel('Voltage(uVolts)')

        if self.phase:
            self.ax[1].cla()
            self.ax[1].plot(self.filterDataIntoBuffers[self.curr_pos])
            self.ax[1].set_title('Phase')
            self.ax[1].set_xlabel('Sample')
            self.ax[1].set_ylabel('Degrees')
        self.fig.canvas.draw()

    def stepThroughData(self,  bufferSize = 1, byEvents = False, eventChannel = 1, bandPass = False, lowPass = False, psd = False, dsFactor = 1, magnitude = False, phase = False):
        '''
        bufferSize = how many seconds in each step
        byEvents = step through events or every time point in data
        '''
        ### Load data
        con = ephysHelper.loadCon(self.path + '/106_CH2.continuous')
        if byEvents:
            events = ephysHelper.loadEvents(self.path + '/all_channels.events', con.tsStart)

        self.bufferSize = bufferSize
        self.fs = con.fs / dsFactor
        bufferLen = int(bufferSize * self.fs)
        con.data = con.data[::dsFactor]


        ### Filter data?
        if bandPass:
            filterData = ephysHelper.butter_bandpass_filter(con.data,4,8,self.fs)
        if lowPass:
            filterData = con.lowPass()
        if bandPass or lowPass:
            self.filter = True
        if magnitude:
            self.magnitude = True
            x = abs(signal.hilbert(filterData))
            N = 600
            cumsum = np.cumsum(np.insert(x, 0, 0)) 
            
            filterData = (cumsum[N:] - cumsum[:-N]) / float(N)

        ### PSD Data?
        if psd:
            self.psd = True

        if phase:
            self.phase = True
            filterData = ephysHelper.butter_bandpass_filter(con.data,4,8,self.fs)
            filterData = np.rad2deg(np.angle(signal.hilbert(filterData)))

            phaseData = ephysHelper.loadCon(self.path + '/105_CH2.continuous')
            filterData = phaseData.data[::dsFactor]
        
        # if buffering by Event timestamps
        if byEvents: 
            eventTimes = []
            for n in range(len(events.ts)):
                if events.channel[n] == eventChannel and events.eventId[n] == 1:
                    eventTimes.append(events.ts[n])

            for ts in eventTimes:
                halfBuf = int(bufferLen/2)
                self.dataIntoBuffers.append(filterData[int(ts-halfBuf):int(ts+halfBuf)])
                if self.filter or self.phase:
                    self.filterDataIntoBuffers.append(filterData[int(ts-halfBuf):int(ts+halfBuf)])

        else: # Otherwise iterate through all data
            self.dataIntoBuffers = [con.data[i*bufferLen:(i+1)*bufferLen] for i in range((len(con.data) + bufferLen - 1) // bufferLen)]
            if self.filter:
                #self.filterDataIntoBuffers.append(filterData[int(ts-halfBuf):int(ts+halfBuf)])
                self.filterDataIntoBuffers = [filterData[i*bufferLen:(i+1)*bufferLen] for i in range((len(filterData) + bufferLen - 1) // bufferLen)]
                print('filtered!')

        # Plot and button callback function
        self.fig, self.ax = plt.subplots(1,2)
        self.fig.canvas.mpl_connect('key_press_event', self.key_event)
        self.ax[0].plot()
        self.ax[1].plot()
        plt.show()


from tkinter import Tk
from tkinter.filedialog import askdirectory

Tk().withdraw()
path = askdirectory()
print(path)

x = ephysStepper(path)
if 'ERP' in path or 'CLOSED_LOOP' in path or 'Parameter_sweeping' in path or 'stim' in path and not 'sham':
    byEvents = True
else:
    byEvents = False

x.stepThroughData(byEvents = False, bufferSize = 0.5, bandPass=True, dsFactor=60, phase = True)
