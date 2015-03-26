#!/usr/bin/env python

import sys

__author__ = 'Nurzhan Saktaganov'

def main():
    numbers = []
    for line in sys.stdin:
        numbers.append(int(line))

    varbyte_encoder = varbyte_encode_arithmetic
    to_encode = numbers
    compressed = varbyte_encoder(to_encode)

    for byte in compressed:
        sys.stdout.write(byte)
     
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

def varbyte_encode_bitwise(numbers):
    result = []
    for number in numbers:
    	number_bytes = []
    	while number > 127:
    		number_bytes.append(chr(number & 127))
    		number = number >> 7
    	number_bytes.append(chr(number))
    	number_bytes[0] = chr(ord(number_bytes[0]) + 128)
    	number_bytes.reverse()
    	result += number_bytes
    return result

def varbyte_encode_arithmetic(numbers):
    result = []
    for number in numbers:
    	number_bytes = []
    	while number > 127:
    		number_bytes.append(chr(number % 128))
    		number /= 128
    	number_bytes.append(chr(number))
    	number_bytes[0] = chr(ord(number_bytes[0]) + 128)
    	number_bytes.reverse()
    	result += number_bytes
    return result

if __name__ == '__main__':
    main()