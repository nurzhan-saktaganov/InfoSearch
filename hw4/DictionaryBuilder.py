class DictionaryBuilder:
    @staticmethod
    def build(path):
        dictionary = {}
        f = open(path)
        offset, line = 0, f.readline()
        while line:
            splitted = line.split('\t')
            size = len(line)
            dictionary[splitted[0].decode('utf-8')] = [offset, size - 1]
            offset += size
            line = f.readline()

        f.close()

        return dictionary