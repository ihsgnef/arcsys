import argparse
import random

from arc_standard import ArcStandard
from arc_eager import ArcEager
from parser import SimpleParser
from feature_extractor import *
import util

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("train_file", nargs="?", type=str, default="en.tr100")
    parser.add_argument("test_file", nargs="?", type=str, default="en.dev")
    parser.add_argument("test_output", nargs="?", type=str, default="en.dev.out")
    parser.add_argument("-i", "--iters", type=int, default=20)
    parser.add_argument("-v", "--verbose", action='store_true', default=False)
    return parser.parse_args()

def print_result(sentence, arcs, outfile):
    head_of = dict()
    for h, t in arcs:
        if h >= 0:
            head_of[t] = h
    for i, word in enumerate(sentence):
        word = word[0]
        s = str(i+1) + '\t' + word + '\t_\t_\t_\t_\t'
        if i in head_of:
            s += str(head_of[i] + 1)
        else:
            s += '_'
        s += '\t_\t_\t_\n'
        outfile.write(s)
    outfile.write('\n')

if __name__ == '__main__':
    args = parse_args()
    train_set = util.read_conll_data(args.train_file)
    test_set = util.read_conll_data(args.test_file)

    arcsys = ArcEager()
    parser = SimpleParser(arcsys, rich_baseline)

    # training
    train_set, train_gold_configs = util.filter_non_projective(arcsys, train_set)
    for i in xrange(args.iters):
        idx = list(range(len(train_set)))
        random.shuffle(idx)
        train_set = [train_set[i] for i in idx]
        train_gold_configs = [train_gold_configs[i] for i in idx]
        total_transitions = 0.0
        correct_transitions = 0.0
        for sentence, gold_config in zip(train_set, train_gold_configs):
            t, c = parser.train(sentence, gold_config)
            total_transitions += t
            correct_transitions += c
        if args.verbose:
            print correct_transitions / total_transitions
    parser.average_weights()

    # testing
    test_out_file = open(args.test_output, 'w')
    for sentence in test_set:
        arcs = parser.predict(sentence)
        print_result(sentence, arcs, test_out_file)
