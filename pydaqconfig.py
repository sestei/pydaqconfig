#!/usr/bin/env python
import sys
import os

def get_model_name(filename):
    return os.path.splitext(os.path.basename(filename))[0]

if __name__ == '__main__':
    import daqmodel
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        filename = 'examples/G2SSM.ini'

    with open(filename) as ini:
        dm = daqmodel.DAQModel.from_ini(get_model_name(filename), ini)
    
    for chan in dm.channels:
        print "{c.name}: {c.datarate}Hz, enabled={c.enabled}, acquire={c.acquire}".format(c=chan)

    with open('out.ini', 'wb') as ini:
        dm.to_ini(ini)
