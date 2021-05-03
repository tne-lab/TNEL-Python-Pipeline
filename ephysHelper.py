# -*- coding: utf-8 -*-
"""
Created on Thu Sep 26 15:02:56 2019

@author: markschatza@gmail.com
TNEL Analysis code
"""
import numpy as np
from scipy import signal

'''
Helper Functions
'''
def butter_bandpass(lowcut, highcut, fs, order=2):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = signal.butter(order, [low, high], btype='bandpass')
    return b, a


def butter_bandpass_filter(data, lowcut, highcut, fs, order=2):
    b, a = butter_bandpass(lowcut, highcut, fs, order=order)
    filteredData = signal.filtfilt(b, a, data)
    return filteredData


def butter_lowpass(cutoff, fs, order=2):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = signal.butter(order, normal_cutoff, btype='low', analog=False)
    return b, a

def butter_lowpass_filter(data, cutoff, fs, order=2):
    b, a = butter_lowpass(cutoff, fs, order=order)
    y = signal.filtfilt(b, a, data)
    return y


class Event:
    def __init__(self, data, tsStart = 0):
        self.eventId = data['eventId'] # Event id holds info about the event. TTL event: 1 = On, 0 = Off
        self.nodeId = data['nodeId'] # What node (Plugin) did this event come from?
        self.eventType = data['eventType']
        self.channel = data['channel']
        
        self.ts = []
        for t in data['timestamps']:
            self.ts.append(t - tsStart) # Zero out the timestamp to correspond with continuous data


class Con:
    def __init__(self, data):
        self.data = data['data'] # Volatage data
        self.lowPassData = self.data
        self.fs = float(data['header']['sampleRate']) # Sample Rate
        self.interpTs(data['timestamps']) # Interpolate timestamps for all data points (Only has 1 time stamp for each buffer of 1024 data points)

    def interpTs(self, ts):
        tsStart = ts[0]
        tsEnd = ts[-1] + 1023
        self.ts = np.linspace(0, len(self.data), len(ts) * 1024) # Creates the array of timestamps
        #i = 0
        #for t in self.ts:
        #    self.ts[i] = t - tsStart # Zero out the timestamps, just makes it look better when graphing/explaining
        #    i = i + 1
        self.tsStart = tsStart # Send the ts start to event data
        
    def lowPass(self, cutoff = 20):
        self.lowPassData = butter_lowpass_filter(self.data,cutoff,self.fs)
        return self.lowPassData

    def getPhase(self, band = [4, 8]):
        bandpassData = butter_bandpass_filter(self.data, band[0], band[1], self.fs)
        hData = signal.hilbert(bandpassData)
        return np.angle(hData)

import OpenEphys
        
'''
Load Data
'''
def loadConOE(path):
    raw = OpenEphys.load(path)
    return Con(raw)

def loadEventsOE(path, tsStart):
    raw = OpenEphys.load(path)
    return Event(raw, tsStart)

import Binary



### Create avg
class Avg:
    def __init__(self):
        self.sum = 0
        self.num = 0
    def addVal(self, val):
        self.sum += val
        self.num += 1
    def getAvg(self):
        return self.sum/self.num   


def rose_plot(ax, angles, bins=16, density=None, offset=0, lab_unit="degrees",
              start_zero=False, alpha = 1, **param_dict):
    """
    Plot polar histogram of angles on ax. ax must have been created using
    subplot_kw=dict(projection='polar'). Angles are expected in radians.
    """
    # Wrap angles to [-pi, pi)
    angles = (angles + np.pi) % (2*np.pi) - np.pi

    # Set bins symetrically around zero
    if start_zero:
        # To have a bin edge at zero use an even number of bins
        if bins % 2:
            bins += 1
        bins = np.linspace(-np.pi, np.pi, num=bins+1)

    # Bin data and record counts
    count, bin = np.histogram(angles, bins=bins)

    # Compute width of each bin
    widths = np.diff(bin)

    # By default plot density (frequency potentially misleading)
    if density is None or density is True:
        # Area to assign each bin
        area = count / angles.size
        # Calculate corresponding bin radius
        radius = (area / np.pi)**.5
    else:
        radius = count

    # Plot data on ax
    ax.bar(bin[:-1], radius, zorder=1, align='edge', width=widths, fill=True, edgecolor='k', linewidth=1, alpha = alpha)

    # Set the direction of the zero angle
    ax.set_theta_offset(offset)

    # Remove ylabels, they are mostly obstructive and not informative
    ax.set_yticks([])

    if lab_unit == "radians":
        label = ['$0$', r'$\pi/4$', r'$\pi/2$', r'$3\pi/4$',
                  r'$\pi$', r'$5\pi/4$', r'$3\pi/2$', r'$7\pi/4$']
        ax.set_xticklabels(label)