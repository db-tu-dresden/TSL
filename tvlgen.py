import argparse
import logging
from pathlib import Path

from core.tvlgenerator import TVLGenerator

def existing_path(path_str: str):
    p = Path(path_str)
    if not p.is_absolute():
        p = Path(".").joinpath(p)
    if p.exists():
        if not p.is_dir():
            raise argparse.ArgumentError(f"{p} is already present but not a directory.")
    else:
        p.mkdir(parents=True)
    # return str(p.resolve())
    return str(p)


if __name__ == '__main__':
    logging.basicConfig(#filename="tvlgen.log",
                        format='[%(asctime)s %(levelname)-8s %(name)s::%(decorated_funcName)s (%(decorated_filename)s)]: %(message)s',
                        datefmt='%d.%m.%Y %I:%M:%S %p',
                        level=logging.ERROR)

    parser = argparse.ArgumentParser(description="TVL Generator")
    parser.add_argument(
        '-o', '--outpath',
        default="./generated/",
        type=existing_path,
        help='Relative or absolut path where TVL should be generated into.',
        dest='outpath')
    parser.add_argument(
        '-c', '--configpath',
        default="./config/",
        type=existing_path,
        help='Relative or absolut path to generator config files.',
        dest='configpath')
    parser.add_argument(
        '-d', '--datapath',
        default="./primitive_data/",
        type=existing_path,
        help='Relative or absolut path where TVL primitive and extension files are located.',
        dest='datapath')
    parser.add_argument(
        '-t', '--targets',
        default=None,
        nargs='*',
        dest='targets'
    )
    args = parser.parse_args()
    generator = TVLGenerator(
        Path(args.outpath),
        Path(args.configpath).joinpath("data/templates"),
        Path(args.configpath).joinpath("data/tvl_generator_schema.yaml"),
        Path(args.datapath),
        Path(__file__).resolve().parent.joinpath("static_files")
    )
    generator.import_data()
    generator.create_generated_files(args.targets)
    generator.create_static_files()
    
