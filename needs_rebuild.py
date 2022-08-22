from pathlib import Path
import sys
import yaml

from utils.file_utils import StaticFileTree

if __name__ == '__main__':
    helper_file = Path("./.files_list")
    if helper_file.is_file():
        with open(helper_file.resolve(), "r") as fl:
            files_with_timestamps = yaml.safe_load(fl)
        sft = StaticFileTree(Path("./"))
        sft.build()
        for file, time_stamp in sft.items:
            if file.resolve() not in files_with_timestamps:
                sys.exit(0)
            if time_stamp > files_with_timestamps[file]:
                sys.exit(0)
        sys.exit(1)
    else:
        sys.exit(0)