#!/bin/bash
#set -x
ALL_TARGET_FLAGS=("sse" "sse;sse2" "sse;sse2;ssse3" "sse;sse2;ssse3;sse4_1" "sse;sse2;ssse3;sse4_1;sse4_2" "sse;sse2;ssse3;sse4_1;sse4_2;avx" "sse;sse2;ssse3;sse4_1;sse4_2;avx;avx2" "sse;sse2;ssse3;sse4_1;sse4_2;avx;avx2;avx512f" "sse;sse2;ssse3;sse4_1;sse4_2;avx;avx2;avx512f;avx512cd;avx512er;avx512pf" "sse;sse2;ssse3;sse4_1;sse4_2;avx;avx2;avx512f;avx512cd;avx512bw;avx512dq;avx512vl")

for CURRENT_TARGET_FLAGS in ${ALL_TARGET_FLAGS[@]}; do
   echo "Testing target flags: ${CURRENT_TARGET_FLAGS}"
   IFS=";" read -ra TARGET_FLAGS <<< "${CURRENT_TARGET_FLAGS}"
   cmake -S . -B build -DTARGETS_FLAGS="${CURRENT_TARGET_FLAGS}"
   make -j -C build > "./build_${CURRENT_TARGET_FLAGS}.log" 2>&1
done
