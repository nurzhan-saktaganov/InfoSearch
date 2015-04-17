import base64

class Simple9:
    # constants
    MAX_1_BIT_NUMBER  = (1 << 1) - 1
    MAX_2_BIT_NUMBER  = (1 << 2) - 1
    MAX_3_BIT_NUMBER  = (1 << 3) - 1
    MAX_4_BIT_NUMBER  = (1 << 4) - 1
    MAX_5_BIT_NUMBER  = (1 << 5) - 1
    MAX_7_BIT_NUMBER  = (1 << 7) - 1
    MAX_9_BIT_NUMBER  = (1 << 9) - 1
    MAX_14_BIT_NUMBER = (1 << 14) - 1
    MAX_28_BIT_NUMBER = (1 << 28) - 1

    MAX_N_BIT_NUMBERS =\
    [\
          MAX_1_BIT_NUMBER\
        , MAX_2_BIT_NUMBER\
        , MAX_3_BIT_NUMBER\
        , MAX_4_BIT_NUMBER\
        , MAX_5_BIT_NUMBER\
        , MAX_7_BIT_NUMBER\
        , MAX_9_BIT_NUMBER\
        , MAX_14_BIT_NUMBER\
        , MAX_28_BIT_NUMBER\
    ]

    MASK_8_BIT = 0xff
    MASK_32_BIT = 0xffffffff

    NUM_COUNTS =\
        [28, 14, 9, 7, 5, 4, 3, 2, 1]
    SIZES_IN_BIT =\
        [1, 2, 3, 4, 5, 7, 9, 14, 28]
    CASES =\
        [0, 1, 2, 3, 4, 5, 6, 7, 8]

    @staticmethod
    def encode(input_numbers,to_diff=True):
        if to_diff:
            numbers = Simple9.__to_diff_representation(input_numbers)
        else:
            numbers = input_numbers

        begin, end, result = 0, len(numbers), []
        
        while begin < end:
            # get portion
            for i in range(len(Simple9.NUM_COUNTS)):
                portion = numbers[begin: begin + Simple9.NUM_COUNTS[i]]
                if len(portion) == Simple9.NUM_COUNTS[i] \
                        and max(portion) <= Simple9.MAX_N_BIT_NUMBERS[i]:
                    break
            # encode portion
            encoded_portion = Simple9.__encode_portion(portion)

            result += encoded_portion
            begin += len(portion)

        return base64.b64encode(str(bytearray(result)))

    @staticmethod
    def decode(input_byte_list,from_diff=True):
        result = []

        bytes_count = len(input_byte_list)

        for i in range(0, bytes_count, 4):
            encoded_32_bits =\
                (ord(input_byte_list[i]) << 24)\
                | (ord(input_byte_list[i + 1]) << 16)\
                | (ord(input_byte_list[i + 2]) << 8)\
                | (ord(input_byte_list[i + 3]))

            # control_4_bits
            case = encoded_32_bits >> 28
            numbers_count = Simple9.NUM_COUNTS[case]
            each_number_size_in_bits = Simple9.SIZES_IN_BIT[case]
            mask = Simple9.MAX_N_BIT_NUMBERS[case]

            portion = []
            for i in range(numbers_count):
                portion.append(encoded_32_bits & mask)
                encoded_32_bits = encoded_32_bits >> each_number_size_in_bits

            portion.reverse()
            
            result += portion

        if from_diff:
            result = Simple9.__from_diff_representation(result)

        return result


    @staticmethod
    def __to_diff_representation(numbers):
        result = [ numbers[len(numbers) - i - 1] - numbers[len(numbers) - i - 2]\
                        for i in range(len(numbers) - 1)]
        result.append(numbers[0])
        result.reverse()
        return result

    @staticmethod
    def __from_diff_representation(numbers):
        summ, result = 0, []
        for number in numbers:
            summ += number
            result.append(summ)
        return result

    @staticmethod
    def __encode_portion(portion):
        numbers_count = len(portion)
        case = Simple9.NUM_COUNTS.index(numbers_count)

        control_4_bits = case << 28
        each_number_size_in_bits = Simple9.SIZES_IN_BIT[case]

        encoded_28_bits = 0
        for number in portion:
            encoded_28_bits = encoded_28_bits << each_number_size_in_bits
            encoded_28_bits += number

        encoded_32_bits = (control_4_bits | encoded_28_bits) #& MASK_32_BIT

        encoded_byte_list = []
        for i in range(4):
            encoded_byte_list.append(chr(encoded_32_bits & Simple9.MASK_8_BIT))
            encoded_32_bits = encoded_32_bits >> 8

        encoded_byte_list.reverse()

        return encoded_byte_list