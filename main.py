from core.tvl_config import config, parse_args

from pathlib import Path

from core.tvl_generator import TVLGenerator
from utils.dict_utils import dict_update
from utils.yaml_utils import yaml_load


def tvl_setup(config_path: Path, additional_config=None) -> None:
    if additional_config is None:
        additional_config = dict()
    config_file_cfg = yaml_load(config_path)
    # overwrite / extend config file entries with additional config dict entries

    config.setup(dict_update(config_file_cfg, additional_config))


if __name__ == '__main__':
    args_dict = parse_args()
    tvl_setup(Path("config/default_conf.yaml"), args_dict)
    gen = TVLGenerator()
    gen.generate(args_dict["targets"])
    # gen.generate(["sse", "sse2", "sse3", "ssse3", "sse4_1", "sse4_2", "avx", "avx2"])