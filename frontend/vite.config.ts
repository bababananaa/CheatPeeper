// Vite is the tool that runs our dev server (`npm run dev`) and builds the
// production files (`npm run build`). This file tells it which plugins to use.
//
// We import defineConfig from "vitest/config" (instead of "vite") so the same
// file can also hold our test settings in the `test` section below.
import tailwindcss from '@tailwindcss/vite'
import react from '@vitejs/plugin-react'
import { defineConfig } from 'vitest/config'

export default defineConfig({
  plugins: [
    react(), // lets Vite understand React/JSX files (.tsx)
    tailwindcss(), // turns Tailwind class names (e.g. "rounded-xl") into real CSS
  ],

  test: {
    // Tests run in Node, which has no browser. "jsdom" fakes one so we can
    // render components and click on them in tests.
    environment: 'jsdom',
    // Runs before every test file (adds helpers like toBeInTheDocument()).
    setupFiles: ['./src/test/setup.ts'],
  },
})
