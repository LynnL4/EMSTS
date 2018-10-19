#!/usr/bin/env python

import os
import sys
import struct
'''
struct am335x_baseboard_id {
       u8 magic[4];
       u8 name[8];
       u8 version[4];
       u8 serial[12];
       u8 config[32];
       u8 mac_addr[3][6];
};
#define as I8sI12s32s18s
'''
eeprom_path = "/sys/devices/platform/ocp/44e0b000.i2c/i2c-0/0-0050/eeprom"
# eeprom_path = "/sys/devices/platform/ocp/44e0b000.i2c/i2c-0/0-0050/at24-0/nvmem"

class eeprom:
    def __init__(self,dumpName = ''):
        self.eeprom_dump = struct.Struct("I8s4s12s32s18s")

    def readBoardinfo(self):
        self.fp_sys = open(eeprom_path,'rb')
        self.eeprom_dump = self.fp_sys.read(78)
        self.fp_sys.close()

        self.magic,\
        self.name,\
        self.version,\
        self.serial,\
        self.config,\
        self.mac_addr = \
            struct.unpack("I8s4s12s32s18s",self.eeprom_dump)

        # print(self.name, self.version, self.serial, self.mac_addr)
        return self.name,self.version,self.serial


    def writeBoardinfo(self,new_name,new_version,new_serial):
        self.name = new_name
        self.version = new_version
        self.serial = new_serial
        # print("Write to eeprom.tmp then to eeprom")
        # print("name    = {}".format(self.name))
        # print("version = {}".format(self.version))
        # print("serial  = {}".format(self.serial))

        self.fp_local = open('eeprom.tmp','wb+')
        self.eeprom_dump = struct.pack('I8s4s12s32s18s', self.magic,\
                                                        self.name,\
                                                        self.version,\
                                                        self.serial,\
                                                        self.config,\
                                                        self.mac_addr)
        self.fp_local.write(self.eeprom_dump)
        self.fp_local.close()
        os.system("sync")
        os.popen('hexdump -C ./eeprom.tmp').read()

    	os.system("dd if=./eeprom.tmp of=" + eeprom_path + " > /dev/null 2>&1")
        os.system("sync")

    def restore_default(self, res = 'resource/bbgw-eeprom.dump'):
        os.system("dd if=" + res + " of=" + eeprom_path + " bs=1k > /dev/null 2>&1")

#Test eeprom class
if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: {} version serial [name]".format(sys.argv[0]))
        quit(1)

    eep_obj = eeprom()
    eep_obj.restore_default()
        
    # read
    name,version,serial = eep_obj.readBoardinfo()
    '''
    print("************ Read from eeprom  ************")
    print("name    = {}".format(name))
    print("version = {}".format(version))
    print("serial  = {}".format(serial))
    '''

    # write
    # version = 'GW1A'
    version = sys.argv[1]
    # serial = '4318GW000010'
    serial  = sys.argv[2]
    if len(sys.argv) > 3:
        name = sys.argv[3]

    print("************ Write eeprom ************")
    eep_obj.writeBoardinfo(name,version,serial)

    name,version,serial = eep_obj.readBoardinfo()
    print("************ Read from eeprom  ************")
    print("name    = {}".format(name))
    print("version = {}".format(version))
    print("serial  = {}".format(serial))
    quit(0)

