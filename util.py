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
            if row[HEAD] != '_':
                sentence.append((row[FORM].lower(), row[CPOSTAG], 
                                int(row[HEAD]) - 1, row[DEPREL]))
            else:
                sentence.append((row[FORM].lower(), row[CPOSTAG], 
                                row[HEAD], row[DEPREL]))

    return sentences


def filter_non_projective(arcsys, sentences):
    gold_configs = []
    projective = []
    for sentence in sentences:
        gold_config = arcsys.get_gold_config(sentence)
        if not arcsys.is_not_projective(gold_config):
            gold_configs.append(gold_config)
            projective.append(sentence)
    return projective, gold_configs
