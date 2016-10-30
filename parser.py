from arc_standard import *
from conll_util import *
from feature_extractor import *

class Parser:

    def __init__(self, arcsys, fex):
        self.weights = {}
        self.arcsys = arcsys
        self.fex = fex

    def score(self, fv):
        scores = dict((t, 0) for t in self.arcsys.TRANSITIONS)
        for key, val in fv.items():
            if val == 0:
                continue
            if key not in self.weights:
                continue
            for transition, weight in self.weights[k].items():
                scores[transition] += weight * val
        return scores

    def update(self, true_transition, pred_transition, features):
        def update_label_feature(label, feature, value):
            if feature not in self.weights:
                self.weights[feature] = {}
            if label not in self.weights[feature]:
                self.weights[feature][label] = 0
            self.weights[feature][label] += value

        for feature, value in features.items():
            update_label_feature(true_transition, feature, value)
            update_label_feature(pred_transition, feature, -value)

    def train(self, sentence):
        config = self.arcsys.get_initial_config(sentence)
        gold_config = self.arcsys.get_gold_config(sentence)
        
        while not self.arcsys.is_finished(config):
            legal_transitions = self.arcsys.get_legal_transitions(config)
            features = self.fex(config)
            scores = self.score(features)
            pred_transition = max(legal_transitions, key=lambda p: scores[p])
            true_transition = self.arcsys.static_oracle(config, gold_config)
            if pred_transition is not true_transition:
                self.update(true_transition, pred_transition, features)
            config = self.arcsys.take_transition(config, true_transition)


if __name__ == '__main__':
    f = 'en.tr100'
    ss = read_conll_data(f)
    sentence = ss[100]

    arcsys = ArcStandard()
    config = arcsys.get_initial_config(sentence)
    print config

    gold_config = arcsys.get_gold_config(sentence)
    gg = gold_config.arcs
    print gg
    print

    while not arcsys.is_finished(config):
        action = arcsys.static_oracle(config, gold_config)
        print arcsys.TRANSITION_NAMES[action]
        config = arcsys.take_transition(config, action)
        print config
        print gg - set(config.arcs)
        print

    # parser = Parser(arcsys, baseline_fex)
    # parser.train(sentence)
