WORD  = 0
POS   = 1
HEAD  = 2
LABEL = 3
ROOT_ID  = 0
ROOT = "ROOT"
NULL = "NULL"

def baseline_fex(config):
    '''
    identity of word at top of the stack
    identity of word at head of buffer
    coarse POS of word at top of the stack
    coarse POS of word at head of buffer
    pair of words at top of stack and head of buffer
    pair of coarse POS at top of stack and head of buffer
    '''
    fv = {}
    
    s0_word   = NULL
    b0_word   = NULL
    s0_pos    = NULL
    b0_pos    = NULL
    s0b0_word = (NULL, NULL)
    s0b0_pos  = (NULL, NULL)

    if len(config.stack) > 0:
        s0_id = config.stack[-1]
        if s0_id is not ROOT_ID:
            s0_id -= 1
            s0_word = config.sentence[s0_id][WORD]
            s0_pos  = config.sentence[s0_id][POS]
        else:
            s0_word = ROOT
            s0_pos  = ROOT

    if len(config.buffer) > 0:
        b0_id = config.buffer[0]
        if b0_id is not ROOT_ID:
            b0_id -= 1
            b0_word = config.sentence[b0_id][WORD]
            b0_pos  = config.sentence[b0_id][POS]
        else:
            b0_word = ROOT
            b0_pos  = ROOT

    s0b0_word = s0_word + '+' + b0_word
    s0b0_pos = s0_pos + '+' + b0_pos

    fv['s0_word=' + s0_word] = 1
    fv['b0_word=' + b0_word] = 1
    fv['s0_pos=' + s0_pos] = 1
    fv['b0_pos=' + b0_pos] = 1
    fv['s0b0_word=' + s0b0_word] = 1
    fv['s0b0_pos=' + s0b0_pos] = 1

    return fv
