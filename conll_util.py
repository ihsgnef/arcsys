ID      = 0
FORM    = 1
LEMMA   = 2
CPOSTAG = 3
POSTAG  = 4
FEATS   = 5
HEAD    = 6
DEPREL  = 7
PHEAD   = 8
PDEPREL = 9

def read_conll_data(file_path):
    sentences = []
    with open(file_path) as f:
        sentence = []
        for row in f.readlines():
            row = row.lstrip().rstrip().split('\t')
            if len(row) == 1:
                # end of sentence
                sentences.append(sentence)
                sentence = []
                continue
            sentence.append((row[FORM].lower(), row[CPOSTAG], int(row[HEAD]),
                row[DEPREL]))
    return sentences

if __name__ == '__main__':
    f = 'en.tr100'
    ss = read_conll_data(f)
