class DictionaryBuilder:
    @staticmethod
    def build(path):
        dictionary = {}
        f = open(path)
        offset, line = 0, f.readline()
        while line:
            splitted = line.split('\t')
            size = len(line)
            # splitted[1] is document frequency of term
            dictionary[splitted[0].decode('utf-8')] = [offset, size - 1, int(splitted[1])]
            offset += size
            line = f.readline()

        f.close()

        return dictionary