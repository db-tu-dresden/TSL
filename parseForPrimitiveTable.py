from pathlib import Path

from generator.utils.yaml_utils import yaml_load
from generator.utils.yaml_utils import yaml_load_all

def get_config(config_path: Path) -> dict:
    return yaml_load(config_path)

def get_functor_name( yaml_thingy: any ) -> str:
    return yaml_thingy["functor_name"] if "functor_name" in yaml_thingy else yaml_thingy["primitive_name"]

class PrintablePrimitive:
    def __init__(self, name, ctype_to_extension_dict ) -> None:
        self.name = name
        self.ctype_to_extension_dict = ctype_to_extension_dict
        pass

    def __repr__(self) -> str:
        return f"{self.name}: {self.ctype_to_extension_dict}"

primitive_config = get_config(Path("generator/config/default_conf.yaml"))["configuration_files"]
for file in Path(primitive_config["primitive_data"]["root_path"] + "/" + primitive_config["primitive_data"]["primitives_path"] ).rglob("*.yaml"):
    print(file)
    yaml_contents = yaml_load_all(file)
    for doc in yaml_contents:
        if "primitive_name" in doc:
            ctype_ext_dict = dict()
            for definition in doc["definitions"]:
                ext = definition["target_extension"]
                for ctype in definition["ctype"]:
                    if ctype not in ctype_ext_dict:
                        ctype_ext_dict[ctype] = []
                    if ext not in ctype_ext_dict[ctype]:
                        ctype_ext_dict[ctype].append(definition["target_extension"])
            pP = PrintablePrimitive(get_functor_name( doc ), ctype_ext_dict)
            print( f"\t{pP}" )
