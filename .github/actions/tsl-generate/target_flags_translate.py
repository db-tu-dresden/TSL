#!/usr/bin/env python3

import sys

def get_variants(arr):
  if len(arr) == 1:
    for x in arr[0]:
      yield [x]
  else:
    for x in arr[0]:
      for y in get_variants(arr[1:]):
        yield [x] + y

def flatten_alternatives(arr):
  for entry in arr:
    for x in entry.split("|"):
      yield x

targets_str = sys.argv[1]
targets_arr = [x.strip() for x in targets_str.split(",")]

direct_targets = list(filter(lambda x: "|" not in x, targets_arr))
alternatives_targets = list(filter(lambda x: "|" in x, targets_arr))

targets_all = direct_targets + [x for x in flatten_alternatives(alternatives_targets)]
targets_name = "-".join(targets_all)

if len(alternatives_targets) > 0:
  alternatives = [x for x in get_variants([alt.split("|") for alt in alternatives_targets])]
else:
  alternatives = []
	
if len(sys.argv) == 3:
  print(targets_name)
else:
  if len(alternatives) > 0:
    for alternative in alternatives:
      print(f"flags: {':'.join(direct_targets + alternative)}")
      print(f"path: {targets_name}")
  else:
    print(f"flags: {':'.join(direct_targets)}")
    print(f"path: {targets_name}")
