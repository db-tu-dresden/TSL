import time

from core.tvl_config import config, parse_args
import sys, os
from pathlib import Path

from core.tvl_generator import TVLGenerator
from expansions.tvl_readme_md import create_readme
from utils.dict_utils import dict_update
from utils.yaml_utils import yaml_load

def get_config(config_path: Path) -> dict:
    return yaml_load(config_path)

def tvl_setup(file_config, additional_config=None) -> None:
    if additional_config is None:
        additional_config = dict()
    # overwrite / extend config file entries with additional config dict entries
    merged_config = dict_update(file_config, additional_config)
    config.setup(merged_config)


if __name__ == '__main__':
    st = time.time()
    os.chdir(Path(os.path.realpath(__file__)).parent)
    file_config = get_config(Path("config/default_conf.yaml"))
    args_dict = parse_args(known_types = file_config["configuration"]["relevant_types"])
    tvl_setup(file_config, args_dict)
    gen = TVLGenerator()
    gen.generate(args_dict["targets"])


    print("----%.2f----" % (time.time() - st))

