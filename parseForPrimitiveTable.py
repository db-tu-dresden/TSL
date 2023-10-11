from pathlib import Path
import copy

from generator.utils.yaml_utils import yaml_load
from generator.utils.yaml_utils import yaml_load_all

class PrintablePrimitive:
    def __init__(self, name: any, ctype_to_extension_dict: dict ) -> None:
        self.name = name
        self.ctype_to_extension_dict = ctype_to_extension_dict
        pass

    def __repr__(self) -> str:
        return f"{self.name}: {self.ctype_to_extension_dict}"
    
    def to_html(self, considered_types: list, considered_exts: list) -> str:
        primitive_button = f"""<div class="primitiveContainer"><div class="primitive"><button id ="{self.name}_link" onclick="togglePrimitive(event, '{self.name}')">{self.name}</button></div>"""
        primitive_table_start = f"""<div id="{self.name}" class="primitiveinfo"><center><table border=1 cellpadding=10 cellspacing=0>"""
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
        print(f"My HTML: {html}")
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

html_start = """<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
body {font-family: Arial;}

.checkmark {
      display: inline-block;
      transform: rotate(45deg);
      height: 12px;
      width: 5px;
      border-bottom: 6px solid #78b13f;
      border-right: 5px solid #78b13f;
}

.dot_yes {
  height: 25px;
  width: 25px;
  background-color: rgb(51, 208, 51);
  border-radius: 50%;
  display: inline-block;
}

.dot_no {
  height: 25px;
  width: 25px;
  background-color: rgb(187, 40, 40);
  border-radius: 50%;
  display: inline-block;
}

.avail {
  color: rgb(51, 208, 51);
  font-weight: bolder;
  font-size: 20pt;
}

.no_avail {
  color: rgb(187, 40, 40);
  font-weight: bold;
  font-size: 20pt;
}

/* Style the tab */
.primitive {
  overflow: hidden;
  border: 1px dashed #ccc;
  background-color: #f1f1f1;
}

/* Style the buttons inside the tab */
.primitive button {
  background-color: inherit;
  float: left;
  border: none;
  outline: none;
  cursor: pointer;
  padding: 14px 16px;
  transition: 0.3s;
  font-size: 17px;
  width: 100%;
}

/* Change background color of buttons on hover */
.primitive button:hover {
  background-color: #ddd;
}

/* Create an active/current tablink class */
.primitive button.active {
  background-color: #ccc;
}

/* Style the tab content */
.primitiveinfo {
  display: none;
  padding: 14px 16px;
  border: 1px solid #ccc;
}
</style>

</head>
<body>
<input type="text" id="primitiveFilterInput" onkeyup="filterPrimitives()" placeholder="Search primitives"><br/>"""
html_end = """<script>
	function togglePrimitive(evt, primName) {
      if ( document.getElementById(primName).style.display == "block" ) {
        button = document.getElementById(primName + "_link" );
        button.className = button.className.replace(" active", "");
        document.getElementById(primName).style.display = "none";
      } else {
        document.getElementById(primName).style.display = "block";
        evt.currentTarget.className += " active";
      }
    }

    function filterPrimitives() {
      var input, filterPredicate, primContainer;
      input = document.getElementById('primitiveFilterInput');
      filterPredicate = input.value.toUpperCase();
      primContainer = document.getElementsByClassName("primitiveContainer");

      // Loop through all list items, and hide those who don't match the search query
      for (var i = 0; i < primContainer.length; i++) {
        var primitive = primContainer[i].getElementsByTagName("button")[0];
        txtValue = primitive.textContent;
        console.log(txtValue);
        if (txtValue.toUpperCase().indexOf(filterPredicate) > -1) {
          primContainer[i].style.display = "";
        } else {
          primContainer[i].style.display = "none";
        }
      }
    }
</script>
   
</body>
</html> 
"""

tsl_config = get_config(Path("generator/config/default_conf.yaml"))
primitive_config = tsl_config["configuration_files"]["primitive_data"]

all_types = extract_types( tsl_config )
all_extensions = extract_extensions( primitive_config["root_path"] + "/" + primitive_config["extensions_path"] )

all_extensions.sort()

print(all_types)
print(all_extensions)

raw_primitive_dict = prepare_primitive_dict( all_types )

table_vis_file = open( "primitives_table.html", 'w')
table_vis_file.write(html_start)

for file in Path(primitive_config["root_path"] + "/" + primitive_config["primitives_path"] ).rglob("*.yaml"):
    print(file)
    yaml_contents = yaml_load_all(file)
    for doc in yaml_contents:
        if "primitive_name" in doc:
            print(f" --- Now processing: {doc['primitive_name']}")
            ctype_ext_dict = copy.deepcopy(raw_primitive_dict)
            for definition in doc["definitions"]:
                exts = make_list_if_necessary(definition["target_extension"])
                ctypes = make_list_if_necessary(definition["ctype"])
                
                for ctype in ctypes:
                    for ext in exts:
                        ctype_ext_dict[ctype].add(ext)

            pP = PrintablePrimitive(get_functor_name( doc ), ctype_ext_dict)
            print( f"\t{pP}" )
            table_vis_file.write(pP.to_html( all_types, all_extensions ))
    break

table_vis_file.write(html_end)
table_vis_file.close()