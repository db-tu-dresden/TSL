class LibtslDev < Formula
  desc "Template SIMD Library (TSL) for SIMD programming"
  homepage "https://github.com/db-tu-dresden/TSL"
  url "file:///tsl/brew/libtsl-dev.tar.gz"
  sha256 "$<< SHA256 >>"
  version "$<< VERSION_TAG >>"
  license "Apache-2.0"

  def install
    bin.install "select_flavor.sh"
    bin.install "detect_flags.sh"
    lib.install "tsl.tar.gz"
  end

  test do
    system "#{bin}/select_flavor.sh", "--help"
  end
end
