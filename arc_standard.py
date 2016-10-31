import conll_util

WORD  = 0
POS   = 1
HEAD  = 2
LABEL = 3
ROOT  = -1

class Configuration:

    def __init__(self, root, buffer, sentence):
        self.arcs = []
        self.stack = [root]
        self.buffer = buffer
        self.sentence = sentence

    def __str__(self):
        ret = 'stack: ' + list(self.stack).__str__() + '\n'
        ret += 'buffer: ' + list(self.buffer).__str__() + '\n'
        ret += 'arcs: ' + self.arcs.__str__()
        return ret


class GoldConfiguration:

    def __init__(self):
        self.head_of = {}
        self.deps_of = {}
        self.arcs = set()


class ArcStandard:
    
    LEFT   = 0
    RIGHT  = 1
    SHIFT  = 2
    TRANSITIONS = [LEFT, RIGHT, SHIFT]
    TRANSITION_NAMES = ['LEFT', 'RIGHT', 'SHIFT']
    transition_funcs = {}

    def __init__(self):
        ArcStandard.transition_funcs[ArcStandard.LEFT] = ArcStandard.left_arc
        ArcStandard.transition_funcs[ArcStandard.RIGHT] = ArcStandard.right_arc
        ArcStandard.transition_funcs[ArcStandard.SHIFT] = ArcStandard.shift

    @staticmethod
    def get_initial_config(sentence):
        '''
        construct initial configuration from given sentence
        buffer is constructed with an extra root
        root is -1
        '''
        buffer = list(range(len(sentence)))
        return Configuration(ROOT, buffer, sentence)

    @staticmethod
    def get_gold_config(sentence):
        gold_config = GoldConfiguration()
        for i in xrange(len(sentence)):
            head = sentence[i][HEAD]
            gold_config.head_of[i] = head
            if head not in gold_config.deps_of:
                gold_config.deps_of[head] = []
            gold_config.deps_of[head].append(i)
            gold_config.arcs.add((head, i))
        return gold_config

    @staticmethod
    def is_finished(config):
        '''
        finish when buffer is empty 
        and only root is left in stack
        '''
        return len(config.buffer) == 0 and len(config.stack) == 1

    @staticmethod
    def is_not_projective(config):
        for d1 in config.head_of.keys():
            h1 = config.head_of[d1]
            for d2 in config.head_of.keys():
                h2 = config.head_of[d2]
                if h1 is ROOT or h2 is ROOT:
                    continue
                # h1 h2 d1 d2
                if h1 < h2 and h2 < d1 and d1 < d2:
                    return True
                # d1 h2 h1 d2
                if d1 < h2 and h2 < h1 and h1 < d2:
                    return True
                # h1 d2 d1 h2
                if h1 < d2 and d2 < d1 and d1 < h2:
                    return True
                # d1 d2 h1 h2
                if d1 < d2 and d2 < h1 and h1 < h2:
                    return True
        return False

    @staticmethod
    def get_legal_transitions(config):
        '''
        get the legal transitions in given configuration
        '''
        is_legal = [True for _ in ArcStandard.TRANSITIONS]

        if len(config.buffer) == 0:
            # buffer is empty, cannot do right_arc or shift
            is_legal[ArcStandard.LEFT] = False
            is_legal[ArcStandard.RIGHT] = False
            is_legal[ArcStandard.SHIFT] = False
        else:
            # precondition for right_arc: buffer_first is not root 
            # and does not already have a head
            buffer_first = config.buffer[0]

            if buffer_first is ROOT:
                is_legal[ArcStandard.RIGHT] = False

            if len([h for h, t in config.arcs if t == buffer_first]) > 0:
                is_legal[ArcStandard.RIGHT] = False


        if len(config.stack) == 0:
            # stack is empty, cannot do left_arc or right_arc
            is_legal[ArcStandard.LEFT] = False
            is_legal[ArcStandard.RIGHT] = False
        else:
            # precondition for left_arc: stack_top is not root 
            # and does not already have a head
            stack_top = config.stack[-1]

            if stack_top is ROOT:
                is_legal[ArcStandard.LEFT] = False

            if len([h for h, t in config.arcs if t == stack_top]) > 0:
                is_legal[ArcStandard.LEFT] = False

        legal_transitions = [trans for trans, legal in enumerate(is_legal)
                             if legal is True]
        return legal_transitions

    @staticmethod
    def left_arc(config):
        '''
        pop stack
        add (buffer_first, stack_top)
        '''
        s = config.stack.pop()
        b = config.buffer[0]
        config.arcs.append((b, s))
        return config
    
    @staticmethod
    def right_arc(config):
        '''
        move buffer_first to stack
        add (stack_top, buffer_first)
        '''
        s = config.stack.pop()
        b = config.buffer[0]
        del config.buffer[0]
        config.buffer.insert(0, s)
        config.arcs.append((s, b))
        return config

    @staticmethod
    def shift(config):
        ''' move buffer_first to stack '''
        b = config.buffer[0]
        del config.buffer[0]
        config.stack.append(b)
        return config
    
    @staticmethod
    def take_transition(config, transition):
        '''
        take the given transition on the given config
        return the new config
        '''
        assert transition in ArcStandard.TRANSITIONS
        return ArcStandard.transition_funcs[transition](config)

    @staticmethod
    def static_oracle(config, gold_config):
        if len(config.buffer) == 0:
            return None
        b = config.buffer[0]
        if len(config.stack) == 0:
            return ArcStandard.SHIFT
        s = config.stack[-1]
        if s is not ROOT and b == gold_config.head_of[s]:
            arcs = gold_config.arcs - set(config.arcs)
            if len([t for h, t in arcs if h == s]) == 0:
                return ArcStandard.LEFT
        if s == gold_config.head_of[b]:
            # to do a right arc (s, b), 
            # need to make sure b doesn' have head left
            arcs = gold_config.arcs - set(config.arcs)
            if len([t for h, t in arcs if h == b]) == 0:
                return ArcStandard.RIGHT
        return ArcStandard.SHIFT


if __name__ == '__main__':
    # sentence = "economic news had little effect on financial markets .".split()
    # arcsys = ArcStandard()
    # transitions = [2, 0, 2, 0, 2, 2, 0, 2, 2, 2, 0, 1, 1, 1, 2, 1, 1, 2]
    # config = arcsys.get_initial_config(sentence)
    # print config
    # 
    # for t in transitions:
    #     print arcsys.TRANSITION_NAMES[t]
    #     if t in arcsys.get_legal_transitions(config):
    #         config = arcsys.take_transition(config, t)
    #         print config
    #     else:
    #         print 'not legal'
    #     if arcsys.is_finished(config):
    #         print 'finished'
    #         break

    f = 'en.tr100'
    ss = conll_util.read_conll_data(f)
    sentence = ss[30]
    arcsys = ArcStandard()
    config = arcsys.get_initial_config(sentence)
    print config
    gold_config = arcsys.get_gold_config(sentence)
    gold_arcs = gold_config.arcs
    print gold_arcs
    print

    if not arcsys.is_not_projective(gold_config):
        while not arcsys.is_finished(config):
            action = arcsys.static_oracle(config, gold_config)
            print arcsys.TRANSITION_NAMES[action]
            config = arcsys.take_transition(config, action)
            print config
            print gold_arcs - set(config.arcs)
            print
    else:
        print 'not projective'
