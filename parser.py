from collections import defaultdict

class SimpleParser:

    def __init__(self, arcsys, fex, oracle):
        self.weights = {}
        self.arcsys = arcsys
        self.fex = fex
        self.oracle = oracle

        self.current_update = 0
        self.previous_update = defaultdict(lambda: 0)
        self.weight_accumulate = defaultdict(lambda: 0)

    def score(self, features):
        scores = dict((label, 0) for label in self.arcsys.TRANSITIONS)
        for feature, value in features.items():
            if feature not in self.weights:
                continue
            for transition, weight in self.weights[feature].items():
                scores[transition] += weight * value
        return scores

    def average_weights(self):
        for feature in self.weights:
            for label in self.weights[feature]:
                total = self.weight_accumulate[(feature, label)]
                t_delta = self.current_update - self.previous_update[(feature, label)]
                total += t_delta * self.weights[feature][label]
                avg = total / float(self.current_update)
                self.weights[feature][label] = avg

    def update(self, true_label, pred_label, features):
        def update_label_feature(label, feature, value):
            if feature not in self.weights:
                self.weights[feature] = {}
            if label not in self.weights[feature]:
                self.weights[feature][label] = 0

            weight = self.weights[feature][label]
            t_delta = self.current_update - self.previous_update[(feature, label)]
            self.weight_accumulate[(feature, label)] += t_delta * weight
            self.previous_update[(feature, label)] = self.current_update
            self.weights[feature][label] += value

        self.current_update += 1
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
            zero_transitions = self.oracle(config, gold_config)
            true_transition = max(zero_transitions, key=lambda t: scores[t])
            if pred_transition not in zero_transitions:
                self.update(true_transition, pred_transition, features)
            else:
                correct_transitions += 1
            config = self.arcsys.take_transition(config, true_transition)
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
