from pathlib import Path
import sys
import yaml

from utils.file_utils import StaticFileTree


if __name__ == '__main__':
    helper_file = Path("./.files_list")
    sft = StaticFileTree(Path("./"), "*")
    sft.build()
    with open(helper_file, 'w') as file:
        yaml.dump({f"{f.resolve()}": t for f, t in sft.items}, file)

