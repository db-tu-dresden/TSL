from pathlib import Path
import sys
import yaml

from utils.file_utils import StaticFileTree


if __name__ == '__main__':
    lib_path = Path(sys.argv[1])
    build_path = Path("./")
    helper_file = build_path.joinpath(".files_list")
    sft = StaticFileTree(lib_path, "*.yaml|*.template|*.py")
    sft.build()
    with open(helper_file, 'w') as file:
        yaml.dump({f"{f.resolve()}": t for f, t in sft.items}, file)

