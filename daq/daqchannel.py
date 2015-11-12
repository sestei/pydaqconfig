#!/usr/bin/env python

import math
import re

class DAQChannelDatatypeInvalid(Exception):
    pass

class DAQChannelBitrateMustBePowerOf2(Exception):
    pass

class DAQChannelBitrateTooHigh(Exception):
    def __init__(self, maxdatarate, *args):
        self.maxdatarate = maxdatarate
        super(DAQChannelBitrateTooHigh, self).__init__(*args)

class DAQChannel(object):
    # CDS data types in bytes
    TYPEBYTES = {
        1: 4, # int
        2: 4, # float
        4: 2, # short
    }
  
    def __init__(self, name, channum, model=None, datatype=4,
                 enabled=False, acquire=False, datarate=65536):
        self._name = name
        self._short_name = name[name.find('-')+1:]
        self._channum = int(channum)
        self._model = model
        self.enabled = enabled
        self.acquire = acquire
        self.datarate = datarate
        self.datatype = datatype

    # ===== PROPERTIES =====

    # name: the DAQ channel name, read only
    @property
    def name(self):
        return self._name

    # short_name: the DAQ channel name without IFO and model prefix, read only
    @property
    def short_name(self):
        return self._short_name

    # channum: the DAQ channel number, read only
    @property
    def channum(self):
        return self._channum

    # datatype: the datatype (generally 4), r/w
    @property
    def datatype(self):
        return self._datatype
    @datatype.setter
    def datatype(self, datatype):
        if datatype not in self.TYPEBYTES.keys():
            raise DAQChannelDatatypeInvalid()
        
        self._datatype = datatype

    # datarate: daq datarate for this channel, r/w
    @property
    def datarate(self):
        return self._datarate
    @datarate.setter
    def datarate(self, datarate):
        datarate = int(datarate)
        if self._model and (datarate > self._model.datarate):
            raise DAQChannelBitrateTooHigh(self._model.datarate)
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

    # enabled: makes channel visible, r/w
    @property
    def enabled(self):
        return self._enabled == 1
    @enabled.setter
    def enabled(self, value):
        if value:
            self._enabled = 1
        else:
            self._enabled = 0
            self.acquire = False

    # ===== METHODS =====
    
    def get_bytes_per_second(self):
        return self.TYPEBYTES[self.datatype] * self.datarate * self.acquire
    
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
