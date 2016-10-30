from arc_system import *
from conll_util import *
from feature_extractor import *


if __name__ == '__main__':
    f = 'en.tr100'
    ss = read_conll_data(f)
    sentence = ss[100]
    print sentence
    print

    arcsys = ArcStandard()
    config = arcsys.get_initial_config(sentence)
    print config

    fx = baseline_fex(config)
    print fx
