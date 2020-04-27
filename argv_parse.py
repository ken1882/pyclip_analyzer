import _G
from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument("-s", "--sample", action="store_true", help="Process positive samples")
parser.add_argument("-i", "--vodid", type=int, help="Target vodid")

def init():
  args = parser.parse_args()
  _G.FLAG_SAMPLE_PROC = True if args.sample else False
  if args.vodid:
    _G.StreamFileIndex = args.vodid