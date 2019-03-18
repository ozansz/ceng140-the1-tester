import os
import sys

from libtester import TestDataset
import testutils as util

if __name__ == '__main__':
    if os.name != 'posix':
        util.warn("This program can only be run in Linux environment.")
        sys.exit(0)

    os.system("clear")

    args = util.dg_parser.parse_args()

    if args.gen_only and (args.spec_loan or args.spec_mc or args.spec_payment or args.spec_rate):
        util.dg_parser.error(message="Option --only cannot be used with --spec-* options")

    gen_labels = {
        "L": False,
        "n": False,
        "p": False,
        "r": False
    }

    if args.gen_only:
        gen_labels[args.gen_only] = True
    else:
        gen_labels["L"] = bool(args.spec_loan)
        gen_labels["n"] = bool(args.spec_mc)
        gen_labels["p"] = bool(args.spec_payment)
        gen_labels["r"] = bool(args.spec_rate)

    if not (args.gen_only or args.spec_loan or args.spec_mc or args.spec_payment or args.spec_rate):
        gen_labels = {
        "L": True,
        "n": True,
        "p": True,
        "r": True
    }

    td = TestDataset(labels=gen_labels, executable_path=args.executable, logging={
        "loggerfn": util.info,
        "logging_enabled": args.verbose
    })

    if args.samples is not None:
        td.set_sample_count(args.samples)

    td.generate()

    ext = "csv"
    if args.json:
        ext = "json"

    td.save(ext=ext)