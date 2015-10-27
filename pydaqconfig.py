#!/usr/bin/env python

if __name__ == '__main__':
    import daqmodel
    with open('examples/G2SSM.ini') as ini:
        dm = daqmodel.DAQModel.from_ini('G2SSM', ini)
    
    for chan in dm.channels:
        print "{c.name}: {c.datarate}Hz, enabled={c.enabled}, acquire={c.acquire}".format(c=chan)
