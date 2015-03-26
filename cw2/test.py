#!/usr/bin/env python

import sys
from VarByte import VarByte
from Simple9 import Simple9

__author__ = 'Nurzhan Saktaganov'

def main():
    numbers = []
    for line in sys.stdin:
        numbers.append(int(line))

    to_encode = numbers
    print 'Original numbers count: %d' % (len(to_encode), )

    compressed = Simple9.encode(to_encode)
    restored = Simple9.decode(compressed)
    print 'Testing Simple9 with diff'
    print 'Compressed with diff size: %d bytes' % (len(compressed), )
    print 'Restored numbers count: %d' % (len(restored), )
    for i in range(len(to_encode)):
        if restored[i] != to_encode[i]:
            raise 'Simple9 with diff error'
    
    compressed = Simple9.encode(to_encode,to_diff=False)
    restored = Simple9.decode(compressed,from_diff=False)
    print 'Testing Simple9 without diff'
    print 'Compressed without diff size: %d bytes' % (len(compressed), )
    print 'Restored numbers count: %d' % (len(restored), )
    for i in range(len(to_encode)):
        if restored[i] != to_encode[i]:
            raise 'Simple9 without diff error'

    compressed = VarByte.encode(to_encode)
    restored = VarByte.decode(compressed)
    print 'Testing Varbyte with diff'
    print 'Compressed with diff size: %d bytes' % (len(compressed), )
    print 'Restored numbers count: %d' % (len(restored), )
    for i in range(len(to_encode)):
        if restored[i] != to_encode[i]:
            raise 'VarByte with diff error'
    
    compressed = VarByte.encode(to_encode,to_diff=False)
    restored = VarByte.decode(compressed,from_diff=False)
    print 'Testing Varbyte without diff'
    print 'Compressed without diff size: %d bytes' % (len(compressed), )
    print 'Restored numbers count: %d' % (len(restored), )
    for i in range(len(to_encode)):
        if restored[i] != to_encode[i]:
            raise 'VarByte without diff error'

if __name__ == '__main__':
    main()