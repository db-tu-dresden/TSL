import argparse
import json
from typing import Any, Dict, List, Generator
from itertools import combinations
from pathlib import Path

def flags_str_to_list(flags_str: str) -> List[str]:
  return sorted([flag.strip() for flag in flags_str.split(' ')])

def list_to_str(flags: List[str]) -> str:
  return ' '.join(sorted(flags))

def generate_substitutions(flags: List[str], alternatives: Dict[str, str]) -> Generator[List[str], None, None]:
  alternative_flags = sorted([alternative.strip() for alternative in list(alternatives.keys())])
  # Generate all possible combinations of alternative flags
  for r in range(1, len(alternative_flags)+1):
    for alternatives_list in combinations(alternative_flags, r):
      substituted_flags = flags
      for alternative_from in alternatives_list:
        if alternative_from in flags:
          alternative_to = alternatives[alternative_from]
          alternative_to = ' '.join(sorted(alternative_to.strip().split(' ')))
          subst_pos = substituted_flags.index(alternative_from)
          substituted_flags = substituted_flags[:subst_pos] + [alternative_to] + substituted_flags[subst_pos+1:]
      if substituted_flags != flags and len(substituted_flags) > 0:
        yield substituted_flags
  
def main(
  install_sh: Path, 
  prefix: str, targets_spec_file: Path,
  tsl_folder_ph: str, default_flags_ph: str,
  alt_flags_ph: str, mapping_ph: str,
  generic_fallback_ph: str
):
  with open(targets_spec_file, 'r') as f:
    data: Dict[str, Any] = json.loads(f.read())

  tsl_folders: List[str] = []
  default_flags: List[str] = []
  alternative_flags: List[str] = []
  alternative_mappings: List[str] = []
  generic_fallback: str = ''
  for architecture, specs in data.items():
    print(f"Architecture: {architecture}")
    for spec in specs:
      if architecture == 'generic' and spec['name'] == 'scalar':
        generic_fallback = f"{prefix}-{architecture}-{spec['name']}"
        continue
      folder_name: str = f"{prefix}-{architecture}-{spec['name']}"
      tsl_folders.append(f'  "{folder_name}"')
      flags_list: List[str] = flags_str_to_list(spec['flags'])
      default_flags.append(f'  "{list_to_str(flags_list)}" #{folder_name}')
      if 'alternatives' in spec:
        for current_alternative_flags in generate_substitutions(flags_list, spec['alternatives']):
          alternative_flags.append(f'  "{list_to_str(current_alternative_flags)}" #{folder_name}')
          alternative_mappings.append(f'  "{folder_name}"')
  
  with open(install_sh, 'r') as f:
    install_sh_content = f.read()
  install_sh_content = install_sh_content.replace(tsl_folder_ph, '\n'.join(tsl_folders))
  install_sh_content = install_sh_content.replace(default_flags_ph, '\n'.join(default_flags))
  install_sh_content = install_sh_content.replace(alt_flags_ph, '\n'.join(alternative_flags))
  install_sh_content = install_sh_content.replace(mapping_ph, '\n'.join(alternative_mappings))
  install_sh_content = install_sh_content.replace(generic_fallback_ph, f'"{generic_fallback}"')
  with open(install_sh, 'w') as f:
    f.write(install_sh_content)

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='...')
  parser.add_argument('--install-sh', help="Path to install.sh", required=True, type=Path, dest='install_sh')
  parser.add_argument('--folder-prefix', help='Prefix that was used as prefix for tsl folders', required=False, type=str, dest='prefix', default='tsl')
  parser.add_argument('--targets-spec-file', help='Path to targets specs json file', required=True, type=Path, dest='specs_file')
  parser.add_argument('--tsl-folder-ph', help='Name of placeholder for tsl folders array in install.sh', required=True, type=str, dest='tsl_folder_ph')
  parser.add_argument('--default-flags-array-ph', help='Name of placeholder for default flags array values', required=True, type=str, dest='default_flags_ph')
  parser.add_argument('--alt-flags-array-ph', help='Name of placeholder for alternative flags array values', required=True, type=str, dest='alt_flags_ph')
  parser.add_argument('--alt-to-tsl-mapping-ph', help='Name of placeholder for alternative to tsl-folder mapping values', required=True, type=str, dest='mapping_ph')
  parser.add_argument('--generic-fallback-ph', help='Name of placeholder for generic fallback value', required=True, type=str, dest='generic_fallback_ph')
  args = parser.parse_args()
  main(args.install_sh, args.prefix, args.specs_file,
       args.tsl_folder_ph, args.default_flags_ph,
       args.alt_flags_ph, args.mapping_ph,
       args.generic_fallback_ph)