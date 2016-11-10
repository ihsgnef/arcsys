from collections import defaultdict

WORD  = 0
POS   = 1
HEAD  = 2
LABEL = 3
ROOT_ID  = -1
ROOT = "ROOT"
NULL = "NULL"


def sentence_to_dict(sentence):
    '''
    convert a sentence (list) to a dict where -1 maps to ROOT
    '''
    s = dict((i, word) for i, word in enumerate(sentence))
    s[ROOT_ID] = (ROOT, ROOT)
    return s


def left_right_deps(arcs, head, sentence):
    '''
    get the left-most and right-most dependents of the given head
    '''
    deps  = [d for h, d in arcs if h == head]
    deps.sort()
    l0 = (NULL, NULL) if len(deps) == 0 else sentence[deps[0]]
    r0 = (NULL, NULL) if len(deps) == 0 else sentence[deps[-1]]
    l1 = (NULL, NULL) if len(deps) < 2 else sentence[deps[1]]
    r1 = (NULL, NULL) if len(deps) < 2 else sentence[deps[-2]]
    return l0, l1, r1, r0


def baseline(config):
    sentence = sentence_to_dict(config.sentence)
    features = {}

    s0_word = NULL # top stack word
    s0_pos  = NULL # top stack pos
    b0_word = NULL # first buffer word
    b0_pos  = NULL # first buffer pos

    if len(config.buffer) > 0:
        i = config.buffer[0]
        b0_word = sentence[i][WORD]
        b0_pos = sentence[i][POS]

    if len(config.stack) > 0:
        i = config.stack[-1]
        s0_word = sentence[i][WORD]
        s0_pos = sentence[i][POS]

    s0_word_b0_word = s0_word + b0_word
    s0_pos_b0_pos = s0_pos + b0_pos

    features['b0_word=' + b0_word] = 1
    features['b0_pos=' + b0_pos] = 1
    features['s0_word=' + s0_word] = 1
    features['s0_pos=' + s0_pos] = 1
    features['s0_word_b0_word=' + s0_word_b0_word] = 1
    features['s0_pos_b0_pos=' + s0_pos_b0_pos] = 1

    return features

def rich_baseline(config):
    '''
    baseline feature set from paper
    Transition-based Dependency Parsing with Rich Non-local Features
    '''
    sentence = sentence_to_dict(config.sentence)
    head_of = defaultdict(lambda : (NULL, NULL))
    for h, t in config.arcs:
        head_of[t] = sentence[h]

    features = {}

    s0w  = NULL # top stack word
    s0p  = NULL # top stack pos
    n0w  = NULL # first buffer word
    n0p  = NULL # first buffer pos
    n1w  = NULL # second buffer word
    n1p  = NULL # second buffer pos
    n2w  = NULL # third buffer word
    n2p  = NULL # third buffer pos
    s0hw = NULL # word of head of stack top
    s0hp = NULL # pos of head of stack top
    s0lw = NULL # word of left-most dependent of stack top
    s0lp = NULL # pos of left-most dependent of stack top
    s0rw = NULL # word of right-most dependent of stack top
    s0rp = NULL # pos of right-most dependent of stack top
    n0lw = NULL # word of right-most dependent of buffer first
    n0lp = NULL # pos of right-most dependent of buffer first
    s0l2w = NULL
    s0l2p = NULL
    s0r2w = NULL
    s0r2p = NULL
    n0l2w = NULL
    n0l2p = NULL

    if len(config.buffer) > 0:
        i = config.buffer[0]
        n0w = sentence[i][WORD]
        n0p = sentence[i][POS]


    if len(config.buffer) > 1:
        i = config.buffer[1]
        n1w = sentence[i][WORD]
        n1p = sentence[i][POS]
        l0, l1, r1, r0 = left_right_deps(config.arcs, i, sentence)
        n0lw = l0[WORD]
        n0lp = l0[POS]
        n0l2w = l1[WORD]
        n0lrp = l1[POS]

    if len(config.buffer) > 2:
        i = config.buffer[2]
        n2w = sentence[i][WORD]
        n2p = sentence[i][POS]

    if len(config.stack) > 0:
        i = config.stack[-1]
        s0w = sentence[i][WORD]
        s0p = sentence[i][POS]
        l0, l1, r1, r0 = left_right_deps(config.arcs, i, sentence)
        s0lw = l0[WORD]
        s0lp = l0[POS]
        s0rw = r0[WORD]
        s0rp = r0[POS]
        s0l2w = l1[WORD]
        s0l2p = l1[POS]
        s0r2w = r1[WORD]
        s0r2p = r1[POS]
        s0hw = head_of[i][WORD]
        s0hp = head_of[i][POS]

    s0wp = ';'.join([s0w, s0p])
    n0wp = ';'.join([n0w, n0p])
    n1wp = ';'.join([n1w, n1p])
    n2wp = ';'.join([n2w, n2p])
    
    # from single words
    features['s0wp=' + s0wp] = 1
    features['s0w='  + s0w]  = 1
    features['s0p='  + s0p]  = 1
    features['n0wp=' + n0wp] = 1
    features['n0w='  + n0w]  = 1
    features['n0p='  + n0p]  = 1
    features['n1wp=' + n1wp] = 1
    features['n1w='  + n1w]  = 1
    features['n1p='  + n1p]  = 1
    features['n2wp=' + n2wp] = 1
    features['n2w='  + n2w]  = 1
    features['n2p='  + n2p]  = 1

    s0wpn0wp = ';'.join([s0wp, n0wp])
    s0wpn0w  = ';'.join([s0wp, n0w])
    s0wn0wp  = ';'.join([s0w, n0wp])
    s0wpn0p  = ';'.join([s0wp, n0p])
    s0pn0wp  = ';'.join([s0p, n0wp])
    s0wn0w   = ';'.join([s0w, n0w])
    s0pn0p   = ';'.join([s0p, n0p])
    n0pn1p   = ';'.join([n0p, n1p])

    # from word pairs
    features['s0wpn0wp=' + s0wpn0wp] = 1
    features['s0wpn0w='  + s0wpn0w]  = 1
    features['s0wn0wp='  + s0wn0wp]  = 1
    features['s0wpn0p='  + s0wpn0p]  = 1
    features['s0pn0wp='  + s0pn0wp]  = 1
    features['s0wn0w='   + s0wn0w]   = 1
    features['s0pn0p='   + s0pn0p]   = 1
    features['n0pn1p='   + n0pn1p]   = 1

    n0pn1pn2p  = ';'.join([n0p, n1p, n2p])
    s0pn0pn1p  = ';'.join([s0p, n0p, n1p])
    s0hps0pn0p = ';'.join([s0hp, s0p, n0p])
    s0ps0lpn0p = ';'.join([s0p, s0lp, n0p])
    s0ps0rpn0p = ';'.join([s0p, s0rp, n0p])
    s0pn0pn0lp = ';'.join([s0p, n0p, n0lp])

    # from three words
    features['n0pn1pn2p  =' + n0pn1pn2p ] = 1 
    features['s0pn0pn1p  =' + s0pn0pn1p ] = 1
    features['s0hps0pn0p =' + s0hps0pn0p] = 1
    features['s0ps0lpn0p =' + s0ps0lpn0p] = 1
    features['s0ps0rpn0p =' + s0ps0rpn0p] = 1
    features['s0pn0pn0lp =' + s0pn0pn0lp] = 1

    # unigrams
    features['s0hw=' + s0hw] = 1
    features['s0hp=' + s0hp] = 1
    features['s0lw=' + s0lw] = 1
    features['s0lp=' + s0lp] = 1
    features['s0rw=' + s0rw] = 1
    features['s0rp=' + s0rp] = 1
    features['n0lw=' + n0lw] = 1
    features['n0lp=' + n0lp] = 1
    
    # third order
    features['s0l2w=' + s0l2w] = 1
    features['s0l2p=' + s0l2p] = 1
    features['s0r2w=' + s0r2w] = 1
    features['s0r2p=' + s0r2p] = 1
    features['n0l2w=' + n0l2w] = 1
    features['n0l2p=' + n0l2p] = 1

    return features
