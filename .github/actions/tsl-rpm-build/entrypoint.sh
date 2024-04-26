#!/bin/sh -l

VERSION_ORIG=$1 #v0.0.1
#remove prefix "v" from VERSION_ORIG
VERSION=${VERSION_ORIG#v}
TSL_TAR_GZ_NAME=$2 #tsl.tar.gz
TSL_TAR_PREFIX=$3 #tsl/generate_tsl_

RPM_BASE=/root/rpmbuild
SPEC_FILE=${RPM_BASE}/SPECS/tsl.spec


REPO_ROOT=/github/workspace
TSL_ROOT=${REPO_ROOT}/${TSL_TAR_GZ_NAME}
OUT_BASE=packages/rpm
OUT=${REPO_ROOT}/${OUT_BASE}
mkdir -p ${OUT}
echo "out=${OUT_BASE}" >> $GITHUB_OUTPUT

RPM_FILE="${OUT}/noarch/libtsl-dev-${VERSION}-1.noarch.rpm"

# sed ${{ VERSION_TAG }} in tsl.spec with $VERSION
if [[ "$VERSION" == *"-"* ]]; then
  #release candidate
  VER=${VERSION%%-*}
  RC=${VERSION##*-}
  sed -i "s/\${{ VERSION_TAG }}/${VER}/g" ${SPEC_FILE}
  sed -i "s/\${{ RELEASE_TAG }}/${RC}/g" ${SPEC_FILE}
  RMP_FILE="${OUT}/noarch/libtsl-dev-${VER}-${RC}.noarch.rpm"
else
  sed -i "s/\${{ VERSION_TAG }}/${VERSION}/g" ${SPEC_FILE}
  sed -i "s/\${{ RELEASE_TAG }}/1/g" ${SPEC_FILE}
fi

sed -i "s/\${{ TSL_TARBALL }}/${TSL_TAR_GZ_NAME}/g" ${SPEC_FILE}
sed -i "s|\${{ TSL_TARBALL_PREFIX }}|${TSL_TAR_PREFIX}|g" ${SPEC_FILE}



cp ${SPEC_FILE} ${OUT}

cp ${TSL_ROOT} ${RPM_BASE}/SOURCES/${TSL_TAR_GZ_NAME}

rpmbuild -bb ${SPEC_FILE} --buildroot ${RPM_BASE}/BUILDROOT --define "_rpmdir ${OUT}"

if [ $? -ne 0 ]; then
  echo "msg=rpmbuild failed" >> $GITHUB_OUTPUT
  echo "success=false" >> $GITHUB_OUTPUT
  exit
fi

mv ${RPM_FILE} ${OUT}/libtsl-dev.rpm
# try to install and remove
dnf install ${OUT}/libtsl-dev.rpm -y
dnf remove libtsl-dev -y

if [ $? -ne 0 ]; then
  echo "msg=rpmbuild failed" >> $GITHUB_OUTPUT
  echo "success=false" >> $GITHUB_OUTPUT
  exit
fi

echo "name=libtsl-dev.rpm" >> $GITHUB_OUTPUT

ls -l ${OUT} >> ${OUT}/ls.txt

echo "msg=rpmbuild success" >> $GITHUB_OUTPUT
echo "success=true" >> $GITHUB_OUTPUT
