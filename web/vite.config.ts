import react from "@vitejs/plugin-react";
import { defineConfig } from "vitest/config";

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: { "/api": "http://localhost:8080" },
  },
  build: {
    outDir: "dist",
    rollupOptions: {
      output: {
        // Split the heavy chart/React vendors into a cached chunk so the main
        // bundle is small and repeat loads hit cache.
        manualChunks: {
          react: ["react", "react-dom"],
          charts: ["recharts"],
        },
      },
    },
  },
  test: {
    globals: true,
    environment: "jsdom",
    setupFiles: "./vitest.setup.ts",
    coverage: {
      provider: "v8",
      include: ["src/**/*.{ts,tsx}"],
      exclude: [
        "src/main.tsx",
        "src/**/*.test.tsx",
        "src/testUtils.tsx",
        "src/types.ts",
        "src/hooks/**",
      ],
      thresholds: { lines: 75, functions: 75, branches: 70, statements: 75 },
    },
  },
});
