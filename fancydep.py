from arc_standard import ArcStandard
from arc_eager import ArcEager
from parser import SimpleParser
import feature_extractor as fx
from train import main

if __name__ == '__main__':
    arcsys = ArcEager()
    parser = SimpleParser(arcsys, fx.rich, arcsys.dynamic_oracle)
    main(arcsys, parser, True)
