from transparser import main
from arc_eager import ArcEager
from parser import SimpleParser
import feature_extractor as fx

if __name__ == '__main__':
    arcsys = ArcEager()
    parser = SimpleParser(arcsys, fx.rich_baseline, arcsys.dynamic_oracle)
    main(arcsys, parser)
