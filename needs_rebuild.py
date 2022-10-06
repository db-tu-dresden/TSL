from pathlib import Path
import sys
import yaml

from utils.file_utils import StaticFileTree

if __name__ == '__main__':
    lib_path = Path(sys.argv[1])
    build_path = Path("./")
    helper_file = build_path.joinpath(".files_list")

    print(f"Checking for file {str(helper_file.resolve())}... ", end="")
    if helper_file.is_file():
        print("Exists.")
        with open(helper_file.resolve(), "r") as fl:
            files_with_timestamps = yaml.safe_load(fl)
        print(f"Scanning library path {str(lib_path)}... ")
        sft = StaticFileTree(lib_path, "*.yaml|*.template|*.py")
        sft.build()
        needs_rebuild = False
        for file, time_stamp in sft.items:
            fname: str = str(file.resolve())
            if fname not in files_with_timestamps:
                print(f"New file detected ({file}).")
                needs_rebuild = True
            elif time_stamp > files_with_timestamps[fname]:
                print(f"Updated file detected ({file}).")
                needs_rebuild = True
        print("done.")
        if needs_rebuild:
            sys.exit(0)
        else:
            sys.exit(1)
    else:
        print("Doesn't exist.")
        sys.exit(0)