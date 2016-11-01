import random
from collections import defaultdict
from arc_standard import *
from conll_util import *
from feature_extractor import *

class Parser:

    def __init__(self, arcsys, fex):
        self.weights = {}
        self.arcsys = arcsys
        self.fex = fex

        self.train_tick = 0
        self.train_last_tick = defaultdict(lambda: 0)
        self.train_totals = defaultdict(lambda: 0)

    def score(self, features):
        scores = dict((label, 0) for label in self.arcsys.TRANSITIONS)
        for feature, value in features.items():
            if feature not in self.weights:
                continue
            for transition, weight in self.weights[feature].items():
                scores[transition] += weight * value
        return scores

    def avg_weights(self):
        for fj in self.weights:
            for label in self.weights[fj]:
                total = self.train_totals[(fj, label)]
                t_delt = self.train_tick - self.train_last_tick[(fj, label)]
                total += t_delt * self.weights[fj][label]
                avg = round(total / float(self.train_tick))
                if avg:
                    self.weights[fj][label] = avg

    def update(self, true_label, pred_label, features):
        def update_label_feature(label, feature, value):
            if feature not in self.weights:
                self.weights[feature] = {}
            if label not in self.weights[feature]:
                self.weights[feature][label] = 0

            wv = self.weights[feature][label]

            self.weights[feature][label] += value
            t_delt = self.train_tick - self.train_last_tick[(feature, label)]
            self.train_totals[(feature, label)] += t_delt * wv
            self.train_last_tick[(feature, label)] = self.train_tick

        for feature, value in features.items():
            update_label_feature(true_label, feature, value)
            update_label_feature(pred_label, feature, -value)

    def train(self, sentence, gold_config):
        config = self.arcsys.get_initial_config(sentence)
        # gold_config = self.arcsys.get_gold_config(sentence)
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
            else:
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
    
    def predict(self, sentence):
        config = self.arcsys.get_initial_config(sentence)
        while not self.arcsys.is_finished(config):
            legal_transitions = self.arcsys.get_legal_transitions(config)
            if len(legal_transitions) == 0:
                break
            features = self.fex(config)
            scores = self.score(features)
            pred_transition = max(legal_transitions, key=lambda p: scores[p])
            config = self.arcsys.take_transition(config, pred_transition)
        return config.arcs


def filter_non_projective(arcsys, sentences):
    gold_configs = []
    projective = []
    for sentence in sentences:
        gold_config = arcsys.get_gold_config(sentence)
        if not arcsys.is_not_projective(gold_config):
            gold_configs.append(gold_config)
            projective.append(sentence)
    return projective, gold_configs

if __name__ == '__main__':
    train_set = read_conll_data('en.tr100')
    valid_set = read_conll_data('en.dev')
    arcsys = ArcStandard()
    parser = Parser(arcsys, baseline_fex_1)

    train_set, train_gold_configs = filter_non_projective(arcsys, train_set)
    valid_set, valid_gold_configs = filter_non_projective(arcsys, valid_set)
    for i in xrange(20):
        tt = 0
        cc = 0
        idx = list(range(len(train_set)))
        random.shuffle(idx)
        train_set = [train_set[i] for i in idx]
        train_gold_configs = [train_gold_configs[i] for i in idx]
        for sentence, gold_config in zip(train_set, train_gold_configs):
            t, c = parser.train(sentence, gold_config)
            tt += t
            cc += c
        print tt, cc, cc * 1.0 / tt

    # parser.avg_weights()
    tt = 0
    cc = 0
    for sentence, gold_config in zip(valid_set, valid_gold_configs):
        arcs = parser.predict(sentence)
        correct_arcs = gold_config.arcs.intersection(set(arcs))
        tt += len(gold_config.arcs)
        cc += len(correct_arcs)
    print tt, cc, cc * 1.0 / tt
