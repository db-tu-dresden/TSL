#!/usr/bin/env python
import time

from generator.core.tsl_config import config, parse_args
import os
import sys
import json
from pathlib import Path

from generator.core.tsl_generator import TSLGenerator
from generator.utils.dict_utils import dict_update
from generator.utils.yaml_utils import yaml_load
from generator.utils.file_utils import remove_path

def get_config(config_path: Path) -> dict:
    return yaml_load(config_path)

def tsl_setup(file_config, additional_config=None) -> None:
    if additional_config is None:
        additional_config = dict()
    # overwrite / extend config file entries with additional config dict entries
    merged_config = dict_update(file_config, additional_config)
    config.setup(merged_config)


if __name__ == '__main__':
    st = time.time()
    os.chdir(Path(os.path.realpath(__file__)).parent)
    file_config = get_config(Path("generator/config/default_conf.yaml"))
    args_dict = parse_args(known_types = file_config["configuration"]["relevant_types"])
    tsl_setup(file_config, args_dict)

    gen = TSLGenerator()

    if config.get_config_entry("clean"):
        remove_path(config.generation_out_path)

    if config.get_config_entry("daemon"):
        try:
            while True:
                print("Ready", end='')
                sys.stdout.flush()
                for input in sys.stdin:
                    targetDict = {}
                    flags = None
                    primitives = []
                    try:
                        targetDict = json.loads(input)
                    except json.JSONDecodeError as err:
                        print(f"Wrong parameter: {err.msg}", file=sys.stderr, end='')
                        sys.stderr.flush()
                        continue
                    if "lscpu_flags" in targetDict:
                        flags = targetDict["lscpu_flags"]
                    if "primitives" in targetDict:
                        primitives = targetDict["primitives"]
                    remove_path(config.generation_out_path)
                    gen.generate(flags, primitives)
                    print("Done", end='')
                    sys.stdout.flush()
        except KeyboardInterrupt:
            sys.stdout.flush()
            exit(0)
    else:
        print(f"Generating for {args_dict['targets']}")
        gen.generate(args_dict["targets"])

    print("Generation needed %.2f seconds." % (time.time() - st))


