from pathlib import Path
import copy

from generator.utils.yaml_utils import yaml_load
from generator.utils.yaml_utils import yaml_load_all

class PrintablePrimitive:
    def __init__(self, name: str, description: str, ctype_to_extension_dict: dict ) -> None:
        self.name = name
        self.description = description
        self.ctype_to_extension_dict = ctype_to_extension_dict
        pass

    def __repr__(self) -> str:
        return f"{self.name}: {self.ctype_to_extension_dict}"
    
    def to_html(self, considered_types: list, considered_exts: list) -> str:
        primitive_button = f"""<div class="primitiveContainer"><div class="primitive"><button id ="{self.name}_link" onclick="togglePrimitive(event, '{self.name}')">{self.name}</button></div>"""
        primitive_table_start = f"""<div id="{self.name}" class="primitiveinfo"><p>Brief: <span class="description">{self.description}</span></p><center><table border=1 cellpadding=10 cellspacing=0>"""
        primitive_table_end = """</table></center></div><br/></div>"""
        
        top_left_corner = """<td style="border-top:0;border-left:0;"></td>"""
        ext_avail = """<td><div class="avail">+</div></td>"""
        ext_not_avail = """<td><div class="no_avail">-</div></td>"""

        rows = []
        header = """<tr align="center">""" + top_left_corner
        for ext in considered_exts:
            header += f"""<td>{ext}</td>"""
        header += """<tr>"""
        rows.append(header)

        for ctype in considered_types:
            row = f"""<tr align="center"><td>{ctype}</td>"""
            for ext in considered_exts:
                if ext in self.ctype_to_extension_dict[ctype]:
                    row += ext_avail
                else:
                    row += ext_not_avail
            row += """</tr>"""
            rows.append(row)

        html = primitive_button + primitive_table_start + "".join(rows) + primitive_table_end
        return html

def get_config(config_path: Path) -> dict:
    return yaml_load(config_path)

def get_functor_name( yaml_thingy: any ) -> str:
    return yaml_thingy["functor_name"] if "functor_name" in yaml_thingy else yaml_thingy["primitive_name"]

def extract_types( config ):
    return config["configuration"]["relevant_types"]

def extract_extensions( path_string: str ) -> list:
    exts = []
    for file in Path( path_string ).rglob("*.yaml"):
        yaml_contents = yaml_load(file)
        exts.append( yaml_contents["extension_name"] )
    return exts

def prepare_primitive_dict( all_types: list ) -> dict:
    raw_type_dict = dict()
    for type in all_types:
        raw_type_dict[type] = set()
    return raw_type_dict

def make_list_if_necessary( var: any ) -> list: 
    if not isinstance( var, list ):
        return [var]
    return var

def add_checkbox( name: str ) -> str:
    return f"""<input class="primitiveClassSelector" type="checkbox" value="{name}" id="checkbox_{name}" onclick="filterByCheckbox();"><label for="checkbox_{name}">{name}</label><br>"""


tsl_config = get_config(Path("generator/config/default_conf.yaml"))
primitive_config = tsl_config["configuration_files"]["primitive_data"]
html_template_path = tsl_config["configuration"]["expansions"]["primitive_vis"]["template_path"]

all_types = extract_types( tsl_config )
all_extensions = extract_extensions( primitive_config["root_path"] + "/" + primitive_config["extensions_path"] )
all_extensions.sort()

html_content = ""
with open(html_template_path, 'r') as template:
    html_content = template.read()

raw_primitive_dict = prepare_primitive_dict( all_types )
table_vis_file = open( "primitives_table.html", 'w')
checkbox_html = ""
primitive_html = ""
for file in Path(primitive_config["root_path"] + "/" + primitive_config["primitives_path"] ).rglob("*.yaml"):
    checkbox_html += add_checkbox(file.stem)
    yaml_contents = yaml_load_all(file)
    primitive_html += f"""<div class="primitiveCategory" id="{file.stem}">"""
    for doc in yaml_contents:
        if "primitive_name" in doc:
            descr = doc["brief_description"] if "brief_description" in doc else ""
            ctype_ext_dict = copy.deepcopy(raw_primitive_dict)
            for definition in doc["definitions"]:
                exts = make_list_if_necessary(definition["target_extension"])
                ctypes = make_list_if_necessary(definition["ctype"])
                
                for ctype in ctypes:
                    for ext in exts:
                        ctype_ext_dict[ctype].add(ext)

            pP = PrintablePrimitive(get_functor_name( doc ), descr, ctype_ext_dict)
            primitive_html += pP.to_html( all_types, all_extensions )
    primitive_html += f"""</div>"""

html_content = html_content.replace("---filterBoxes---",checkbox_html)
html_content = html_content.replace("---content---",primitive_html)

table_vis_file.write(html_content)
table_vis_file.close()