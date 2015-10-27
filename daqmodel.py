#/usr/bin/env python
import re
import daqchannel

class DAQModel(object):
    def __init__(self, name, channels, header):
        self._name = name
        self._channels = channels
        self._header = header
        self._datarate = self.get_datarate_from_header()

    # ===== PROPERTIES =====

    @property
    def name(self):
        return self._name

    @property
    def datarate(self):
        return self._datarate

    @property
    def channels(self):
        return self._channels

    # ===== METHODS ======

    def get_datarate_from_header(self):
        for line in self._header:
            if line.startswith('datarate='):
                m = re.match('datarate=(\d*)', line)
                return int(m.group(1))
        return -1

    @staticmethod
    def from_ini(name, ini):
        header = []
        channels = []

        # TODO: this assumes that all DQ channels appear at the end of the file.
        #       Is that guaranteed to be the case?
        while True:
            fpos = ini.tell()
            line = ini.readline()
            if not line: break
            if line.endswith('_DQ]\n'):
                ini.seek(fpos)
                break
            header.append(line)

        model = DAQModel(name, [], header)

        while True:
            channel = daqchannel.DAQChannel.from_ini(model, ini)
            if not channel: break
            channels.append(channel)

        model._channels = channels

        return model


