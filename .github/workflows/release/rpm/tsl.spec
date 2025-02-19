Name:           libtsl-dev
Version:        $<< VERSION_TAG >>
Release:        $<< RELEASE_TAG >>
Summary:        Template SIMD Library (TSL) is an open-source C++ library for SIMD programming. It provides a comprehensive collection of SIMD intrinsics and high-level interfaces to exploit the full power of SIMD hardware.
BuildArch:      noarch

License:        Apache License, Version 2.0
URL:            https://github.com/db-tu-dresden/TSL
Source0:        tsl.tar.gz
Source1:        detect_flags.sh
Source2:        select_flavor.sh

Requires:       util-linux tar gzip which

%global install_dir %{_includedir}/tsl
%global tmp_dir %{_tmppath}/tsl

%description
Header-only library TSL (Template SIMD Library) provides a comprehensive collection of SIMD intrinsics and high-level interfaces to exploit the full power of SIMD hardware. It is designed to be used in a wide range of applications, such as image processing, computer graphics, computer vision, machine learning, and scientific computing.

%install
mkdir -p %{buildroot}%{install_dir}
mkdir -p %{buildroot}%{tmp_dir}
ls -l %{buildroot}%{tmp_dir}
install -m 755 %{SOURCE2} %{buildroot}%{tmp_dir}/select_flavor.sh
install -m 755 %{SOURCE1} %{buildroot}%{tmp_dir}/detect_flags.sh
install -m 644 %{SOURCE0} %{buildroot}%{tmp_dir}/tsl.tar.gz

%files
%dir %{install_dir}
%dir %{tmp_dir}
%{tmp_dir}/select_flavor.sh
%{tmp_dir}/detect_flags.sh
%{tmp_dir}/tsl.tar.gz

%post
echo "Detecting the best TSL flavor for your system..." > /dev/console
%{tmp_dir}/select_flavor.sh %{tmp_dir} --log > /dev/console
CHOSEN_TSL_PATH=$(%{tmp_dir}/select_flavor.sh %{tmp_dir})
if [ -z "${CHOSEN_TSL_PATH}" ]; then
  echo "Error: No valid TSL flavor detected." > /dev/console
  exit 1
fi
echo "Chosen TSL flavor: ${CHOSEN_TSL_PATH}" > /dev/console
rm -rf %{install_dir}/*
tar -xf %{tmp_dir}/tsl.tar.gz -C %{install_dir} ${CHOSEN_TSL_PATH} --strip-components=1

rm -rf %{tmp_dir}
echo "TSL has been installed successfully."

%postun
rm -rf %{install_dir}
echo "TSL has been removed successfully."