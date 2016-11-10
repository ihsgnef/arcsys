from transparser import main
from arc_eager import ArcEager
from parser import SimpleParser
from feature_extractor import *

if __name__ == '__main__':
    arcsys = ArcEager()
    parser = SimpleParser(arcsys, rich_baseline, arcsys.dynamic_oracle)
    main(arcsys, parser)
