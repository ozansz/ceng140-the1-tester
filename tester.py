import os
import sys

EP = 1e-5

import testutils as util
from libtester import Tester

if __name__ == "__main__":
    if os.name != 'posix':
        util.warn("This program can only be run in Linux environment.")
        sys.exit(0)

    args = util.tr_parser.parse_args()

    if args.json:
        dataset = util.load_dataset(args.dataset, 'json')
    else:
        dataset = util.load_dataset(args.dataset, 'csv')

    tr = Tester(dataset=dataset, executable_path=args.executable, logger=util.test_logger)
    tr.start()
     