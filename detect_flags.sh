#!/bin/bash

function parse_flags {
    compiler=$1
    compilerinfo=$2

    if [ $compiler = "clang" ]; then
        regex='"-target-feature" "\+([^\"]+)"'
        if [[ $compilerinfo =~ $regex ]] ; then
            flag="${BASH_REMATCH[1]}"
            printf "$flag "
            # Remove the first regex match and parse recursively
            parse_flags "$compiler" "${compilerinfo/${BASH_REMATCH[0]}/}"
        fi
    elif [ $compiler = "gcc" ]; then
        # regex=' -m((?!no-)[^\s]+)'
        regex=' -m([^ ]+)'
        if [[ $compilerinfo =~ $regex ]] ; then
            flag="${BASH_REMATCH[1]}"
            # only print flags that do not start with "no-", since g++ explicitly emits unsupported flags this way.
            if [[ $flag != no-* ]]; then
                printf "$flag "
            fi
            # Remove the first regex match and parse recursively
            parse_flags "$compiler" "${compilerinfo/${BASH_REMATCH[0]}/}"
        fi
    else
        echo "Unknown compiler."
        exit -1
    fi
}

gcc_exe="/usr/bin/g++"
clang_exe="/usr/bin/clang"

flag_set=()

if [[ -f $gcc_exe && -x $gcc_exe ]]; then
    gcc_output=$(/usr/bin/g++ -E - -march=native -### 2>&1)
    parsed_flags=$(parse_flags "gcc" "$gcc_output")

    # Parse whitespace-separated string into an array
    IFS=' ' read -r -a parsed_array <<< "$parsed_flags"
    unset IFS

    # Check for every flag if it is already contained in the flag array
    for flag in "${parsed_array[@]}"
    do
        if [[ ! " ${flag_set[*]} " =~ [[:space:]]${flag}[[:space:]] ]]; then
            flag_set+=("$flag")
        fi
    done
fi

if [[ -f $clang_exe && -x $clang_exe ]]; then
    if [[ "$OSTYPE" == "linux-gnu"* ]] && [[ $(uname -i) != aarch*  ]]; then
        arch_string="-march=native"
    elif [[ "$OSTYPE" == "linux-gnu"* ]] && [[ $(uname -i) == aarch*  ]]; then
        arch_string="-mcpu=native"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        arch_string="-march=native"
    elif [[ "$OSTYPE" == "cygwin" ]]; then
        # POSIX compatibility layer and Linux environment emulation for Windows
        continue
    elif [[ "$OSTYPE" == "msys" ]]; then
        # Lightweight shell and GNU utilities compiled for Windows (part of MinGW)
        continue
    else
        echo "Could not detect the current operating system. Aborting."
        exit 1
    fi
    
    clang_output=$(/usr/bin/clang -E - $arch_string -### 2>&1)
    parsed_flags=$(parse_flags "clang" "$clang_output")

    # Parse whitespace-separated string into an array
    IFS=' ' read -r -a parsed_array <<< "$parsed_flags"
    unset IFS

    # Check for every flag if it is already contained in the flag array
    for flag in "${parsed_array[@]}"
    do
        if [[ ! " ${flag_set[*]} " =~ [[:space:]]${flag}[[:space:]] ]]; then
            flag_set+=("$flag")
        fi
    done
fi

IFS=$'\n' sorted=($(sort <<<"${flag_set[*]}"))
unset IFS
printf "%s " "${sorted[@]}"
printf "\n"
