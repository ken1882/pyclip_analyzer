import _G
from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument("-s", "--sample", action="store_true", help="Process positive samples")
parser.add_argument("-i", "--vodid", type=int, help="Target vodid")
parser.add_argument("-r", "--retrain", action="store_true", help="Retrain exsiting model")
parser.add_argument("--host-name", help="Name of the host streamer")
parser.add_argument("-t", "--timestamp-start", type=int, help="Starting time in second when downloading stream")
parser.add_argument("-p", "--positive-label", help="Positive duration of target vod, format: `<start time in second>:<duration>`")
parser.add_argument("-c", "--clip-name", help="Name of the clip")
parser.add_argument("-y", "--yes", action="store_true", help="Auto enter Y when promopting")
parser.add_argument("-n", "--no", action="store_true", help="Auto enter N when promopting")
parser.add_argument("-f", "--full-process", action="store_true", help="Full vod processing")

def init():
  args = parser.parse_args()
  _G.FLAG_SAMPLE_PROC = True if args.sample else False
  if args.vodid:
    _G.StreamFileIndex = args.vodid
  if args.retrain:
    _G.FLAG_RETRAIN = True
  if args.host_name:
    _G.StreamFilePrefix = args.host_name
  if args.timestamp_start:
    _G.StartDownloadTimestamp = args.timestamp_start
  if args.positive_label:
    _G.PositiveLabelString = args.positive_label
  if args.clip_name:
    _G.ClipName = args.clip_name
  if args.yes:
    _G.FLAG_ALWAYS_YES = True
  if args.no:
    _G.FLAG_ALWAYS_NO = True
  
  if args.yes and args.no:
    print("Argument option -y(--yes) and -n(--no) conflicted!")
    exit()