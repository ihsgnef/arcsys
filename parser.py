import random
import functools
from collections import defaultdict
from multiprocessing import Pool

random.seed(543)

class SimpleParser:

    def __init__(self, arcsys, fex, oracle):
        self.weights = dict()
        self.arcsys = arcsys
        self.fex = fex
        self.oracle = oracle
        self.exploring = False
        self.EXPLORE_P = 0.9
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

    def update_weights(self, label, pair):
        feature, value = pair
        if feature not in self.weights:
            self.weights[feature] = {}
        if label not in self.weights[feature]:
            self.weights[feature][label] = 0
        weight = self.weights[feature][label]
        t_delta = self.current_update - self.previous_update[(feature, label)]
        self.weight_accumulate[(feature, label)] += t_delta * weight
        self.previous_update[(feature, label)] = self.current_update
        self.weights[feature][label] += value

    def update(self, true_label, pred_label, features):
        self.current_update += 1
        for feature, value in features.items():
            self.update_weights(true_label, (feature, value))
            self.update_weights(pred_label, (feature, -value))

    def train(self, sentence, gold_config):
        config = self.arcsys.get_initial_config(sentence)
        total = 0
        correct = 0
        while not self.arcsys.is_finished(config):
            legal_transitions = self.arcsys.get_legal_transitions(config)
            if len(legal_transitions) == 0:
                break
            features = self.fex(config)
            scores = self.score(features)
            pred_transition = max(legal_transitions, key=lambda p: scores[p])
            zero_transitions = self.oracle(config, gold_config)
            true_transition = max(zero_transitions, key=lambda t: scores[t])
            if pred_transition not in zero_transitions:
                self.update(true_transition, pred_transition, features)
                if self.exploring:
                    config = self.explore(config, true_transition, pred_transition)
                else:
                    config = self.arcsys.take_transition(config, true_transition)
            else:
                correct += 1
                config = self.arcsys.take_transition(config, true_transition)
            total += 1
        return total, correct
    
    def explore(self, config, true_transition, pred_transition):
        if random.random() < self.EXPLORE_P:
            return self.arcsys.take_transition(config, pred_transition)
        else:
            return self.arcsys.take_transition(config, true_transition)
    
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
