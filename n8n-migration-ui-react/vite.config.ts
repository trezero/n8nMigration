import path from "path";
import { fileURLToPath } from 'url';
import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  server: {
    port: 5173, // Default port for the dev server
    open: true, // Automatically open in browser on dev start
  },
  build: {
    outDir: 'dist',
    sourcemap: true, // Generate source maps for production build
  },
  // Vitest configuration - needs to be at top level of defineConfig, not inside build
  // test: { 
  //   globals: true,
  //   environment: 'jsdom',
  //   setupFiles: './src/setupTests.ts', // if you have a setup file for tests
  //   coverage: {
  //     provider: 'v8', // or 'istanbul'
  //     reporter: ['text', 'json', 'html'],
  //   },
  // },
});

// Separate Vitest config (or use inline in defineConfig if preferred by your Vite version)
// For Vitest specific config, often it's in vitest.config.ts or within defineConfig as 'test'
// Example of 'test' block for Vitest if you prefer it inside vite.config.ts:
/*
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  server: {
    port: 3000,
    open: true,
  },
  build: {
    outDir: 'dist',
    sourcemap: true,
  },
  test: {
    globals: true,
    environment: 'jsdom',
    // setupFiles: './src/setupTests.ts', // Uncomment if you create this file
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
    },
  },
});
*/
