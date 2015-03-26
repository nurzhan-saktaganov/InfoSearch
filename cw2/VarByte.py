class VarByte:
    @staticmethod
    def encode(input_numbers,to_diff=True):
        if to_diff:
            numbers = VarByte.__to_diff_representation(input_numbers)
        else:
            numbers = input_numbers

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

    @staticmethod
    def decode(input_byte_list,from_diff=True):
        number, result = 0, []
        byte_list = map(ord, input_byte_list)
        for byte in byte_list:
            number *= 128
            number += (byte % 128)
            if byte > 127:
                result.append(number)
                number = 0
        if from_diff:
            result = VarByte.__from_diff_representation(result)

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
