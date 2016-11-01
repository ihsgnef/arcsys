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
    if len(deps):
        left = min(deps)
        right = max(deps)
        return sentence[left], sentence[right]
    return (NULL, NULL), (NULL, NULL)


def baseline_fex_0(config):
    sentence = sentence_to_dict(config.sentence)
    features = {}

    s0_word      = NULL # top stack word
    s0_pos       = NULL # top stack pos
    b0_word      = NULL # first buffer word
    b0_pos       = NULL # first buffer pos

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

def baseline_fex_1(config):
    sentence = sentence_to_dict(config.sentence)
    head_of = defaultdict(lambda : (NULL, NULL))
    for h, t in config.arcs:
        head_of[t] = h

    features = {}

    s0_word      = NULL # top stack word
    s0_pos       = NULL # top stack pos
    b0_word      = NULL # first buffer word
    b0_pos       = NULL # first buffer pos
    b1_word      = NULL # second buffer word
    b1_pos       = NULL # second buffer pos
    b2_word      = NULL # third buffer word
    b2_pos       = NULL # third buffer pos
    b0_head_pos  = NULL # pos of head of buffer first
    b0_left_pos  = NULL # pos of left-most dependent of buffer first
    b0_right_pos = NULL # pos of right-most dependent of buffer first
    s0_head_pos  = NULL # pos of head of stack top
    s0_left_pos  = NULL # pos of left-most dependent of stack top
    s0_right_pos = NULL # pos of right-most dependent of stack top

    if len(config.buffer) > 0:
        i = config.buffer[0]
        b0_word = sentence[i][WORD]
        b0_pos = sentence[i][POS]
        left_dep, right_dep = left_right_deps(config.arcs, i, sentence)
        b0_left_pos = left_dep[POS]
        b0_right_pos = right_dep[POS]
        b0_head_pos = head_of[i][POS]

    if len(config.buffer) > 1:
        i = config.buffer[1]
        b1_word = sentence[i][WORD]
        b1_pos = sentence[i][POS]

    if len(config.buffer) > 2:
        i = config.buffer[2]
        b2_word = sentence[i][WORD]
        b2_pos = sentence[i][POS]

    if len(config.stack) > 0:
        i = config.stack[-1]
        s0_word = sentence[i][WORD]
        s0_pos = sentence[i][POS]
        left_dep, right_dep = left_right_deps(config.arcs, i, sentence)
        s0_left_pos = left_dep[POS]
        s0_right_pos = right_dep[POS]
        s0_head_pos = head_of[i][POS]

    b0_word_b0_pos = b0_word + "+" + b0_pos
    b1_word_b1_pos = b1_word + "+" + b1_pos
    b2_word_b2_pos = b2_word + "+" + b2_pos
    b0_pos_b1_pos = b0_pos + "+" + b1_pos
    s0_word_b0_word = s0_word + "+" + b0_word
    s0_pos_b0_pos = s0_pos + "+" + b0_pos
    
    b0_pos_b1_pos_b2_pos = b0_pos + "+" + b1_pos + "+" + b2_pos
    s0_pos_b0_pos_b1_pos = s0_pos + "+" + b0_pos + "+" + b1_pos
    s0_head_pos_b0_pos_b1_pos = s0_head_pos + "+" + b0_pos + "+" + b1_pos
    s0_pos_s0_left_pos_b0_pos = s0_pos + "+" + s0_left_pos + "+" + b0_pos
    s0_pos_s0_right_pos_b0_pos = s0_pos + "" + s0_right_pos + "+" + b0_pos
    b0_pos_b0_left_pos_s0_pos = b0_pos + "+" + b0_left_pos + "+" + s0_pos
    b0_pos_b0_right_pos_s0_pos = b0_pos + "+" + b0_right_pos + "+" + s0_pos

    features['b0_word=' + b0_word] = 1
    features['b0_pos=' + b0_pos] = 1
    features['s0_word=' + s0_word] = 1
    features['s0_pos=' + s0_pos] = 1
    features['s0_word_b0_word=' + s0_word_b0_word] = 1
    features['s0_pos_b0_pos=' + s0_pos_b0_pos] = 1

    features['b1_word=' + b1_word] = 1
    features['b1_pos=' + b1_pos] = 1
    features['b2_word=' + b2_word] = 1
    features['b2_pos=' + b2_pos] = 1

    features['b0_word_b0_pos=' + b0_word_b0_pos] = 1
    features['b1_word_b1_pos=' + b1_word_b1_pos] = 1
    features['b2_word_b2_pos=' + b2_word_b2_pos] = 1
    features['b0_pos_b1_pos=' + b0_pos_b1_pos] = 1
    features['s0_word_b0_word=' + s0_word_b0_word] = 1
    # features['s0_pos_b0_pos=' + s0_pos_b0_pos] = 1

    features['b0_pos_b1_pos_b2_pos=' + b0_pos_b1_pos_b2_pos] = 1
    features['s0_pos_b0_pos_b1_pos=' + s0_pos_b0_pos_b1_pos] = 1
    features['s0_head_pos_b0_pos_b1_pos=' + s0_head_pos_b0_pos_b1_pos] = 1
    features['s0_pos_s0_left_pos_b0_pos=' + s0_pos_s0_left_pos_b0_pos] = 1
    features['s0_pos_s0_right_pos_b0_pos=' + s0_pos_s0_right_pos_b0_pos] = 1
    features['b0_pos_b0_left_pos_s0_pos=' + b0_pos_b0_left_pos_s0_pos] = 1
    features['b0_pos_b0_right_pos_s0_pos=' + b0_pos_b0_right_pos_s0_pos] = 1

    return features
