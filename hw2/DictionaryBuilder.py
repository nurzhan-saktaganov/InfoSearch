class DictionaryBuilder:
    @staticmethod
    def build(path):
        dictionary = {}
        f = open(path)
        offset, line = 0, f.readline()
        while line:
            term, doc_ids = line.split('\t')
            offset += len(term) + 1
            size = len(doc_ids) - 1
            dictionary[term.decode('utf-8')] = [offset, size]
            offset += len(doc_ids)
            line = f.readline()

        f.close()

        return dictionary