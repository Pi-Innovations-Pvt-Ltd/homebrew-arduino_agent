class Agent < Formula
  desc "Arduino upload agent with Arduino CLI"
  homepage "https://github.com/biseshadhikari/arduino-agent"
  url "https://github.com/biseshadhikari/arduino-agent/releases/download/v1.0.1/agent-1.0.0.tar.gz"
  sha256 "YOUR_REAL_SHA256_HASH"
  license "MIT"

  def install
    bin.install "agent"
  end

  test do
    system "#{bin}/agent", "--version"
  end
end
