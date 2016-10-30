from arc_standard import *
from conll_util import *
from feature_extractor import *

class Parser:

    def __init__(self, arcsys, fex):
        self.weights = {}
        self.arcsys = arcsys
        self.fex = fex

    def score(self, features):
        scores = dict((t, 0) for t in self.arcsys.TRANSITIONS)
        for feature, value in features.items():
            if feature not in self.weights:
                continue
            for transition, weight in self.weights[feature].items():
                scores[transition] += weight * value
        return scores

    def update(self, true_label, pred_label, features):
        def update_label_feature(label, feature, value):
            if feature not in self.weights:
                self.weights[feature] = {}
            if label not in self.weights[feature]:
                self.weights[feature][label] = 0
            self.weights[feature][label] += value

        for feature, value in features.items():
            update_label_feature(true_label, feature, value)
            update_label_feature(pred_label, feature, -value)

    def train(self, sentence):
        config = self.arcsys.get_initial_config(sentence)
        gold_config = self.arcsys.get_gold_config(sentence)
        total_transitions = 0
        correct_transitions = 0
        
        while not self.arcsys.is_finished(config):
            legal_transitions = self.arcsys.get_legal_transitions(config)
            features = self.fex(config)
            scores = self.score(features)
            pred_transition = max(legal_transitions, key=lambda p: scores[p])
            true_transition = self.arcsys.static_oracle(config, gold_config)
            if pred_transition is not true_transition:
                self.update(true_transition, pred_transition, features)
                correct_transitions += 1
            try:
                config = self.arcsys.take_transition(config, true_transition)
            except AssertionError:
                print '***************'
                print config
                print
                print gold_config.arcs - set(config.arcs)
                print '***************'
                break
            total_transitions += 1
        return total_transitions, correct_transitions


if __name__ == '__main__':
    f = 'en.tr100'
    ss = read_conll_data(f)
    arcsys = ArcStandard()

    parser = Parser(arcsys, baseline_fex)
    for i in xrange(10):
        tt = 0
        cc = 0
        for i, sentence in enumerate(ss):
            gold_config = arcsys.get_gold_config(sentence)
            if arcsys.is_not_projective(gold_config):
                continue
            t, c = parser.train(sentence)
            tt += t
            cc += c
        print tt, cc
