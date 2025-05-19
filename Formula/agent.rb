class Agent < Formula
  desc "Arduino upload agent with Arduino CLI"
  homepage "https://github.com/Pi-Innovations-Pvt-Ltd/homebrew-arduino_agent"
  
  # Updated URL to match release repo name and tag
  url "https://github.com/Pi-Innovations-Pvt-Ltd/homebrew-arduino_agent/releases/download/v1.0.0/agent-1.0.0.tar.gz"
  
  # Replace with the actual SHA256 hash of the renamed tarball agent-1.0.1.tar.gz
  sha256 "cb9c3ef028c06a8fcbf16a24d49d5302969b3118090bd1e971dfdf85b7ba74e3"
  
  license "MIT"

  def install
    bin.install "agent"
  end

  test do
    system "#{bin}/agent", "--version"
  end
end
