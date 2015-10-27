#!/usr/bin/env python

import math
import re

class DAQChannelBitrateMustBePowerOf2(Exception):
    pass

class DAQChannelBitrateTooHigh(Exception):
    pass

class DAQChannel(object):
    def __init__(self, name, channum, model=None, datatype=4,
                 enabled=False, acquire=False, datarate=65536):
        self._name = name
        self._channum = int(channum)
        self._model = model
        self.enabled = enabled
        self.acquire = acquire
        self.datarate = datarate
        self._datatype = datatype

    # ===== PROPERTIES =====

    # name: the DAQ channel name, read only
    @property
    def name(self):
        return self._name

    # channum: the DAQ channel number, read only
    @property
    def channum(self):
        return self._channum

    # datatype: the datatype (generally 4), read only
    @property
    def datatype(self):
        return self._datatype

    # datarate: daq datarate for this channel, r/w
    @property
    def datarate(self):
        return self._datarate
    @datarate.setter
    def datarate(self, datarate):
        datarate = int(datarate)
        if self._model and (datarate > self._model.datarate):
            raise DAQChannelBitrateTooHigh
        if datarate and not (datarate & (datarate-1)):
            self._datarate = datarate
        else:
            raise DAQChannelBitrateMustBePowerOf2

    # acquire: activates recording of the channel, r/w
    @property
    def acquire(self):
        return self._acquire == 1
    @acquire.setter
    def acquire(self, value):
        if value:
            self._acquire = 1
        else:
            self._acquire = 0

    # ===== METHODS =====
    
    def to_ini(self, ini):
        cmt = '' if self.enabled else '#'
        ini.write('{cmt}[{c.name}]\n{cmt}acquire={c._acquire}\n{cmt}datarate={c.datarate}\n{cmt}datatype={c.datatype}\n{cmt}chnnum={c.channum}\n'.format(cmt=cmt, c=self))

    @staticmethod
    def from_ini(model, ini):
        lines = []
        for ii in range(5):
            # need 5 lines of data
            line = ini.readline()
            if not line: return None
            lines.append(line)

        ch_enabled = True
        if lines[0].startswith('#'):
            # disabled channel, remove comment signs
            ch_enabled = False
            for ii in range(len(lines)):
                lines[ii] = lines[ii][1:]

        data = ''.join(lines)
        return DAQChannel(extract_name(data),
                          extract_channum(data), model,
                          datarate=extract_datarate(data),
                          datatype=extract_datatype(data),
                          acquire=extract_acquire(data),
                          enabled=ch_enabled)


def extract_name(data):
    return re.search('.*\[(G2:.*)\]', data, re.MULTILINE).group(1)

def extract_channum(data):
    return int(re.search('.*chnnum=(\d*)', data, re.MULTILINE).group(1))

def extract_datatype(data):
    return int(re.search('.*datatype=(\d*)', data, re.MULTILINE).group(1))

def extract_datarate(data):
    return int(re.search('.*datarate=(\d*)', data, re.MULTILINE).group(1))

def extract_acquire(data):
    acq = int(re.search('.*acquire=(\d*)', data, re.MULTILINE).group(1))
    return acq == 1
