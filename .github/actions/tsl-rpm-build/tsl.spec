Name:           libtsl-dev
Version:        ${{ VERSION_TAG }}
Release:        ${{ RELEASE_TAG }}
Summary:        Template SIMD Library (TSL) is an open-source C++ library for SIMD programming. It provides a comprehensive collection of SIMD intrinsics and high-level interfaces to exploit the full power of SIMD hardware.
BuildArch:      noarch

License:        Apache License, Version 2.0
URL:            https://github.com/db-tu-dresden/TSL
Source0:        ${{ TSL_TARBALL }}

Requires:       util-linux tar gzip grep sed

%global include_dir /usr/include
%global tsl_dir_name tsl
%global tsl_dir %{include_dir}/%{tsl_dir_name}
%global tsl_hollistic_name __hollistic
%global tsl_hollistic_dir %{tsl_dir}/%{tsl_hollistic_name}

%description

%post
LSCPU_FLAGS_STRING=$(LANG=en;lscpu | grep 'Flags:' | sed -E 's/Flags:\s*//g' | sed -E 's/\s/:/g')
AVAIL_FLAGS=(${LSCPU_FLAGS_STRING//:/ })
MAX_AVAIL_FLAGS=0
CHOSEN_TSL_PATH=""
UNKNOWN_PATH="unknown"
while read -r line1 && read -r line2; do
  #remove prefix "flags: " from line1
  TSL_FLAGS_STR=${line1#flags: }
  #create array from flags string
  TSL_FLAGS_ARR=(${TSL_FLAGS_STR//:/ })
  #remove prefix "path: " from line1
  TSL_PATH=${line2#path: }

  #if TSL_FLAGS_STR equals "UNKNOWN" then set TSL_FLAGS_ARR to "UNKNOWN"
  if [ "$TSL_FLAGS_STR" == "$UNKNOWN_PATH" ]; then
    UNKNOWN_PATH=$TSL_PATH
  fi
  COUNTER=0
  FOUND_ALL_FLAGS=1
  for i in "${!TSL_FLAGS_ARR[@]}"
  do
    FOUND_FLAG=0
    for j in "${!AVAIL_FLAGS[@]}"
    do
      if [ "${TSL_FLAGS_ARR[i]}" == "${AVAIL_FLAGS[j]}" ]; then
        FOUND_FLAG=1
        COUNTER=$((COUNTER+1))
      fi
    done
    if [ $FOUND_FLAG -eq 0 ]; then
      FOUND_ALL_FLAGS=0
      break
    fi
  done
  if [ $COUNTER -gt $MAX_AVAIL_FLAGS ] && [ $FOUND_ALL_FLAGS -eq 1 ]; then
    MAX_AVAIL_FLAGS=$COUNTER
    CHOSEN_TSL_PATH=${TSL_PATH}
  fi
done < %{tsl_hollistic_dir}/tsl/tsl.conf
if [ "$MAX_AVAIL_FLAGS" -eq "0" ]; then
  echo "No suitable extension found on this CPU. Falling back to scalar."
  CHOSEN_TSL_PATH=$UNKNOWN_PATH
fi

TMP=$(mktemp -ud %{_tmppath}/%{name}-XXXXXX)
mkdir -p ${TMP}
tar -xf %{tsl_hollistic_dir}/${{ TSL_TARBALL }} -C ${TMP} ${{ TSL_TARBALL_PREFIX }}${CHOSEN_TSL_PATH}
cp -r ${TMP}/${{ TSL_TARBALL_PREFIX }}${CHOSEN_TSL_PATH}/include %{tsl_dir}
if [ -d "${TMP}/${{ TSL_TARBALL_PREFIX }}${CHOSEN_TSL_PATH}/supplementary" ]; then
  cp -r ${TMP}/${{ TSL_TARBALL_PREFIX }}${CHOSEN_TSL_PATH}/supplementary %{tsl_dir}
fi
cp ${TMP}/${{ TSL_TARBALL_PREFIX }}${CHOSEN_TSL_PATH}/tsl.hpp %{tsl_dir}


%postun
rm -rf %{tsl_dir}

%install
rm -rf %{buildroot}/*
umask 0022
mkdir -p %{buildroot}%{tsl_hollistic_dir}
cp -a /root/rpmbuild/SOURCES/${{ TSL_TARBALL }} %{buildroot}%{tsl_hollistic_dir}/
tar -xf %{buildroot}%{tsl_hollistic_dir}/${{ TSL_TARBALL }} -C %{buildroot}%{tsl_hollistic_dir} tsl/tsl.conf

%clean


%files
%{tsl_hollistic_dir}
