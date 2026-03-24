import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Output as standalone for Docker — bundles everything needed to run
  // into a self-contained directory (no node_modules needed at runtime).
  // This makes the Docker image much smaller.
  output: "standalone",
};

export default nextConfig;
