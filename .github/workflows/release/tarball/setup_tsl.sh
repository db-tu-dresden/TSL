#!/bin/bash

print_help() {
  echo "Usage: tsl_install.sh [options]"
  echo "Install the libtsl library in the specified path."
  echo "If no option is provided, the library will be installed in the current directory."
  echo ""
  echo "Options:"
  echo "  --local [path]   Install the library in the specified path (default: current directory)"
  echo "  --system [path]  Install the library in the specified system path (default: /usr/include)"
  echo "  --help           Print this help message"
  exit 0
}

if [[ "$#" -eq 0 ]]; then
  out_path=$(pwd)
else
  # Parse arguments
  while [ "$#" -gt 0 ]; do
    case "$1" in
      --local)
        if [[ -z "$2" ]]; then
          out_path=$(pwd)
          shift 1
        else
          out_path="$2"
          shift 2
        fi
        ;;
      --system)
        if [[ -z "$2" ]]; then
          out_path="/usr/include"
          shift 1
        else
          out_path="$2"
          shift 2
        fi
        ;;
      --help)
        print_help
        ;;
      *)
        echo "Unknown option: $1"
        exit 1
        ;;
    esac
  done
fi

out_path="${out_path}/tsl"
echo "Installing TSL to ${out_path}"
mkdir -p "${out_path}"

tmp_dir=$(mktemp -ud /tmp/libtsl-dev-XXXXXX)
mkdir -p "${tmp_dir}"

curl -L "https://github.com/db-tu-dresden/TSL/releases/latest/download/libtsl-dev.tar.gz" -o ${tmp_dir}/libtsl-dev.tar.gz
tar -xzf "${tmp_dir}/libtsl-dev.tar.gz" -C "${tmp_dir}"
chmod 755 "${tmp_dir}"/*.sh
supported_path=$("${tmp_dir}"/select_flavor.sh "${tmp_dir}")

echo "Underlying hardware: ${supported_path}"
tar -xzf "${tmp_dir}/tsl.tar.gz" -C "${tmp_dir}" "${supported_path}"
mv "${tmp_dir}/${supported_path}"/* "${out_path}"

rm -rf "${tmp_dir}"

