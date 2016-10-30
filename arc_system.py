from collections import deque

class Configuration:

    def __init__(self, root, buffer, sentence):
        self.arcs = []
        self.stack = deque([root])
        self.buffer = deque(buffer)
        self.sentence = sentence

    def __str__(self):
        ret = 'stack: ' + list(self.stack).__str__() + '\n'
        ret += 'buffer: ' + list(self.buffer).__str__() + '\n'
        ret += 'arcs: ' + self.arcs.__str__() + '\n'
        return ret


class ArcStandard:
    
    ROOT   = 0
    LEFT   = 0
    RIGHT  = 1
    SHIFT  = 2
    TRANSITIONS = [LEFT, RIGHT, SHIFT]
    TRANSITION_NAMES = ['LEFT', 'RIGHT', 'SHIFT']

    def __init__(self):
        self.transition_funcs = {}
        self.transition_funcs[ArcStandard.LEFT] = ArcStandard.left_arc
        self.transition_funcs[ArcStandard.RIGHT] = ArcStandard.right_arc
        self.transition_funcs[ArcStandard.SHIFT] = ArcStandard.shift

    @staticmethod
    def get_initial_config(sentence):
        '''
        construct initial configuration from given sentence
        buffer is constructed with an extra root
        root is zero
        '''
        buffer = list(range(1, len(sentence) + 1))
        return Configuration(ArcStandard.ROOT, buffer, sentence)

    @staticmethod
    def is_finished(config):
        '''
        finish when buffer is empty
        '''
        return len(config.buffer) == 0

    @staticmethod
    def get_legal_transitions(config):
        '''
        get the legal transitions in given configuration
        '''
        is_legal = [True for _ in ArcStandard.TRANSITIONS]

        if len(config.buffer) == 0:
            # buffer is empty, cannot do right_arc or shift
            is_legal[ArcStandard.RIGHT] = False
            is_legal[ArcStandard.SHIFT] = False
        else:
            # precondition for right_arc: buffer_first is not root 
            # and does not already have a head
            buffer_first = config.buffer[0]

            if buffer_first is ArcStandard.ROOT:
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

            if stack_top is ArcStandard.ROOT:
                is_legal[ArcStandard.LEFT] = False

            if len([h for h, t in config.arcs if t == stack_top]) > 0:
                is_legal[ArcStandard.LEFT] = False

        legal_transitions = [trans for trans, legal in enumerate(is_legal)
                             if legal is True]
        return legal_transitions

    def take_transition(self, transition, config):
        '''
        take the given transition on the given config
        return the new config
        '''
        assert transition in ArcStandard.TRANSITIONS
        return self.transition_funcs[transition](config)

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
        config.buffer.appendleft(s)
        config.arcs.append((s, b))
        return config

    @staticmethod
    def shift(config):
        ''' move buffer_first to stack '''
        b = config.buffer[0]
        del config.buffer[0]
        config.stack.append(b)
        return config

class ArcEager:
    
    ROOT   = 0
    LEFT   = 0
    RIGHT  = 1
    SHIFT  = 2
    REDUCE = 3
    TRANSITIONS = [LEFT, RIGHT, SHIFT, REDUCE]
    TRANSITION_NAMES = ['LEFT', 'RIGHT', 'SHIFT', 'REDUCE']

    def __init__(self):
        self.transition_funcs = {}
        self.transition_funcs[ArcEager.LEFT] = ArcEager.left_arc
        self.transition_funcs[ArcEager.RIGHT] = ArcEager.right_arc
        self.transition_funcs[ArcEager.SHIFT] = ArcEager.shift
        self.transition_funcs[ArcEager.REDUCE] = ArcEager.reduce

    @staticmethod
    def get_initial_config(sentence):
        '''
        construct initial configuration from given sentence
        buffer is constructed with an extra root
        root is zero
        '''
        buffer = list(range(1, len(sentence) + 1))
        return Configuration(ArcEager.ROOT, buffer, sentence)

    @staticmethod
    def is_finished(config):
        '''
        finish when buffer is empty
        '''
        return len(config.buffer) == 0

    @staticmethod
    def get_legal_transitions(config):
        '''
        get the legal transitions in given configuration
        '''
        is_legal = [True for _ in ArcEager.TRANSITIONS]

        if len(config.buffer) == 0:
            # buffer is empty, cannot do right_arc or shift
            is_legal[ArcEager.RIGHT] = False
            is_legal[ArcEager.SHIFT] = False
        else:
            # precondition for right_arc: buffer_first is not root 
            # and does not already have a head
            buffer_first = config.buffer[0]

            if buffer_first is ArcEager.ROOT:
                is_legal[ArcEager.RIGHT] = False

            if len([h for h, t in config.arcs if t == buffer_first]) > 0:
                is_legal[ArcEager.RIGHT] = False

        if len(config.stack) == 0:
            # stack is empty, cannot do left_arc or right_arc
            is_legal[ArcEager.LEFT] = False
            is_legal[ArcEager.RIGHT] = False
            is_legal[ArcEager.REDUCE] = False
        else:
            # precondition for left_arc: stack_top is not root 
            # and does not already have a head
            stack_top = config.stack[-1]

            if stack_top is ArcEager.ROOT:
                is_legal[ArcEager.LEFT] = False

            if len([h for h, t in config.arcs if t == stack_top]) > 0:
                is_legal[ArcEager.LEFT] = False
            else:
                is_legal[ArcEager.REDUCE] = False

        legal_transitions = [trans for trans, legal in enumerate(is_legal)
                             if legal is True]
        return legal_transitions

    def take_transition(self, transition, config):
        '''
        take the given transition on the given config
        return the new config
        '''
        assert transition in ArcEager.TRANSITIONS
        return self.transition_funcs[transition](config)

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
        s = config.stack[-1]
        b = config.buffer[0]
        del config.buffer[0]
        config.stack.append(b)
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
    def reduce(config):
        ''' pop stack '''
        config.stack.pop()
        return config


if __name__ == '__main__':
    sentence = "economic news had little effect on financial markets .".split()
    arcsys = ArcStandard()
    transitions = [2, 0, 2, 0, 2, 2, 0, 2, 2, 2, 0, 1, 1, 1, 2, 1, 1, 2]
    # arcsys = ArcEager()
    # transitions = [2, 0, 2, 0, 1, 2, 0, 1, 1, 2, 0, 1, 3, 3, 3, 1]
    config = arcsys.get_initial_config(sentence)
    print config
    
    for t in transitions:
        print arcsys.TRANSITION_NAMES[t]
        if t in arcsys.get_legal_transitions(config):
            config = arcsys.take_transition(t, config)
            print config
        else:
            print 'not legal'
        if arcsys.is_finished(config):
            print 'finished'
            break
