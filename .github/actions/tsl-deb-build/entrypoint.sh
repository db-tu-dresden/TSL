#!/bin/bash -l

VERSION_ORIG=$1 #v0.0.1
#remove prefix "v" from VERSION_ORIG
VERSION=${VERSION_ORIG#v}
TSL_TAR_GZ_NAME=$2 #tsl.tar.gz
TSL_TAR_PREFIX=$3 #tsl/generate_tsl_

BUILD_ROOT=/root/debbuild/tsl
DEB_BASE=${BUILD_ROOT}/DEBIAN
INSTALL_BASE=/usr/include/tsl/__hollistic
POSTINSTALL_BASE=/usr/include/tsl
SOURCE_BASE=${BUILD_ROOT}${INSTALL_BASE}


CONTROL_FILE=${DEB_BASE}/control
POSTINST_FILE=${DEB_BASE}/postinst
POSTRM_FILE=${DEB_BASE}/postrm

# sed ${{ VERSION_TAG }} in tsl.spec with $VERSION
sed -i "s/\${{ VERSION_TAG }}/${VERSION}/g" ${CONTROL_FILE}

sed -i "s|\${{ INSTALL_BASE }}|${INSTALL_BASE}|g" ${POSTINST_FILE}
sed -i "s/\${{ TSL_TARBALL }}/${TSL_TAR_GZ_NAME}/g" ${POSTINST_FILE}
sed -i "s|\${{ TSL_TARBALL_PREFIX }}|${TSL_TAR_PREFIX}|g" ${POSTINST_FILE}
sed -i "s|\${{ POSTINSTALL_BASE }}|${POSTINSTALL_BASE}|g" ${POSTINST_FILE}
sed -i "s|\${{ POSTINSTALL_BASE }}|${POSTINSTALL_BASE}|g" ${POSTRM_FILE}

chmod +x ${POSTINST_FILE}

REPO_ROOT=/github/workspace
TSL_ROOT=${REPO_ROOT}/${TSL_TAR_GZ_NAME}
OUT_BASE=packages/deb
OUT=${REPO_ROOT}/${OUT_BASE}
mkdir -p ${OUT}
echo "out=${OUT_BASE}" >> $GITHUB_OUTPUT

cp ${CONTROL_FILE} ${OUT}
cp ${POSTINST_FILE} ${OUT}
cp ${POSTRM_FILE} ${OUT}

cp ${TSL_ROOT} ${SOURCE_BASE}/
tar -xf ${SOURCE_BASE}/${TSL_TAR_GZ_NAME} -C ${SOURCE_BASE}/ tsl/tsl.conf

dpkg-deb --root-owner-group --build ${BUILD_ROOT} ${OUT}

if [ $? -ne 0 ]; then
  echo "msg=dpkg-deb failed" >> $GITHUB_OUTPUT
  echo "success=false" >> $GITHUB_OUTPUT
  exit
fi


mv ${OUT}/libtsl-dev_${VERSION}_all.deb ${OUT}/libtsl-dev.deb
# try to install and remove
apt install ${OUT}/libtsl-dev.deb -y
apt remove libtsl-dev -y

if [ $? -ne 0 ]; then
  echo "msg=deb install failed" >> $GITHUB_OUTPUT
  echo "success=false" >> $GITHUB_OUTPUT
  exit
fi

echo "name=libtsl-dev.deb" >> $GITHUB_OUTPUT



echo "msg=dpkb-deb success" >> $GITHUB_OUTPUT
echo "success=true" >> $GITHUB_OUTPUT