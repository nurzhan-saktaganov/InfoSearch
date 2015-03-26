#!/usr/bin/env python

import sys

__author__ = 'Nurzhan Saktaganov'

def main():

    input_bytes = [ord(byte) for line in sys.stdin.readlines() for byte in line ]
    varbyte_decoder = varbyte_decode_arithmetic
    decoded = varbyte_decoder(input_bytes)
    restored = decoded
    
    for number in restored:
        print number
    
def to_diff(numbers):
    result = [ numbers[len(numbers) - i - 1] - numbers[len(numbers) - i - 2]\
                    for i in range(len(numbers) - 1)]
    result.append(numbers[0])
    result.reverse()
    return result

def from_diff(numbers):
    summ, result = 0, []
    for number in numbers:
        summ += number
        result.append(summ)
    return result

def varbyte_decode_arithmetic(byte_list):
    number, result = 0, []
    for byte in byte_list:
        number *= 128
        number += (byte % 128)
        if byte > 127:
            result.append(number)
            number = 0
    return result

def varbyte_decode_bitwise(byte_list):
    number, result = 0, []
    for byte in byte_list:
        number = number << 7
        number += (byte & 127)
        if byte > 127:
            result.append(number)
            number = 0
    return result

if __name__ == '__main__':
    main()