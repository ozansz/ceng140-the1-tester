import argparse
import json
import sys

dg_parser = argparse.ArgumentParser(description="THE1 Unofficial Data Generator",
    epilog="Created with ❤️  by Ozan Sazak")
dg_parser.add_argument("-v", "--verbose", action="store_true", help="Improve verbosity")
dg_parser.add_argument("-sL", "--spec-loan", action="store_true", help="Generate data for unknown loan")
dg_parser.add_argument("-sn", "--spec-mc", action="store_true", help="Generate data for unknown month count")
dg_parser.add_argument("-sp", "--spec-payment", action="store_true", help="Generate data for unknown payment")
dg_parser.add_argument("-sr", "--spec-rate", action="store_true", help="Generate data for unknown rate")
dg_parser.add_argument("--gen-only", choices=["L", "n", "p", "r"], help="Generate data for ONLY specified label")
dg_parser.add_argument("--json", action="store_true", help="Save dataset as Json file")
dg_parser.add_argument("--csv", action="store_true", default=True, help="Save dataset as CSV file (default)")
dg_parser.add_argument("-sc", "--samples", help="Sample count per test label")
dg_parser.add_argument("executable", help="THE1 program executable", type=str)

tr_parser = argparse.ArgumentParser(description="THE1 Unofficial Tester",
    epilog="Created with ❤️  by Ozan Sazak")
ext = tr_parser.add_mutually_exclusive_group()
ext.add_argument("--json", action="store_true", help="JSON dataset")
ext.add_argument("--csv", action="store_true", help="CSV dataset (default)", default=True)
tr_parser.add_argument("dataset", help="Test dataset")
tr_parser.add_argument("executable", help="THE1 program executable")

def warn(msg):
    print("[!]", msg)

def info(msg, sender=None, message_depth=1):
    if sender is not None:
        print("[%s]:" % sender, msg)
    else:
        if message_depth not in [1, None]:
            print("  " * (message_depth-1) + "==>", msg)
        else:
            print("[+]", msg)

def test_logger(test_id, result, msg=None):
    print("[+] Test #{}    = {} =".format(test_id, result))
    if msg:
        print("    ==>", msg)

def load_dataset(path, dtype='csv'):
    if dtype == "json":
        with open(path, "r") as fp:
            data = json.load(fp)
        return data
    elif dtype == "csv":
        data = dict()
        with open(path, "r") as fp:
            fp.readline()
            for line in fp.readlines():
                atoms = list(map(float, line[:-1].split(",")))
                data[int(atoms[0])] = {
                    "label": atoms[1],
                    "d1": atoms[2],
                    "d2": atoms[3],
                    "d3": atoms[4],
                    "output": atoms[5]
                }
        return data
    else:
        print("[ERROR] Unknown dataset type:", dtype)
        sys.exit(1)