#!/usr/bin/env python3
# Serena Geroe

# Test file

import os
import sys 

# Test: index into a bytes object
bytes_ob = bytes(bytes('8c04ba7511d10ccb85fa0ccd08004500003c00000000740175f008080808c0a8001900005343000102186162636465666768696a6b6c6d6e6f7071727374757677616263646566676869', 'utf8'))
#print((bytes_ob[0:20]))
#print(len(bytes_ob[0:20]))
#print(len(bytes_ob[20:28]))
#print((bytes_ob[20:28]))
print(os.getpid() & 0xFFFF)
